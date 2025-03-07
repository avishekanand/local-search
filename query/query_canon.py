import os
import re
import editdistance
from collections import defaultdict
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util

# Pattern to extract 'jw_jobname': 'VALUE' from searchParam
JW_JOBNAME_PATTERN = re.compile(r"'jw_jobname':\s*'([^']*)'")
# Fallback pattern to extract jw_jobname=VALUE from event_url
JW_JOBNAME_URL_PATTERN = re.compile(r"jw_jobname=([^&]+)")

def parse_line(line):
    """
    Extract the query (jw_jobname) from a log line.
    Tries the searchParam style first; if that fails, tries the event_url style.
    """
    match = JW_JOBNAME_PATTERN.search(line)
    if match:
        return match.group(1).strip()
    fallback = JW_JOBNAME_URL_PATTERN.search(line)
    if fallback:
        return fallback.group(1).strip()
    return None

def load_autocomplete_queries(filepath):
    """
    Load known autocomplete queries from a file into a set.
    Each line in the file represents one autocomplete query.
    """
    autocomplete_queries = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            autocomplete_queries.add(line.strip())
    return autocomplete_queries

def is_typed_query(query, autocomplete_queries):
    """
    Determine if a query is typed.
    A query is typed if it is NOT in the autocomplete_queries set.
    """
    return query not in autocomplete_queries

def canonicalize_queries(filtered_queries, filtered_freq, model, threshold_cosine=0.8, threshold_edit=5):
    """
    Group semantically similar queries using embeddings and an edit distance filter.
    For each cluster, choose the canonical query (the one with highest frequency) and
    aggregate the frequencies of all queries in the cluster.
    
    Returns:
      canonical_frequencies: dict mapping canonical query -> aggregated frequency.
      canonical_mapping: dict mapping each original query -> canonical query.
      canonical_clusters: dict mapping canonical query -> list of original queries in the cluster.
    """
    # Compute embeddings for all filtered queries.
    embeddings = model.encode(filtered_queries, convert_to_tensor=True)
    
    canonical_mapping = {}
    canonical_frequencies = {}
    canonical_clusters = {}
    visited = set()
    clusters = []
    
    for i, q in enumerate(filtered_queries):
        if q in visited:
            continue
        cluster = [q]
        visited.add(q)
        for j, other in enumerate(filtered_queries):
            if other in visited:
                continue
            if editdistance.eval(q, other) <= threshold_edit:
                sim = util.cos_sim(embeddings[i], embeddings[j]).item()
                if sim >= threshold_cosine:
                    cluster.append(other)
                    visited.add(other)
        clusters.append(cluster)
    
    for cluster in clusters:
        canonical_label = max(cluster, key=lambda x: filtered_freq[x])
        total_freq = sum(filtered_freq[q] for q in cluster)
        canonical_frequencies[canonical_label] = total_freq
        canonical_clusters[canonical_label] = cluster
        for q in cluster:
            canonical_mapping[q] = canonical_label

    return canonical_frequencies, canonical_mapping, canonical_clusters

def main():
    # ----- Configuration -----
    input_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/Querydata/20250112/searchType1.txt"
    autocomplete_queries_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/typeahead_suggestions.txt"
    
    # ----- Step 1: Parse Query Log and Build Frequency Dictionary -----
    query_frequencies = defaultdict(int)
    total_queries = 0

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Search(" not in line:
                continue
            query = parse_line(line)
            if query:
                total_queries += 1
                query_frequencies[query] += 1

    print(f"Total queries processed: {total_queries}")
    print(f"Unique raw queries: {len(query_frequencies)}")
    
    # ----- Step 2: Filter to Only Queries with Frequency >= 2 -----
    filtered_freq = {q: freq for q, freq in query_frequencies.items() if freq >= 2}
    filtered_queries = list(filtered_freq.keys())
    print(f"Canonicalizing {len(filtered_queries)} queries with frequency >= 2...")

    # ----- Step 3: Canonicalize Queries -----
    model = SentenceTransformer('all-MiniLM-L6-v2')
    canonical_frequencies, canonical_mapping, canonical_clusters = canonicalize_queries(
        filtered_queries, filtered_freq, model, threshold_cosine=0.8, threshold_edit=5
    )
    
    # ----- Step 4: Filter Canonical Groups with Aggregate Frequency > 5 -----
    canonical_filtered = {q: freq for q, freq in canonical_frequencies.items() if freq > 5}

    # ----- Step 5: Print Canonicalized Queries with Color Coding -----
    # Use ANSI escape codes: red for groups with multiple queries, blue for single.
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

    print("\n=== Top Canonicalized Queries (Aggregate Frequency > 5) ===")
    sorted_canonical = sorted(canonical_filtered.items(), key=lambda x: x[1], reverse=True)
    for canon, freq in sorted_canonical:
        cluster = canonical_clusters.get(canon, [])
        if len(cluster) > 1:
            print(f"{RED}{canon!r} => {freq} (Group: {cluster}){RESET}")
        else:
            print(f"{BLUE}{canon!r} => {freq}{RESET}")

    # ----- Step 6: Plot Top 20 Canonicalized Query Distribution -----
    top_20_canonical = sorted(canonical_filtered.items(), key=lambda x: x[1], reverse=True)[:20]
    canonical_queries = [q for q, f in top_20_canonical]
    canonical_freqs = [f for q, f in top_20_canonical]
    
    # Color bars: red for multi-query groups, blue for single.
    bar_colors = []
    for q in canonical_queries:
        if len(canonical_clusters.get(q, [])) > 1:
            bar_colors.append("red")
        else:
            bar_colors.append("blue")
    
    plt.figure(figsize=(10, 8))
    plt.barh(canonical_queries, canonical_freqs, color=bar_colors)
    plt.xlabel("Aggregated Frequency")
    plt.title("Top 20 Canonicalized Query Distribution (Freq > 5)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()