import os
from collections import Counter
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "----"
RESULTS_DIR = "./found_frames"
MOVIES_DIR = "./results_movies"
AGGREGATED_DIR = "./found_movies_aggregated"

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_movie_name(tx, frame_id):
    query = f"""
    MATCH (f:Frame {{id: '{frame_id}'}})-[r]->(a)
    WHERE type(r) = 'from_movie'
    RETURN a.value AS movie_name
    """
    result = tx.run(query)
    record = result.single()
    return record["movie_name"] if record else None

def process_frames(result_file, output_file, aggregate_file):
    frame_to_movie = {}
    with open(result_file, 'r') as file:
        frame_ids = [line.strip() for line in file if line.strip()]

    for frame_id in frame_ids:
        with driver.session() as session:
            movie_name = session.read_transaction(get_movie_name, frame_id)
            if movie_name:
                frame_to_movie[frame_id] = movie_name

    # Save individual mappings
    with open(output_file, 'w') as out_file:
        for frame_id, movie_name in frame_to_movie.items():
            out_file.write(f"{frame_id}: {movie_name}\n")

    # Aggregate counts and save
    movie_counter = Counter(frame_to_movie.values())
    with open(aggregate_file, 'w') as agg_file:
        for movie_name, count in movie_counter.items():
            agg_file.write(f"{movie_name}: {count}\n")

# Make sure the movies results folders exist
os.makedirs(MOVIES_DIR, exist_ok=True)
os.makedirs(AGGREGATED_DIR, exist_ok=True)

# Run processing for all result_*.txt files
for filename in os.listdir(RESULTS_DIR):
    if filename.startswith("result_") and filename.endswith(".txt") and not filename.startswith("result_movies_"):
        result_file = os.path.join(RESULTS_DIR, filename)
        output_file = os.path.join(MOVIES_DIR, filename.replace("result_", "result_movies_"))
        aggregate_file = os.path.join(AGGREGATED_DIR, filename.replace("result_", "aggregate_movies_"))
        print(f"Processing {filename} -> {os.path.basename(output_file)} and {os.path.basename(aggregate_file)}")
        process_frames(result_file, output_file, aggregate_file)

print("All movies extracted and aggregated successfully.")

