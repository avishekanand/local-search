import csv
import matplotlib.pyplot as plt

def main():
    # Use the specified input file path
    input_file = "/Users/avishekanand/Projects/search-engine/batched_query_precision_20.csv"

    queries = []
    precision_values = []
    time_values = []

    # Read the CSV file; it should have a header: query,precision@10,time@10
    with open(input_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            queries.append(row["query"])
            precision_values.append(float(row["precision@10"]))
            time_values.append(float(row["time@10"]))

    # Compute the average precision
    if precision_values:
        avg_precision = sum(precision_values) / len(precision_values)
        print(f"Average precision@10: {avg_precision:.2f}")
    else:
        avg_precision = 0.0
        print("No precision values found.")

    # --- Plot 1: Horizontal Bar Chart of Precision ---
    plt.figure(figsize=(12, 8))
    plt.barh(queries, precision_values, color="skyblue")
    
    # Reduce font sizes on the first plot
    plt.xlabel("Precision@10", fontsize=10)
    plt.title("Precision@10 for Queries", fontsize=12)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    
    # Plot the average precision as a red dashed vertical line
    plt.axvline(avg_precision, color='red', linestyle='--', label=f'Average Precision: {avg_precision:.2f}')
    plt.legend(fontsize=8)
    
    plt.gca().invert_yaxis()  # Invert y-axis so the query with the highest precision appears at the top
    plt.tight_layout()
    plt.show()

    # --- Plot 2: Scatter Plot of Precision vs. Time ---
    plt.figure(figsize=(8, 6))
    plt.scatter(time_values, precision_values, color="darkgreen")
    plt.xlabel("Time@10")
    plt.ylabel("Precision@10")
    plt.title("Precision@10 vs. Time@10 for Queries")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()