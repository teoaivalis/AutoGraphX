
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys

def analyze_results(result_dir):
    files = {
        "attribute_listing": os.path.join(result_dir, "attribute_listing_top_images.csv"),
        "graph_visualisation": os.path.join(result_dir, "graph_visualisation_top_products.csv"),
        "distinct_attributes": os.path.join(result_dir, "distinct_attribute_values.csv"),
        "attribute_cooccurrence": os.path.join(result_dir, "attribute_cooccurrence_patterns.csv"),
        "shared_attribute_pairs": os.path.join(result_dir, "shared_attributes_between_pairs.csv"),
        "clustering_5": os.path.join(result_dir, "clustering_shared_attributes_5.csv"),
        "clustering_7": os.path.join(result_dir, "clustering_shared_attributes_7.csv"),
        "least_attributes": os.path.join(result_dir, "most_distinct_products.csv")
    }

    try:
        dfs = {name: pd.read_csv(path) for name, path in files.items()}
    except Exception as e:
        print(f"Skipping {result_dir} due to error reading files: {e}")
        return

    stats = {}
    stats['num_relationship_types'] = dfs['distinct_attributes']['relationshipType'].nunique()
    stats['avg_unique_values_per_relation'] = dfs['distinct_attributes']['unique_value_count'].mean()

    most_common_rel = dfs['distinct_attributes'].sort_values("unique_value_count", ascending=False).iloc[0]
    stats['most_common_relationship'] = most_common_rel['relationshipType']
    stats['most_common_relationship_value_count'] = most_common_rel['unique_value_count']

    stats['max_shared_attributes'] = dfs['shared_attribute_pairs']['shared_attributes'].max()
    stats['avg_shared_attributes'] = dfs['shared_attribute_pairs']['shared_attributes'].mean()

    stats['num_clusters_5'] = len(dfs['clustering_5'])
    stats['num_clusters_7'] = len(dfs['clustering_7'])
    stats['largest_cluster_size_5'] = dfs['clustering_5']['cluster'].apply(eval).apply(len).max()
    stats['largest_cluster_size_7'] = dfs['clustering_7']['cluster'].apply(eval).apply(len).max()

    stats['min_attribute_count'] = dfs['least_attributes']['attribute_count'].min()
    stats['attribute_count_std'] = dfs['least_attributes']['attribute_count'].std()

    # Write text summary
    summary_path = os.path.join(result_dir, "statistics_summary.txt")
    with open(summary_path, "w") as f:
        f.write("## Attribute Richness & Diversity\n\n")
        f.write(f"- **Number of distinct attribute relationships**: {stats['num_relationship_types']}\n")
        f.write(f"- **Average unique values per relationship**: {stats['avg_unique_values_per_relation']:.2f}\n")
        f.write(f"- **Most common relationship**: `{stats['most_common_relationship']}`\n")
        f.write(f"- **Unique values in most common relationship**: {stats['most_common_relationship_value_count']}\n\n")

        f.write("---\n\n## Product-to-Product Similarity\n\n")
        f.write(f"- **Maximum shared attributes between any product pair**: {stats['max_shared_attributes']}\n")
        f.write(f"- **Average shared attributes across all pairs**: {stats['avg_shared_attributes']:.2f}\n")
        f.write(f"- **Minimum attribute count across products**: {stats['min_attribute_count']}\n")
        f.write(f"- **Standard deviation of attribute counts**: {stats['attribute_count_std']:.2f}\n\n")

        f.write("---\n\n## Clustering Structure\n\n")
        f.write(f"- **Number of clusters with ≥ 5 shared attributes**: {stats['num_clusters_5']}\n")
        f.write(f"- **Number of clusters with ≥ 7 shared attributes**: {stats['num_clusters_7']}\n")
        f.write(f"- **Size of largest cluster (≥ 5 shared attributes)**: {stats['largest_cluster_size_5']}\n")
        f.write(f"- **Size of largest cluster (≥ 7 shared attributes)**: {stats['largest_cluster_size_7']}\n\n")

        f.write("---\n\n## Visual Summaries\n\n")
        f.write("- `unique_values_per_relation.png`: Bar chart showing the number of unique values per attribute relationship.\n")
        f.write("- `top_attribute_pairs.png`: Bar chart of the top 10 most frequently co-occurring attribute pairs.\n")
        f.write("---\n")

    # Plots
    plt.figure(figsize=(10, 6))
    sns.barplot(x=dfs['distinct_attributes']['relationshipType'],
                y=dfs['distinct_attributes']['unique_value_count'])
    plt.xticks(rotation=45, ha="right")
    plt.title("Unique Attribute Values per Relationship Type")
    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, "unique_values_per_relation.png"))
    plt.close()

    plt.figure(figsize=(10, 6))
    top_pairs = dfs['attribute_cooccurrence'].sort_values("frequency", ascending=False).head(10)
    sns.barplot(y=top_pairs['attribute1'] + " & " + top_pairs['attribute2'],
                x=top_pairs['frequency'])
    plt.title("Top 10 Attribute Co-occurrence Pairs")
    plt.xlabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, "top_attribute_pairs.png"))
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_all_results.py <main_output_folder>")
        sys.exit(1)

    root = sys.argv[1]
    for folder in os.listdir(root):
        folder_path = os.path.join(root, folder)
        if os.path.isdir(folder_path):
            print(f"Analyzing {folder_path}")
            analyze_results(folder_path)
