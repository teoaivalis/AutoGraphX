import os
from neo4j import GraphDatabase

# Neo4j connection details
URI = "neo4j://localhost:7687"  # Change this if Neo4j is running elsewhere
USERNAME = "neo4j"
PASSWORD = "-----"  # Replace with your actual Neo4j password

# Define Neo4j driver
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Mapping of relationship variations to a standardized format
RELATIONSHIP_MAPPING = {
    "depicts": "depicts",
    "belongs_to_category": "belongsToCategory",
    "has_nickname": "hasNickname",
    "has_silhouette": "hasSilhouette",
    "has_waistline": "hasWaistline",
    "has_length": "hasLength",
    "has_collar_type": "hasCollarType",
    "has_lapel_type": "hasLapelType",
    "has_neckline": "hasNeckline",
    "has_sleeve_type": "hasSleeveType",
    "has_pocket_type": "hasPocketType",
    "has_opening_type": "hasOpeningType",
    "has_material_type": "hasMaterialType",
    "has_leather_type": "hasLeatherType",
    "has_fabric_treatment": "hasFabricTreatment",
    "has_pattern": "hasPattern",
    "has_animal_pattern": "hasAnimalPattern"
}

# Attribute standardization dictionary
ATTRIBUTE_MAPPING = {
    "hasSilhouette": {
        "straight": ["straight", "straight cut", "straight silhouette"],
        "a-line": ["a-line", "a-line silhouette", "a-line shape"],
        "round": ["round", "round silhouette", "round neckline", "round-toe"],
        "rectangular": ["rectangular", "rectangle", "rectangular silhouette"],
        "slim-fit": ["slim fit", "slim-fit", "slim fitting silhouette"],
        "loose-fit": ["loose fit", "loose-fitting", "loose silhouette"],
        "none": ["none", "no silhouette", "not applicable", "unspecified"]
    },
    "hasCollarType": {
        "none": ["none", "no collar", "no-collar", "collarless"],
        "crew-neck": ["crew neck", "crew-neck", "crewneck"],
        "v-neck": ["v-neck", "v-neck collar", "v-neckline"],
        "spread-collar": ["spread collar", "spread"],
        "pointed-collar": ["pointed collar", "point collar"],
        "mandarin-collar": ["mandarin collar", "mandarin"],
        "notch-collar": ["notch collar", "notched collar"]
    },
    "hasSleeveType": {
        "sleeveless": ["sleeveless", "no sleeves", "strapless"],
        "short-sleeve": ["short sleeves", "short sleeve", "short-sleeved"],
        "long-sleeve": ["long sleeves", "long sleeve", "long-sleeved"],
        "three-quarter-sleeve": ["three-quarter sleeve", "three-quarter"]
    },
    "hasPattern": {
        "none": ["none", "no pattern", "plain", "solid"],
        "striped": ["striped", "stripes", "stripe-pattern"],
        "floral": ["floral", "floral pattern"],
        "polka-dot": ["polka dots", "polka dot"],
        "geometric": ["geometric", "geometric pattern"],
        "animal-print": ["animal print", "zebra print", "leopard print", "tiger print"]
    },
    "hasWaistline": {
        "none": ["none", "no waistline", "no-waistline"],
        "high-waisted": ["high-waisted", "high waist"],
        "low-waisted": ["low-waisted", "low waist"],
        "natural-waist": ["natural waist", "mid-rise"],
        "straight": ["straight", "straight waistline"],
        "fitted": ["fitted", "fitted waist"]
    },
    "hasLength": {
        "short": ["short", "mini", "short length"],
        "long": ["long", "long length", "floor-length"],
        "midi": ["midi", "mid-length", "mid-calf"],
        "ankle-length": ["ankle-length", "ankle"],
        "knee-length": ["knee-length", "knee length"]
    },
    "hasOpeningType": {
        "none": ["none", "no opening", "no openings"],
        "button": ["button opening", "button-front", "buttoned"],
        "zipper": ["zipper", "zippered", "zip-up"],
        "lace-up": ["lace-up", "laces"]
    },
}

# General mapping for common "skipped" values
GENERAL_MAPPING = {
    "plain": "solid",
    "solid": "solid",
    "no collar": "none",
    "no lapel": "none",
    "collarless": "none",
    "no pockets": "none",
    "no fabric treatment": "none",
    "no animal pattern": "none",
    "no opening": "none"
}

def standardize_attribute(attribute_type, attribute_value):
    """
    Standardizes an attribute based on predefined mappings.
    """
    attribute_value_lower = attribute_value.strip().lower()

    # Check for standardization in specific attribute mappings
    if attribute_type in ATTRIBUTE_MAPPING:
        for standard, variations in ATTRIBUTE_MAPPING[attribute_type].items():
            if attribute_value_lower in [v.lower() for v in variations]:
                return standard

    # Convert commonly skipped values into meaningful categories
    if attribute_value_lower in GENERAL_MAPPING:
        return GENERAL_MAPPING[attribute_value_lower]

    # Skip truly empty values
    if attribute_value_lower in ["none", "not applicable", "unspecified", "undefined", "no information available"]:
        return None

    return attribute_value_lower

def insert_triple(tx, subject, predicate, object_):
    """
    Insert a triple into Neo4j using MERGE to avoid duplicates.
    """
    normalized_predicate = predicate.strip().replace(" ", "").lower()

    # Map relationship to a standard form
    standardized_predicate = RELATIONSHIP_MAPPING.get(normalized_predicate)
    if not standardized_predicate:
        print(f"Skipping invalid relationship: {predicate}")
        return

    # Standardize the object attribute if applicable
    standardized_object = standardize_attribute(standardized_predicate, object_)

    # Skip if the standardized object is "none" or equivalent
    if standardized_object is None or standardized_object == "none":
        print(f"Skipping insertion for empty or 'none' attribute: {object_}")
        return

    query = """
    MERGE (s:Product {name: $subject})
    MERGE (o:Attribute {name: $object})
    MERGE (s)-[r:RELATIONSHIP]->(o);
    """
    
    query = query.replace("RELATIONSHIP", standardized_predicate)  # Use standardized relationship name
    tx.run(query, subject=subject, object=standardized_object)

def process_file(file_path):
    """
    Read triples from a file and insert them into Neo4j.
    """
    with driver.session() as session:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                parts = [part.strip().replace('"', '') for part in line.strip().split(",")]
                if len(parts) == 3:
                    subject, predicate, object_ = parts
                    session.execute_write(insert_triple, subject, predicate, object_)
                else:
                    print(f"Skipping malformed line: {line.strip()}")

if __name__ == "__main__":
    processed_dir = "./cleaned_triples_for_generated_images"
    files = [os.path.join(processed_dir, f) for f in os.listdir(processed_dir) if f.endswith(".txt")]

    print("Starting data insertion into Neo4j...")

    for file in files:
        print(f"Processing file: {file}")
        process_file(file)

    driver.close()
    print("Data insertion complete!")

