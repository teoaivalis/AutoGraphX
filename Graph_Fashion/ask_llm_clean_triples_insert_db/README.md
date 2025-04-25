## `ask_llm_clean_triples_insert_db/`

- Contains the scripts and prompts used to query the LLM and extract triples.
- Uses RAG (Retrieval-Augmented Generation) with embedded ontology knowledge.
- Includes:
  - `llm_fashion_triples/`: raw triples generated from the model
  - `cleaned_llm_fashion_triples/`: cleaned triples with redundant info removed
  - `fashionpedia_ontology.txt`: defines the main Fashionpedia relations used

