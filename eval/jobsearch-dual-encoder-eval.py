import pandas as pd
import numpy as np
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from backend.app.services.query_service import QueryService

def load_queries_and_qrels(queries_file, qrels_file):
    """
    Load queries and qrels from their respective files.
    """
    queries = pd.read_csv(queries_file, header=None, names=["query_id", "query_text"])
    qrels = pd.read_csv(qrels_file, header=None, names=["query_id", "doc_id", "relevance"])
    return queries, qrels

def generate_run_file(queries, ranking_function, output_file="runfile.txt"):
    """
    Generate a run file for queries using the ranking function.
    """
    run_file_entries = []

    for _, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        query_text = query_row["query_text"]

        # Retrieve documents using the ranking function
        try:
            retrieved_docs = ranking_function(query_text)
        except Exception as e:
            logger.error(f"Error retrieving documents for query {query_id}: {e}")
            continue

        # Format the retrieved documents into the run file format
        for rank, doc_id in enumerate(retrieved_docs, start=1):
            run_file_entries.append(
                f"{query_id} Q0 {doc_id} {rank} {1.0 / rank} system_name"
            )  # Example scoring: inverse rank

    # Save run file
    with open(output_file, "w") as f:
        f.write("\n".join(run_file_entries))
    
    logger.info(f"Run file generated and saved to {output_file}")


def compute_precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Compute Precision@k.
    """
    retrieved_at_k = retrieved_docs[:k]
    relevant_retrieved = [doc for doc in retrieved_at_k if doc in relevant_docs]
    return len(relevant_retrieved) / k

def compute_dcg_at_k(retrieved_docs, relevant_scores, k):
    """
    Compute Discounted Cumulative Gain (DCG) at rank k.
    """
    dcg = 0.0
    for i, doc in enumerate(retrieved_docs[:k]):
        relevance = relevant_scores.get(doc, 0)
        dcg += (2 ** relevance - 1) / np.log2(i + 2)  # Log base 2
    return dcg

def compute_ndcg_at_k(retrieved_docs, relevant_scores, k):
    """
    Compute Normalized Discounted Cumulative Gain (nDCG) at rank k.
    """
    dcg_at_k = compute_dcg_at_k(retrieved_docs, relevant_scores, k)
    ideal_relevance = sorted(relevant_scores.values(), reverse=True)
    ideal_dcg_at_k = sum((2 ** rel - 1) / np.log2(i + 2) for i, rel in enumerate(ideal_relevance[:k]))
    return dcg_at_k / ideal_dcg_at_k if ideal_dcg_at_k > 0 else 0.0

def ranking_function_with_search(query_text, top_k=100):
    """
    Ranking function that integrates with the `search` function to retrieve documents.
    """
    try:
        # Get search results
        results = search(query_text, top_k=top_k)

        # Extract document IDs (advertiser_id)
        doc_ids = [
            result["metadata"]["metadata"].get("advertiser_id", "")
            for result in results
            if "metadata" in result and "metadata" in result["metadata"]
        ]

        # Return the list of document IDs
        return doc_ids
    except Exception as e:
        logger.error(f"Error in ranking function: {e}")
        return []

def evaluate_ranking(queries, qrels, ranking_function, ks=[5, 10, 20]):
    """
    Evaluate ranking methods using Precision@k and nDCG@k.
    """
    results = []
    for _, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        query_text = query_row["query_text"]

        # Get relevant documents and their relevance scores for this query
        relevant_docs = qrels[qrels["query_id"] == query_id]
        relevant_docs_set = set(relevant_docs["doc_id"])
        relevant_scores = {row["doc_id"]: row["relevance"] for _, row in relevant_docs.iterrows()}

        # Retrieve documents using the ranking function
        retrieved_docs = ranking_function(query_text)

        # Compute metrics at each k
        for k in ks:
            precision = compute_precision_at_k(retrieved_docs, relevant_docs_set, k)
            ndcg = compute_ndcg_at_k(retrieved_docs, relevant_scores, k)
            results.append({
                "query_id": query_id,
                "k": k,
                "precision": precision,
                "ndcg": ndcg
            })

    return pd.DataFrame(results)

def search(query_text, top_k=100):
    """
    Search for documents using the backend's query processing service.
    This function should return a list of result dictionaries, where each result
    contains a 'metadata' key with additional information.
    """
    # Dynamically resolve index directory
    index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../index"))

    # Check if index directory exists
    if not os.path.exists(index_dir):
        raise FileNotFoundError(f"Index directory not found: {index_dir}")

    query_service = QueryService(
        model_name="distiluse-base-multilingual-cased-v1", index_dir=index_dir
    )

    logger.info(f"Query: {query_text}")
    results = query_service.search(query=query_text, top_k=top_k)
    return results

def aggregate_metrics(evaluation_results):
    """
    Aggregate precision and nDCG metrics over all queries for each rank depth.
    """
    aggregated_metrics = evaluation_results.groupby("k").mean()[["precision", "ndcg"]].reset_index()
    logger.info("Aggregated Metrics:")
    logger.info(aggregated_metrics)
    return aggregated_metrics

# Load data
queries_file = "/Users/avishekanand/Projects/search-engine/data/eval-data/queries.csv"
qrels_file = "/Users/avishekanand/Projects/search-engine/data/eval-data/qrels.csv"
queries, qrels = load_queries_and_qrels(queries_file, qrels_file)

# Generate run file
logger.info("Generating run file...")
generate_run_file(queries, ranking_function_with_search, output_file="runfile.txt")

# Evaluate
logger.info("Evaluating ranking function...")
evaluation_results = evaluate_ranking(queries, qrels, ranking_function_with_search, ks=[5, 10, 20])

# Display individual results
print(evaluation_results)

# Aggregate metrics
aggregated_metrics = aggregate_metrics(evaluation_results)

# Save evaluation results
evaluation_results.to_csv("evaluation_results.csv", index=False)
aggregated_metrics.to_csv("aggregated_metrics.csv", index=False)

logger.info("Evaluation complete. Results saved to evaluation_results.csv and aggregated_metrics.csv")