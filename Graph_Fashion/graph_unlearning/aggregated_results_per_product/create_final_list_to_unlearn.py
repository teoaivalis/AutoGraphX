import pandas as pd
import glob
import os

# Directory containing your aggregated CSV files
input_dir = "./outputs_before_1"
output_file = "./top_45_products_1.txt"

# Open the output file for writing
with open(output_file, 'w', encoding='utf-8') as out_file:
    # Process each CSV file in the specified directory
    for file_path in glob.glob(os.path.join(input_dir, "*.csv")):
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Get the top 45 product names based on the ranking
        top_45_products = df.head(45)['product_name'].tolist()

        # Write the top products to the text file
        csv_file_name = os.path.basename(file_path)
        out_file.write(f"Top 45 products from {csv_file_name}:\n")
        for product in top_45_products:
            out_file.write(f"{product}\n")
        out_file.write("\n")

print(f"Top 45 products from each CSV have been saved to '{output_file}'.")


# Full Python script to clean product names from top_45_products.txt

# Input and output file paths
input_file = './top_45_products_1.txt'
output_file = './cleaned_top_45_products_11.txt'

# Open and process the input file
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Process lines to extract only product names
cleaned_products = []
for line in lines:
    line = line.strip()
    if line.startswith("Top 45 products from") or line == "":
        continue
    product_name = line.replace('"', '').strip()
    cleaned_products.append(product_name)

# Save cleaned product names to the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    for product in cleaned_products:
        outfile.write(product + '\n')

print(f"Cleaned product names saved to '{output_file}'.")

