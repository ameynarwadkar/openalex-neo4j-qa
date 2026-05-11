# OpenAlex Property Graph QA Prototype — Summary

## Goal

This prototype validates a minimal software pipeline for property-graph-based question answering and rule-derived reasoning.

The aim was not to build the final thesis dataset, but to confirm that the following pipeline works:

OpenAlex → Neo4j Property Graph → Cypher QA → Rule-Derived Relations → Natural Language to Cypher QA

## Dataset

The prototype uses a small OpenAlex subset around the topic:

`neuro-symbolic AI`

Approximately 500 papers were fetched using the OpenAlex API.

## Property Graph Schema

### Nodes

- Paper
- Author
- Institution
- Concept
- Venue

### Relationships

- Author AUTHORED Paper
- Author AFFILIATED_WITH Institution
- Paper HAS_CONCEPT Concept
- Paper PUBLISHED_IN Venue
- Paper CITES Paper

## Manual Cypher QA

The prototype includes manual Cypher queries for:

- Counting node types
- Counting relationship types
- Finding top authors
- Finding top concepts
- Finding productive institutions
- Finding common venues
- Finding concept co-occurrences
- Inspecting Author → Paper → Concept paths

## Derived Symbolic Rules

Three simple rule-derived relations were added:

### Rule 1: Author works on concept

If:

Author AUTHORED Paper  
Paper HAS_CONCEPT Concept  

Then:

Author WORKS_ON Concept

### Rule 2: Author collaboration

If:

Author A AUTHORED Paper  
Author B AUTHORED Paper  

Then:

Author A COLLABORATED_WITH Author B

### Rule 3: Concept relatedness

If:

Paper HAS_CONCEPT Concept A  
Paper HAS_CONCEPT Concept B  

Then:

Concept A RELATED_TO Concept B

## Natural Language QA

A basic natural-language-to-Cypher interface was implemented using an LLM.

Example questions:

- Which authors work on artificial intelligence?
- Which institutions publish the most papers?
- Which concepts appear most often?
- Explain why an author is connected to a concept.

## Main Takeaway

This prototype confirms that the technical pipeline works.

However, OpenAlex is mainly useful as a pipeline-validation dataset. For the thesis direction, a more practically relevant biomedical or industry knowledge graph should be used next.

The next step is to move from OpenAlex to PrimeKG or a similar biomedical knowledge graph.
