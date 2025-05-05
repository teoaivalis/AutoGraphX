#!/bin/bash

# Define directories
IMAGE_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/generated"
BASE64_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/updated_base64_images_ghibli_style_generated"
OUTPUT_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/generated_descriptions"
#IMAGE_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/originals"
#BASE64_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/updated_base64_images_ghibli_style_originals"
#OUTPUT_DIR="/home/teo/storage/llama_experiments/ghibli_experiments/originals_descriptions"
PROMPT_TEMPLATE="./ontology.txt"


# Extract movie name
MOVIE_NAME=$(basename "$IMAGE_DIR")

mkdir -p "$BASE64_DIR"
mkdir -p "$OUTPUT_DIR"

for IMAGE_PATH in "$IMAGE_DIR"/*.png; do
    FILENAME=$(basename "$IMAGE_PATH" .png)
    IMAGE_ID=$FILENAME

    BASE64_FILE="$BASE64_DIR/${FILENAME}_base64.txt"
    base64 -w 0 "$IMAGE_PATH" > "$BASE64_FILE"

    OUTPUT_FILE="$OUTPUT_DIR/output_${FILENAME}.txt"
    

    # Create prompt
    TEMP_PROMPT="temp_prompt_${IMAGE_ID}.txt"
    sed "s/\${IMAGE_ID}/$IMAGE_ID/g; s/\${MOVIE_NAME}/$MOVIE_NAME/g" "$PROMPT_TEMPLATE" > "$TEMP_PROMPT"

    # Create the complete JSON payload
    TEMP_REQUEST="temp_request_${IMAGE_ID}.json"
    cat <<EOF > "$TEMP_REQUEST"
{
  "model": "llama3.2-vision",
  "messages": [
    {
      "role": "user",
      "content": "$(cat "$TEMP_PROMPT")",
      "images": ["$(cat "$BASE64_FILE")"]
    }
  ],
  "stream": false
}
EOF

    # Now send request using --data-binary (no size limit)
    curl -s -X POST http://localhost:11434/api/chat --data-binary @"$TEMP_REQUEST" | jq -r '.message.content' | sed -e 's/\\n/\n/g' -e 's/\\t//g' -e 's/+//g' > "$OUTPUT_FILE"

    echo "Processed $IMAGE_PATH: Output saved to $OUTPUT_FILE"

    # Clean up
    rm "$TEMP_PROMPT" "$TEMP_REQUEST"
done

echo "Finished processing all images."

