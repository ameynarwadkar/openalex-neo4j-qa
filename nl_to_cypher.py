import os
import re
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import AzureOpenAI

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not NEO4J_PASSWORD:
    raise ValueError("Missing NEO4J_PASSWORD in .env")

if not AZURE_OPENAI_API_KEY:
    raise ValueError("Missing AZURE_OPENAI_API_KEY in .env")

if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("Missing AZURE_OPENAI_ENDPOINT in .env")

if not AZURE_OPENAI_DEPLOYMENT:
    raise ValueError("Missing AZURE_OPENAI_DEPLOYMENT in .env")


neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)


GRAPH_SCHEMA = """
You are generating Cypher for a Neo4j property graph.

Node labels and properties:

1. Paper
   - id
   - title
   - doi
   - year

2. Author
   - id
   - name

3. Institution
   - id
   - name
   - country

4. Concept
   - id
   - name
   - level

5. Venue
   - id
   - name
   - type

Relationships:

1. (:Author)-[:AUTHORED]->(:Paper)

2. (:Author)-[:AFFILIATED_WITH]->(:Institution)

3. (:Paper)-[:HAS_CONCEPT {score}]->(:Concept)

4. (:Paper)-[:PUBLISHED_IN]->(:Venue)

5. (:Paper)-[:CITES]->(:Paper)

6. (:Author)-[:WORKS_ON {
      source,
      evidence_count,
      evidence_papers
   }]->(:Concept)

7. (:Author)-[:COLLABORATED_WITH {
      source,
      joint_papers,
      evidence_papers
   }]->(:Author)

8. (:Concept)-[:RELATED_TO {
      source,
      cooccurrence_count,
      evidence_papers
   }]->(:Concept)
"""


SYSTEM_PROMPT = f"""
You translate natural language questions into Neo4j Cypher.

Use only this graph schema:

{GRAPH_SCHEMA}

Rules:
- Return only Cypher.
- Do not explain.
- Do not wrap the query in markdown.
- Generate only read-only queries.
- Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP, LOAD CSV, APOC, or dbms procedures.
- Use MATCH, OPTIONAL MATCH, WITH, WHERE, RETURN, ORDER BY, and LIMIT only.
- Always include LIMIT 20 unless the query is clearly asking for a count.
- Prefer DISTINCT where duplicate rows are likely.
- Use toLower(x) CONTAINS "keyword" for text matching.
- For author expertise questions, prefer the derived WORKS_ON relationship.
- For explanation questions, show evidence_papers or explicit Author -> Paper -> Concept paths.
- Never use `_` as a wildcard or placeholder in property maps (e.g., avoid `{{score: _}}`). If a property value is unknown, just omit the property entirely from the match pattern.
"""


FORBIDDEN_PATTERNS = [
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bDELETE\b",
    r"\bSET\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bLOAD\s+CSV\b",
    r"\bCALL\b",
    r"\bAPOC\b",
    r"\bDBMS\b",
    r"\bDETACH\b",
]


def clean_cypher(cypher):
    cypher = cypher.strip()
    cypher = cypher.replace("```cypher", "")
    cypher = cypher.replace("```", "")
    return cypher.strip()


def validate_cypher(cypher):
    upper = cypher.upper()

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, upper):
            raise ValueError(f"Unsafe Cypher blocked. Forbidden pattern: {pattern}")

    allowed_start = (
        "MATCH",
        "OPTIONAL MATCH",
        "WITH",
    )

    if not upper.startswith(allowed_start):
        raise ValueError(
            "Unsafe Cypher blocked. Query must start with MATCH, OPTIONAL MATCH, or WITH."
        )

    if not re.search(r"\bRETURN\b", upper):
        raise ValueError("Invalid Cypher blocked. Query must contain RETURN.")

    return True


def generate_cypher(question):
    completion = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0,
    )

    cypher = completion.choices[0].message.content
    cypher = clean_cypher(cypher)
    validate_cypher(cypher)

    return cypher


def run_cypher(cypher):
    with neo4j_driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]


def print_rows(rows):
    if not rows:
        print("\nNo results found.")
        return

    print("\nResults:")
    for i, row in enumerate(rows, start=1):
        print(f"\n[{i}]")
        for key, value in row.items():
            print(f"{key}: {value}")


def main():
    print("\nOpenAlex Neo4j Natural Language QA using Azure OpenAI")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask > ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        try:
            cypher = generate_cypher(question)

            print("\nGenerated Cypher:")
            print(cypher)

            rows = run_cypher(cypher)
            print_rows(rows)

        except Exception as e:
            print("\nError:")
            print(e)

    neo4j_driver.close()


if __name__ == "__main__":
    main()