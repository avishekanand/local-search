import csv
import os
import sys
import time
import yaml

# Add the project root directory to sys.path so that modules can be imported.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.services.query_service import QueryService
from backend.app.services.evaluation_service import EvaluationService

def load_config():
    """
    Loads the YAML configuration file.
    """
    CONFIG_PATH = os.path.abspath("config/config.yml")
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)

def load_queries(csv_file):
    """
    Loads queries from a CSV file.
    The CSV is expected to have a header with at least a column "query".
    
    :param csv_file: Path to the CSV file.
    :return: A list of query strings.
    """
    queries = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # For debugging, you can print out the header keys:
        # print("CSV header keys:", reader.fieldnames)
        for row in reader:
            # Use a case-insensitive lookup for the "query" column.
            lower_row = {key.lower(): value for key, value in row.items()}
            query = lower_row.get("query")
            if query:
                queries.append(query.strip())
    return queries

def main():
    # Load configuration.
    config = load_config()
    
    # Setup retrieval and indexing settings.
    retrieval_model = config["retrieval"]["model"]
    index_directory = config["indexing"]["directory"]

    # Setup evaluation settings.
    ollama_config = config.get("ollama", {})
    ollama_endpoint = ollama_config.get("endpoint", "http://localhost:11434/api/generate")
    ollama_model = ollama_config.get("model", "deepseek-r1:8b")

    # Setup query workload settings.
    queries_csv = config.get("query_workload", {}).get("csv_path", "queries_frequency.csv")
    
    # Initialize the QueryService and EvaluationService.
    query_service = QueryService(model_name=retrieval_model, index_dir=index_directory)
    evaluation_service = EvaluationService(endpoint=ollama_endpoint, model=ollama_model)
    
    # Load queries from the CSV file and limit to 50.
    queries = load_queries(queries_csv)
    queries = queries[:365]
    
    # We'll compute precision at 10, 20, and 100.
    top_k_values = [10]
    
    # List to hold output rows for CSV.
    # Each row will have: query, precision@10, time@10, precision@20, time@20, precision@100, time@100.
    output_rows = []
    
    print("\n=== Evaluating Query Workload (Batched) ===\n")
    
    for query in queries:
        # Retrieve up to 100 results for this query.
        results = query_service.search(query, top_k=100)
        # Build a list of documents (each as a dict with "title" and "description").
        docs = []
        for result in results:
            title = result["metadata"]["title"]
            # Here we assume description is under metadata->metadata with key "resposibilities".
            description = result["metadata"]["metadata"].get("resposibilities", "")
            docs.append({"title": title, "description": description})
        
        query_results = {"query": query}
        
        # Evaluate at different top_k levels.
        for k in top_k_values:
            # If there are fewer than k documents, use what is available.
            current_docs = docs if len(docs) < k else docs[:k]
            
            start_time = time.perf_counter()
            labels = evaluation_service.evaluate_batch(query, current_docs, k)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            
            # Compute precision: assume "relevant" = 1.0, "partially relevant" = 0.5, "not relevant" = 0.0.
            relevance_sum = 0.0
            for label in labels:
                label_lower = label.lower()
                if label_lower == "relevant":
                    relevance_sum += 1.0
                elif label_lower == "partially relevant":
                    relevance_sum += 0.5
                # "not relevant" or any other value gets 0 credit.
            precision = relevance_sum / k if k > 0 else 0.0
            
            query_results[f"precision@{k}"] = precision
            query_results[f"time@{k}"] = elapsed_time
            print(f"Query: {query}  =>  Precision@{k}: {precision:.2f}, Time: {elapsed_time:.2f} sec")
        
        output_rows.append(query_results)
    
    # Write the results to a CSV file.
    output_csv = "batched_query_precision_20.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["query"]
        for k in top_k_values:
            fieldnames.append(f"precision@{k}")
            fieldnames.append(f"time@{k}")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)
    print(f"\nBatched evaluation results written to {output_csv}")

if __name__ == "__main__":
    main()