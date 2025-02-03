import csv
import os
import sys
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
    The CSV is expected to have a header with at least the column "query".
    
    :param csv_file: Path to the CSV file.
    :return: A list of query strings.
    """
    queries = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row["query"].strip()
            if query:
                queries.append(query)
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

    # Initialize the QueryService and EvaluationService.
    query_service = QueryService(model_name=retrieval_model, index_dir=index_directory)
    evaluation_service = EvaluationService(endpoint=ollama_endpoint, model=ollama_model)

    # Get the CSV file path from configuration (under "query_workload").
    queries_csv = config.get("query_workload", {}).get("csv_path", "queries_frequency.csv")
    queries = load_queries(queries_csv)

    top_k = 10  # Number of top results to retrieve for each query.
    query_precision_results = []  # To store (query, precision) tuples.

    print("\n=== Evaluating Query Workload ===\n")
    for query in queries:
        # Retrieve the top-10 results for the query.
        results = query_service.search(query, top_k=top_k)
        relevance_sum = 0.0

        # For each retrieved result, evaluate its relevance.
        for result in results:
            title = result["metadata"]["title"]
            # Adjust the key if necessary; here we assume the description is under 'resposibilities'
            description = result["metadata"]["metadata"].get("resposibilities", "")
            
            # Evaluate the search result using the evaluation service.
            eval_result = evaluation_service.evaluate(query, title, description)
            
            # Based on the evaluation result, assign credit:
            # "relevant" -> 1.0, "partially relevant" -> 0.5, "not relevant" -> 0.0.
            eval_lower = eval_result.lower()
            if eval_lower == "relevant":
                relevance_sum += 1.0
            elif eval_lower == "partially relevant":
                relevance_sum += 0.5
            else:
                relevance_sum += 0.0

        # Compute precision as the weighted sum divided by the number of retrieved results.
        precision = relevance_sum / top_k if top_k > 0 else 0.0
        query_precision_results.append((query, precision))
        print(f"Query: {query}  =>  Precision: {precision:.2f}")

    # Write the results to a CSV file.
    output_csv = "query_precision.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "precision"])
        for query, precision in query_precision_results:
            writer.writerow([query, precision])
    print(f"\nResults written to {output_csv}")

if __name__ == "__main__":
    main()