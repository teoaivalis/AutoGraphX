import os
import re

def load_triples(file_path):
    """Load triples from a cleaned text file into a set."""
    triples = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                triples.add(line)
    return triples

def extract_id(filename):
    """Extract the numeric ID from a filename like output_g83.txt or output_o83.txt."""
    match = re.search(r'(\d+)', filename)
    return match.group(1) if match else None

def compare_triples(original_folder, generated_folder, output_folder):
    """Compare original and generated triples, saving differences."""
    os.makedirs(output_folder, exist_ok=True)

    original_files = [f for f in os.listdir(original_folder) if f.endswith('.txt')]
    generated_files = [f for f in os.listdir(generated_folder) if f.endswith('.txt')]

    # Map by extracted ID
    original_map = {extract_id(f): f for f in original_files}
    generated_map = {extract_id(f): f for f in generated_files}

    for img_id in generated_map.keys():
        if img_id and img_id in original_map:
            original_path = os.path.join(original_folder, original_map[img_id])
            generated_path = os.path.join(generated_folder, generated_map[img_id])

            original_triples = load_triples(original_path)
            generated_triples = load_triples(generated_path)

            # Find extra triples in generated
            extra_triples = generated_triples - original_triples

            if extra_triples:
                output_file = os.path.join(output_folder, f"diff_{img_id}.txt")
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    f_out.write("\n".join(sorted(extra_triples)))

    print(f"Differences saved in: {output_folder}")

if __name__ == "__main__":
    original_folder ='./cleaned_originals_descriptions'
    generated_folder ='./cleaned_generated_descriptions'
    output_folder ='./differences'

    compare_triples(original_folder, generated_folder, output_folder)

