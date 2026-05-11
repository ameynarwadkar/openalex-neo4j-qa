
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password123"

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("RETURN 'connected' AS msg")
    print(result.single()["msg"])

driver.close()