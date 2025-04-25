import os
import re

input_file = "cleaned_top_45_products_1.txt"
target_dir = "fashion_dataset"
output_file = "extracted_numbers_1.txt"

# Read filenames from the input text file
with open(input_file, "r", encoding="utf-8") as f:
    filenames = [line.strip().replace('"', '') for line in f if line.strip()]

# Extract numbers from filenames
numbers_list = []
for filename in filenames:
    matches = re.findall(r'\d+', filename)
    if matches:
        numbers_list.append(matches[0])
    else:
        print(f"Skipping invalid filename (no digits): '{filename}'")

# Remove duplicates
numbers_list = list(set(numbers_list))

# Save extracted numbers
with open(output_file, "w") as out_file:
    for num in numbers_list:
        out_file.write(f"{num}\n")

# Delete corresponding .txt and .jpg files
for number in numbers_list:
    for ext in ['.txt', '.jpg']:
        file_path = os.path.join(target_dir, f"{number}{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")
