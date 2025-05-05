import os
import re
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "---"
DIFF_DIR = "./differences"
RESULTS_DIR = "./found_frames"

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Make sure results folder exists
os.makedirs(RESULTS_DIR, exist_ok=True)

def query_frames(tx, relation, value):
    query = f"""
    MATCH (f:Frame)-[:{relation}]->(a:Attribute {{value: '{value}'}})
    RETURN f.id AS frame_id
    """
    result = tx.run(query)
    return [record["frame_id"] for record in result]

def process_diff_file(diff_path, result_path):
    frames = set()
    with open(diff_path, 'r') as file:
        for line in file:
            line = line.strip()
            match = re.match(r"[^,]+,\s*(\w+),\s*(.+)", line)
            if match:
                relation, value = match.groups()
                with driver.session() as session:
                    frame_ids = session.read_transaction(query_frames, relation, value)
                    frames.update(frame_ids)

    # Save frames to result file
    with open(result_path, 'w') as out_file:
        for frame_id in frames:
            out_file.write(f"{frame_id}\n")

# Main loop
for filename in os.listdir(DIFF_DIR):
    if filename.startswith("diff_") and filename.endswith(".txt"):
        diff_path = os.path.join(DIFF_DIR, filename)
        result_filename = filename.replace("diff_", "result_")
        result_path = os.path.join(RESULTS_DIR, result_filename)
        process_diff_file(diff_path, result_path)

print("Processing completed.")

