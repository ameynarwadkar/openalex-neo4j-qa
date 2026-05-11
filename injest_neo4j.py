import json
import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase
from tqdm import tqdm

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

INPUT_FILE = "openalex_works.json"


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def create_constraints(tx):
    tx.run("""
    CREATE CONSTRAINT paper_id IF NOT EXISTS
    FOR (p:Paper)
    REQUIRE p.id IS UNIQUE
    """)

    tx.run("""
    CREATE CONSTRAINT author_id IF NOT EXISTS
    FOR (a:Author)
    REQUIRE a.id IS UNIQUE
    """)

    tx.run("""
    CREATE CONSTRAINT institution_id IF NOT EXISTS
    FOR (i:Institution)
    REQUIRE i.id IS UNIQUE
    """)

    tx.run("""
    CREATE CONSTRAINT concept_id IF NOT EXISTS
    FOR (c:Concept)
    REQUIRE c.id IS UNIQUE
    """)

    tx.run("""
    CREATE CONSTRAINT venue_id IF NOT EXISTS
    FOR (v:Venue)
    REQUIRE v.id IS UNIQUE
    """)


def ingest_paper(tx, work):
    paper_id = work.get("id")
    if not paper_id:
        return

    title = work.get("title")
    doi = work.get("doi")
    year = work.get("publication_year")

    tx.run("""
    MERGE (p:Paper {id: $paper_id})
    SET p.title = $title,
        p.doi = $doi,
        p.year = $year
    """, {
        "paper_id": paper_id,
        "title": title,
        "doi": doi,
        "year": year
    })

    # Venue
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}

    venue_id = source.get("id")
    if venue_id:
        tx.run("""
        MERGE (v:Venue {id: $venue_id})
        SET v.name = $venue_name,
            v.type = $venue_type

        WITH v
        MATCH (p:Paper {id: $paper_id})
        MERGE (p)-[:PUBLISHED_IN]->(v)
        """, {
            "venue_id": venue_id,
            "venue_name": source.get("display_name"),
            "venue_type": source.get("type"),
            "paper_id": paper_id
        })

    # Authors and institutions
    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        author_id = author.get("id")

        if not author_id:
            continue

        tx.run("""
        MERGE (a:Author {id: $author_id})
        SET a.name = $author_name

        WITH a
        MATCH (p:Paper {id: $paper_id})
        MERGE (a)-[:AUTHORED]->(p)
        """, {
            "author_id": author_id,
            "author_name": author.get("display_name"),
            "paper_id": paper_id
        })

        for inst in authorship.get("institutions", []):
            inst_id = inst.get("id")

            if not inst_id:
                continue

            tx.run("""
            MERGE (i:Institution {id: $inst_id})
            SET i.name = $inst_name,
                i.country = $country

            WITH i
            MATCH (a:Author {id: $author_id})
            MERGE (a)-[:AFFILIATED_WITH]->(i)
            """, {
                "inst_id": inst_id,
                "inst_name": inst.get("display_name"),
                "country": inst.get("country_code"),
                "author_id": author_id
            })

    # Concepts
    for concept in work.get("concepts", []):
        concept_id = concept.get("id")

        if not concept_id:
            continue

        score = concept.get("score")

        tx.run("""
        MERGE (c:Concept {id: $concept_id})
        SET c.name = $concept_name,
            c.level = $level

        WITH c
        MATCH (p:Paper {id: $paper_id})
        MERGE (p)-[r:HAS_CONCEPT]->(c)
        SET r.score = $score
        """, {
            "concept_id": concept_id,
            "concept_name": concept.get("display_name"),
            "level": concept.get("level"),
            "score": score,
            "paper_id": paper_id
        })

    # Citations
    for cited_paper_id in work.get("referenced_works", []):
        tx.run("""
        MERGE (cited:Paper {id: $cited_paper_id})

        WITH cited
        MATCH (p:Paper {id: $paper_id})
        MERGE (p)-[:CITES]->(cited)
        """, {
            "paper_id": paper_id,
            "cited_paper_id": cited_paper_id
        })


def main():
    if not NEO4J_PASSWORD:
        raise ValueError("NEO4J_PASSWORD is missing. Add it to your .env file.")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        works = json.load(f)

    print(f"Loaded {len(works)} papers from {INPUT_FILE}")

    with driver.session() as session:
        print("Creating constraints...")
        session.execute_write(create_constraints)

        print("Ingesting papers into Neo4j...")
        for work in tqdm(works):
            session.execute_write(ingest_paper, work)

    driver.close()
    print("Done. Open Neo4j Browser and check the graph.")


if __name__ == "__main__":
    main()