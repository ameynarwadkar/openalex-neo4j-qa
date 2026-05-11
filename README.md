# OpenAlex Neo4j NL-to-Cypher QA

A prototype natural language question-answering system built on top of a Neo4j knowledge graph using OpenAlex academic data and Azure OpenAI.

This project translates natural language questions into read-only Cypher queries, executes them against a local Neo4j database, and returns the results. It also includes symbolic rule derivation to create rich, secondary relationships (like `WORKS_ON` or `COLLABORATED_WITH`) for better reasoning and explainability.

## Features

- **Natural Language to Cypher:** Translates plain English questions into valid Neo4j Cypher queries using Azure OpenAI.
- **Symbolic Rule Derivation:** Uses Cypher to infer and create new relationships based on graph patterns, adding explainable evidence directly into the graph.
- **Built-in Security:** Validates generated Cypher to ensure only read-only queries (`MATCH`, `RETURN`, etc.) are executed, actively blocking unsafe patterns (`CREATE`, `DELETE`, `APOC`, etc.).
- **Explainable AI:** Can explain *why* an author is connected to a concept by returning the specific underlying papers as evidence.

## Prerequisites

- Python 3.8+
- Local or remote **Neo4j** database running with OpenAlex data loaded.
- **Azure OpenAI** API access.

## Setup

1. **Install dependencies:**
   Ensure you have a virtual environment set up, then install the required packages:
   ```bash
   pip install neo4j openai python-dotenv
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and configure your Neo4j and Azure OpenAI credentials:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password

   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   AZURE_OPENAI_API_VERSION=2025-04-01-preview
   ```

3. **(Optional) Run Rule Derivations:**
   To improve graph reasoning, you can run the symbolic rules in `rules.cypher` through the Neo4j Browser to generate derived relationships like `WORKS_ON` and `COLLABORATED_WITH`.

## Usage

Run the interactive QA script:

```bash
python nl_to_cypher.py
```

**Example Interaction:**
```text
OpenAlex Neo4j Natural Language QA using Azure OpenAI
Type 'exit' to quit.

Ask > Explain why an author is connected to a concept.

Generated Cypher:
MATCH (a:Author)-[w:WORKS_ON]->(c:Concept)
...
```

## Project Structure

- `nl_to_cypher.py`: The main interactive Python script handling the Azure OpenAI API calls, Cypher generation, security validation, and Neo4j database querying.
- `rules.cypher`: Cypher script containing rules to derive new, explainable relationships within the graph.
- `queries.cypher`: A collection of manual, analytical Cypher queries useful for dataset exploration and Neo4j Browser visualization.
- `screenshots/`: Contains visual documentation of the graph and system output.
