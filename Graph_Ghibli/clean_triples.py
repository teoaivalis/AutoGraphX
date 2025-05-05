import os
import re

def clean_triple_line(line):
    # Remove unwanted spaces and trailing dots
    line = line.strip().rstrip('.').strip()
    # Remove parentheses completely
    line = line.replace('(', '').replace(')', '')
    # Normalize spaces around commas
    line = re.sub(r'\s*,\s*', ', ', line)  # exactly one space after each comma
    return line

def clean_triples_folder(input_folder, output_folder):
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all text files
    input_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]

    for filename in input_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        cleaned_lines = []

        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                # Find multiple triples if packed together
                triples = re.findall(r'\([^()]+\)', line)
                if triples:
                    for triple in triples:
                        cleaned_lines.append(clean_triple_line(triple))
                else:
                    # If the line is already simple, clean it
                    cleaned_lines.append(clean_triple_line(line))

        # Save cleaned triples to a new file
        if cleaned_lines:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write("\n".join(cleaned_lines))

    print(f"Cleaning complete. Cleaned files saved in: {output_folder}")

if __name__ == "__main__":
    input_folder = './originals_descriptions'
    output_folder = './cleaned_originals_descriptions'

    clean_triples_folder(input_folder, output_folder)


