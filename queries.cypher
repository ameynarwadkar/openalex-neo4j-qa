// =====================================================
// OpenAlex Neo4j QA Prototype — Manual Cypher Queries
// =====================================================


// -----------------------------------------------------
// 1. Count all node types
// Question: How many Papers, Authors, Concepts, etc. do we have?
// -----------------------------------------------------
MATCH (n)
RETURN labels(n) AS node_type, count(n) AS count
ORDER BY count DESC;


// -----------------------------------------------------
// 2. Count all relationship types
// Question: How many AUTHORED, HAS_CONCEPT, CITES, etc. edges exist?
// -----------------------------------------------------
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(r) AS count
ORDER BY count DESC;


// -----------------------------------------------------
// 3. Top authors by number of papers
// Question: Which authors wrote the most papers in this dataset?
// -----------------------------------------------------
MATCH (a:Author)-[:AUTHORED]->(p:Paper)
RETURN a.name AS author, count(DISTINCT p) AS number_of_papers
ORDER BY number_of_papers DESC
LIMIT 10;


// -----------------------------------------------------
// 4. Top concepts by number of papers
// Question: Which concepts appear most often?
// -----------------------------------------------------
MATCH (p:Paper)-[:HAS_CONCEPT]->(c:Concept)
RETURN c.name AS concept, count(DISTINCT p) AS number_of_papers
ORDER BY number_of_papers DESC
LIMIT 15;


// -----------------------------------------------------
// 5. Papers related to knowledge graphs
// Question: Which papers are connected to Knowledge Graph-related concepts?
// -----------------------------------------------------
MATCH (p:Paper)-[:HAS_CONCEPT]->(c:Concept)
WHERE toLower(c.name) CONTAINS "knowledge graph"
RETURN DISTINCT p.title AS paper, p.year AS year, c.name AS matched_concept
ORDER BY year DESC
LIMIT 20;


// -----------------------------------------------------
// 6. Papers related to symbolic reasoning
// Question: Which papers mention symbolic reasoning / logic-related concepts?
// -----------------------------------------------------
MATCH (p:Paper)-[:HAS_CONCEPT]->(c:Concept)
WHERE toLower(c.name) CONTAINS "symbolic"
   OR toLower(c.name) CONTAINS "logic"
   OR toLower(c.name) CONTAINS "reasoning"
RETURN DISTINCT p.title AS paper, p.year AS year, c.name AS matched_concept
ORDER BY year DESC
LIMIT 20;


// -----------------------------------------------------
// 7. Most productive institutions
// Question: Which institutions appear most often through author affiliations?
// -----------------------------------------------------
MATCH (i:Institution)<-[:AFFILIATED_WITH]-(a:Author)-[:AUTHORED]->(p:Paper)
RETURN i.name AS institution,
       i.country AS country,
       count(DISTINCT p) AS number_of_papers
ORDER BY number_of_papers DESC
LIMIT 10;


// -----------------------------------------------------
// 8. Most common venues
// Question: Which journals/conferences/venues publish these papers?
// -----------------------------------------------------
MATCH (p:Paper)-[:PUBLISHED_IN]->(v:Venue)
RETURN v.name AS venue,
       v.type AS venue_type,
       count(DISTINCT p) AS number_of_papers
ORDER BY number_of_papers DESC
LIMIT 10;


// -----------------------------------------------------
// 9. Concept co-occurrence
// Question: Which concepts often appear together in the same paper?
// -----------------------------------------------------
MATCH (p:Paper)-[:HAS_CONCEPT]->(c1:Concept),
      (p)-[:HAS_CONCEPT]->(c2:Concept)
WHERE c1.id < c2.id
RETURN c1.name AS concept_1,
       c2.name AS concept_2,
       count(DISTINCT p) AS cooccurrence_count
ORDER BY cooccurrence_count DESC
LIMIT 20;


// -----------------------------------------------------
// 10. Author → Paper → Concept path
// Question: What concepts are authors connected to through their papers?
// -----------------------------------------------------
MATCH (a:Author)-[:AUTHORED]->(p:Paper)-[hc:HAS_CONCEPT]->(c:Concept)
RETURN a.name AS author,
       p.title AS paper,
       p.year AS year,
       c.name AS concept,
       hc.score AS concept_score
ORDER BY concept_score DESC
LIMIT 30;


// -----------------------------------------------------
// 11. Citation paths
// Question: Which imported/cited papers cite other papers?
// -----------------------------------------------------
MATCH (p:Paper)-[:CITES]->(q:Paper)
WHERE p.title IS NOT NULL
RETURN p.title AS citing_paper,
       q.title AS cited_paper,
       p.year AS citing_year
ORDER BY citing_year DESC
LIMIT 20;


// -----------------------------------------------------
// 12. Visualize a small graph
// Question: Can we visually inspect Author → Paper → Concept paths?
// -----------------------------------------------------
MATCH path = (a:Author)-[:AUTHORED]->(p:Paper)-[:HAS_CONCEPT]->(c:Concept)
RETURN path
LIMIT 25;