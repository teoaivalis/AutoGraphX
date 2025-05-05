#!/bin/bash

# Define Neo4j credentials
NEO4J_USER="neo4j"
NEO4J_PASS="----"

INPUT_DIR="./cleaned_triples_for_generated_images"
OUTPUT_DIR="./neo4j_results_per_generated_image"

# Create output directory if not exists
mkdir -p "$OUTPUT_DIR"

# Extract base product names (without the trailing _number) to group variations
product_bases=$(ls "$INPUT_DIR"/output_*.txt | sed -E 's#^.*/output_(.*)_[0-9]+\.txt$#\1#' | sort | uniq)

# Loop over each base product
for base in $product_bases; do
    # Define CSV file per base product
    CSV_FILE="$OUTPUT_DIR/${base}.csv"
    echo "product_name,related_product,common_attributes" > "$CSV_FILE"

    # Loop over each variation of the current product
    for file in "$INPUT_DIR"/output_"${base}"_*.txt; do
        PRODUCT_NAME=$(basename "$file" .txt | sed 's/^output_//')

        # Construct exclusion list (all variations of current base)
        EXCLUDE_LIST=$(ls "$INPUT_DIR"/output_"${base}"_*.txt | sed 's#.*/output_##; s/\.txt//' | sed "s/^/'/;s/$/'/" | paste -sd "," -)

        QUERY="MATCH (p1:Product {name:'$PRODUCT_NAME'})-[r]->(a)<-[r2]-(p2:Product)
               WHERE p1 <> p2 AND NOT p2.name IN [$EXCLUDE_LIST]
               WITH p2.name AS related_product, COUNT(a) AS common_attributes
               RETURN '$PRODUCT_NAME', related_product, common_attributes
               ORDER BY common_attributes DESC;"

        # Execute Neo4j query and append to CSV file
        echo "$QUERY" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" --format=plain | tail -n +3 >> "$CSV_FILE"

        echo "Completed query for $PRODUCT_NAME."
    done

    echo "Results saved to $CSV_FILE"
done

echo "All queries executed successfully."
