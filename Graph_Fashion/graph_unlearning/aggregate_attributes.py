import pandas as pd
import glob
import os

# Define the directory containing your Neo4j result CSV files
input_dir = "./neo4j_results_per_product/outputs_before_10"
output_dir = "./aggregated_results_per_product/outputs_before_10"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each CSV file individually
for file in glob.glob(os.path.join(input_dir, "*.csv")):
    # Read the individual CSV file
    df = pd.read_csv(file)

    # Ensure correct column names
    df.columns = ['product_name', 'related_product', 'common_attributes']

    # Aggregate by summing the 'common_attributes' column grouped by 'related_product'
    aggregated_df = df.groupby('related_product', as_index=False)['common_attributes'].sum()

    # Sort the aggregated DataFrame by total common attributes in descending order
    sorted_df = aggregated_df.sort_values(by='common_attributes', ascending=False)

    # Rename columns for clarity
    sorted_df.columns = ['product_name', 'total_shared_attributes']

    # Prepare output file path
    output_file = os.path.join(output_dir, os.path.basename(file).replace(".csv", "_aggregated.csv"))

    # Save the aggregated and sorted results to a new CSV file
    sorted_df.to_csv(output_file, index=False)

print("Aggregated rankings saved individually in the folder 'aggregated_results_per_product'.")
