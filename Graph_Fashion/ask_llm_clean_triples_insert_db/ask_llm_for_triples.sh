#!/bin/bash

# Define your directories
IMAGE_DIR="./fashion_dataset"
BASE64_DIR="./base64_images"
OUTPUT_DIR="./llm_fashion_triples"

mkdir -p "$BASE64_DIR"
mkdir -p "$OUTPUT_DIR"

# Iterate over all images in the IMAGE_DIR
for IMAGE_PATH in "$IMAGE_DIR"/*.jpg; do
    # Extract the image filename without extension
    FILENAME=$(basename "$IMAGE_PATH" .png)
    IMAGE_ID=$FILENAME  # Image ID is now correctly extracted
    
    # Step 1: Convert the image to Base64 and save it
    BASE64_FILE="$BASE64_DIR/${FILENAME}_base64.txt"
    base64 -w 0 "$IMAGE_PATH" > "$BASE64_FILE"

    # Step 2: Send the Base64 image to the chat API and save the text-triples output
    OUTPUT_FILE="$OUTPUT_DIR/output_${FILENAME}.txt"
    curl http://localhost:11434/api/chat -d "{
      \"model\": \"llama3.2-vision\",
      \"messages\": [                                                                  
        {
          \"role\": \"user\",
          \"content\": \"Create Triples for the fashion item in the image based on the following relationships. Include information on the following aspects: (1) depicts: Assign the most relevant garment category (Shirt, Blouse, T-shirt, Sweatshirt, Sweater, Cardigan, Jacket, Vest, Pants, Shorts, Skirt, Coat, Dress, Jumpsuit, Cape, Glasses, Hat, Headband, Hair Accessory, Tie, Scarf, Glove, Watch, Belt, Leg, Warmers, Tights, Stockings, Socks, Shoes, Bag, Wallet, Umbrella, Hood, Collar, Lapel, Epaulette, Sleeve, Pocket, Neckline, Buckle, Zipper, Applique, Bead, Bow, Flower, Fringe, Ribbon, Rivet, Ruffle, Sequin, Tassel, etc.), (2) belongs_to_category: Assign the correct supercategory (upperbody, lowerbody, wholebody, head, neck, arms and hands, waist, legs and feet, others, garment parts, closures, decorations), (3) has_nickname: Assign a valid nickname if applicable, (4) has_silhouette: Assign the most appropriate silhouette, (5) has_waistline: Specify the waistline type, (6) has_length: Define the length, (7) has_collar_type: Specify the collar style, (8) has_lapel_type: Define the lapel type, (9) has_neckline: Assign the correct neckline, (10) has_sleeve_type: Specify the sleeve type, (11) has_pocket_type: Define the pocket type, (12) has_opening_type: Assign the opening type, (13) has_material_type: Define the material type, (14) has_leather_type: Specify the leather type if applicable, (15) has_fabric_treatment: Define any textile finishing or techniques, (16) has_pattern: Assign a pattern type, (17) has_animal_pattern: Specify the animal pattern if applicable. Focus exclusively on the fashion item of the image with image_ id: ${IMAGE_ID=} and give me the triples that describes the image (image_id, relationship, attribute_value) with nodes(image_id) and edges (relationships). Please do not give more ccomments, only the triples ( , , ).\",
          \"images\": [\"$(cat $BASE64_FILE)\"]
        }                     
      ],  \"stream\": false
    }" | jq -r '.message.content' | sed -e 's/\\n/\n/g' -e 's/\\t//g' -e 's/+//g' > "$OUTPUT_FILE"

    echo "Processed $IMAGE_PATH: Output saved to $OUTPUT_FILE"
done
