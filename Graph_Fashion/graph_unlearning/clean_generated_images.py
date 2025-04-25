import os
import re

# Define input directory (where your extracted text files are)
input_dir = "./triples_for_generated_images"  # Adjust if needed
output_dir = "./cleaned_triples_for_generated_images"  # Adjust if needed

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)


# Get all text files from the input directory
input_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

# Regular expression to match valid triples
triple_pattern = re.compile(r"\d+\.\s*\((\d+\.jpg),\s*([\w_]+),\s*([\w\s-]+)\)")

# Process each file
for file_name in input_files:
    input_file_path = os.path.join(input_dir, file_name)
    output_file_path = os.path.join(output_dir, file_name)  # Keep the same file name

    cleaned_triples = []

    with open(input_file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Remove any explanation text
            line = line.strip()
            if "The triples describe" in line or "This response provides" in line:
                continue  # Skip explanation lines

            # Extract and clean the triple
            match = triple_pattern.match(line)
            if match:
                image_id, relation, value = match.groups()
                cleaned_triples.append(f"{image_id}, {relation}, {value}")

    # Save the cleaned data
    if cleaned_triples:  # Avoid empty files
        with open(output_file_path, "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(cleaned_triples))

print(f"Processing complete. Cleaned files are saved in: {output_dir}")
