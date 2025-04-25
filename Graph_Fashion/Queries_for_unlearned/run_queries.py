import os
import pandas as pd
from neo4j import GraphDatabase
import sys

# -----------------------------
# Neo4j Connection Parameters
# -----------------------------
uri = "bolt://localhost:7687"
user = "neo4j"
password = "-----"

driver = GraphDatabase.driver(uri, auth=(user, password))

# -----------------------------
# Define All Queries
# -----------------------------
queries = {
    "attribute_listing_top_images": """
        MATCH (p:Product)-[r]->(a)
        WHERE p.name IN $topProducts
        RETURN p.name AS product_name, COLLECT({relationship: TYPE(r), attribute: a.name}) AS attributes
    """,
    "graph_visualisation_top_products": """
        MATCH (p:Product)-[r]->(a)
        WHERE p.name IN $topProducts
        RETURN p.name AS product, TYPE(r) AS relationship, a.name AS attribute
    """,
    "distinct_attribute_values": """
        MATCH (p:Product)-[r]->(a)
        WHERE p.name IN $topProducts
        RETURN TYPE(r) AS relationshipType, COUNT(DISTINCT a.name) AS unique_value_count,
               COLLECT(DISTINCT a.name) AS unique_values
        ORDER BY unique_value_count DESC
    """,
    "attribute_cooccurrence_patterns": """
        MATCH (p:Product)-[r1]->(a1), (p)-[r2]->(a2)
        WHERE p.name IN $topProducts AND a1 <> a2
        RETURN TYPE(r1) AS relation1, a1.name AS attribute1,
               TYPE(r2) AS relation2, a2.name AS attribute2,
               COUNT(*) AS frequency
        ORDER BY frequency DESC
    """,
    "shared_attributes_between_pairs": """
        MATCH (p1:Product)-[r1]->(a)<-[r2]-(p2:Product)
        WHERE p1.name IN $topProducts AND p2.name IN $topProducts AND p1 <> p2
        RETURN p1.name AS product1, p2.name AS product2, COUNT(a) AS shared_attributes
        ORDER BY shared_attributes DESC
    """,
    "clustering_shared_attributes_5": """
        MATCH (p1:Product)-[r1]->(a)<-[r2]-(p2:Product)
        WHERE p1.name IN $topProducts AND p2.name IN $topProducts AND p1 <> p2
        WITH p1, p2, COUNT(a) AS shared_attributes
        WHERE shared_attributes >= 5
        WITH p1, COLLECT(DISTINCT p2.name) AS similar_products
        RETURN COLLECT(p1.name) AS cluster
        ORDER BY SIZE(cluster) DESC
    """,
    "clustering_shared_attributes_7": """
        MATCH (p1:Product)-[r1]->(a)<-[r2]-(p2:Product)
        WHERE p1.name IN $topProducts AND p2.name IN $topProducts AND p1 <> p2
        WITH p1, p2, COUNT(a) AS shared_attributes
        WHERE shared_attributes >= 7
        WITH p1, COLLECT(DISTINCT p2.name) AS similar_products
        RETURN COLLECT(p1.name) AS cluster
        ORDER BY SIZE(cluster) DESC
    """,
    "most_distinct_products": """
        MATCH (p1:Product)-[r1]->(a)
        WHERE p1.name IN $topProducts
        WITH p1, COUNT(a) AS attribute_count
        ORDER BY attribute_count ASC
        LIMIT 10
        RETURN p1.name AS unique_product, attribute_count
    """
}

def extract_top_images(csv_path):
    try:
        df = pd.read_csv(csv_path)
        image_column = [col for col in df.columns if 'image' in col.lower() or 'name' in col.lower()][0]
        return df[image_column].astype(str).str.strip(" '\"").head(40).tolist()
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return []

def run_queries_for_file(file_path, output_dir):
    top_products = extract_top_images(file_path)
    if not top_products:
        return

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_output_dir = os.path.join(output_dir, file_name)
    os.makedirs(file_output_dir, exist_ok=True)

    with driver.session() as session:
        for name, query in queries.items():
            print(f"Running: {name} for {file_name}")
            result = session.run(query, topProducts=top_products)
            records = [record.data() for record in result]
            df = pd.DataFrame(records)
            df.to_csv(os.path.join(file_output_dir, f"{name}.csv"), index=False)
            print(f"Saved to: {name}.csv")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_all_cleaned_v3.py <main_folder>")
        sys.exit(1)

    main_folder = sys.argv[1]
    if not os.path.isdir(main_folder):
        print(f"Provided path '{main_folder}' is not a directory.")
        sys.exit(1)

    for filename in os.listdir(main_folder):
        if filename.endswith(".csv"):
            full_path = os.path.join(main_folder, filename)
            run_queries_for_file(full_path, main_folder)

    driver.close()

