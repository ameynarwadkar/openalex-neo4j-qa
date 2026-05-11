// =====================================================
// OpenAlex Neo4j QA Prototype — Symbolic Rule Derivation
// =====================================================


// -----------------------------------------------------
// OPTIONAL CLEANUP
// Use this if you want to regenerate derived relations
// -----------------------------------------------------
MATCH (:Author)-[r:WORKS_ON]->(:Concept)
DELETE r;


// -----------------------------------------------------
// RULE 1:
// IF Author A AUTHORED Paper P
// AND Paper P HAS_CONCEPT Concept C
// THEN Author A WORKS_ON Concept C
// -----------------------------------------------------

MATCH (a:Author)-[:AUTHORED]->(p:Paper)-[hc:HAS_CONCEPT]->(c:Concept)
WHERE hc.score >= 0.4
WITH
    a,
    c,
    count(DISTINCT p) AS evidence_count,
    collect(DISTINCT p.title)[0..5] AS evidence_papers
MERGE (a)-[r:WORKS_ON]->(c)
SET
    r.source = "rule_author_authored_paper_with_concept",
    r.evidence_count = evidence_count,
    r.evidence_papers = evidence_papers;


// -----------------------------------------------------
// RULE 2:
// IF Author A AUTHORED Paper P
// AND Author B AUTHORED Paper P
// THEN Author A COLLABORATED_WITH Author B
// -----------------------------------------------------

MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
WHERE a1.id < a2.id
WITH
    a1,
    a2,
    count(DISTINCT p) AS joint_papers,
    collect(DISTINCT p.title)[0..5] AS evidence_papers
MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
SET
    r.source = "rule_coauthored_same_paper",
    r.joint_papers = joint_papers,
    r.evidence_papers = evidence_papers;


// -----------------------------------------------------
// RULE 3:
// IF Paper P HAS_CONCEPT Concept C1
// AND Paper P HAS_CONCEPT Concept C2
// THEN Concept C1 RELATED_TO Concept C2
// -----------------------------------------------------

MATCH (c1:Concept)<-[:HAS_CONCEPT]-(p:Paper)-[:HAS_CONCEPT]->(c2:Concept)
WHERE c1.id < c2.id
WITH
    c1,
    c2,
    count(DISTINCT p) AS cooccurrence_count,
    collect(DISTINCT p.title)[0..5] AS evidence_papers
WHERE cooccurrence_count >= 2
MERGE (c1)-[r:RELATED_TO]->(c2)
SET
    r.source = "rule_concepts_cooccur_in_papers",
    r.cooccurrence_count = cooccurrence_count,
    r.evidence_papers = evidence_papers;


// -----------------------------------------------------
// CHECK DERIVED RELATIONSHIP COUNTS
// -----------------------------------------------------

MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(r) AS count
ORDER BY count DESC;