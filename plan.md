Build a Python + Neo4j MVP for a thesis prototype on rule-guided question answering over biomedical property graphs.

Use PrimeKG as the starting biomedical knowledge graph. Do not build document-to-KG extraction. The goal is to load an existing biomedical KG into Neo4j as a property graph, support Cypher-based QA, derive simple symbolic rules from graph patterns, and return answers with evidence paths and explanations.

Create this repo structure:

bio-property-graph-qa/
- data/raw/
- data/processed/
- src/config.py
- src/download_primekg.py
- src/preprocess_primekg.py
- src/neo4j_loader.py
- src/cypher_queries.py
- src/qa_engine.py
- src/rule_miner.py
- src/reasoner.py
- examples/sample_questions.json
- examples/sample_rules.json
- tests/test_queries.py
- tests/test_rules.py
- docker-compose.yml
- requirements.txt
- .env.example
- README.md

Implementation requirements:

1. Download or load PrimeKG CSV files.
2. Preprocess them into nodes.csv and edges.csv.
3. Keep only an MVP biomedical subset:
   - Disease
   - Drug
   - Gene/Protein
   - Symptom/Phenotype
   - Pathway

4. Load this into Neo4j using Cypher MERGE.
5. Create labels:
   - Disease
   - Drug
   - Gene
   - Symptom
   - Pathway

6. Create relationships:
   - TREATS
   - ASSOCIATED_WITH
   - HAS_SYMPTOM
   - PARTICIPATES_IN
   - CONTRAINDICATED_FOR if available

7. Implement at least 10 manual Cypher query templates.

8. Implement qa_engine.py with:
   - template-based natural language routing first
   - optional LLM-to-Cypher mode
   - Cypher safety validation allowing only read-only MATCH queries

9. Implement rule_miner.py with at least 3 simple rule types:
   - Drug treats Disease + Disease associated_with Gene => Drug indirectly related to Gene
   - Disease has Symptom + another Disease has same Symptom => diseases are symptom-similar
   - Disease associated_with Gene + Gene participates_in Pathway => disease may involve pathway

10. Implement reasoner.py that returns:
   - answer
   - cypher
   - rule_used
   - evidence_path
   - explanation

11. Provide CLI commands:
   - python src/download_primekg.py
   - python src/preprocess_primekg.py --limit 50000
   - python src/neo4j_loader.py
   - python src/qa_engine.py "What drugs treat diabetes?"
   - python src/rule_miner.py

12. Include README instructions.

Acceptance criteria:
- Neo4j runs with docker-compose.
- At least 10,000 nodes and 50,000 relationships can be loaded.
- At least 5 natural language biomedical questions return answers.
- At least 3 symbolic rule types are derived.
- QA output includes answer, Cypher, rule used, evidence path, and explanation.

Avoid:
- SPARQL
- Freebase/Wikidata benchmark focus
- document-to-KG extraction
- model training
- frontend overengineering