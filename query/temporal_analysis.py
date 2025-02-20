import re
import csv
import editdistance
from collections import defaultdict
import matplotlib.pyplot as plt

# 1) Pattern to extract `'jw_jobname': 'VALUE'` from the searchParam block
JW_JOBNAME_PATTERN = re.compile(r"'jw_jobname':\s*'([^']*)'")

# 2) Fallback pattern to extract `jw_jobname=VALUE` from the event_url (e.g. `...?jw_jobname=Minijob&...`)
JW_JOBNAME_URL_PATTERN = re.compile(r"jw_jobname=([^&]+)")

def parse_line(line):
    """
    Try to extract jw_jobname from:
      1) 'jw_jobname': 'VALUE'
         (searchParam style)
      2) jw_jobname=VALUE
         (event_url style)
    Returns the jobname as a string or None if not found.
    """
    # First attempt: searchParam style
    match = JW_JOBNAME_PATTERN.search(line)
    if match:
        return match.group(1).strip()

    # Second attempt: event_url fallback
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
            autocomplete_queries.add(line.strip())  # Remove whitespace/newlines
    return autocomplete_queries

def is_typed_query(query, autocomplete_queries):
    """
    Determine if a query is typed.
    A query is typed if it is NOT in the autocomplete_queries set.
    """
    return query not in autocomplete_queries

def find_closest_match(query, autocomplete_queries):
    """
    Find the closest matching autocomplete query for a given typed query.
    Uses Levenshtein (edit) distance to determine similarity.
    """
    if not autocomplete_queries:
        return None, float("inf")  # No valid match

    closest_match = min(autocomplete_queries, key=lambda x: editdistance.eval(query, x))
    edit_distance = editdistance.eval(query, closest_match)
    
    return closest_match, edit_distance

def main():
    # Adjust your file paths as needed
    input_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/Querydata/20250112/searchType1.txt"
    autocomplete_queries_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/typeahead_suggestions.txt"
    output_typed_queries_not_found = "typed_queries_not_found.csv"

    # Load autocomplete queries from file
    autocomplete_queries = load_autocomplete_queries(autocomplete_queries_file)

    # Frequencies for ALL queries
    query_frequencies = defaultdict(int)
    total_queries = 0  # counts every parsed query

    # Unique query grouping (for canonicalization)
    unique_query_groups = set()

    # Sets for typed/autocomplete queries
    all_queries_typed = set()
    all_queries_autocomplete = set()

    # Read input file
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Search(" not in line:
                continue

            jw_jobname = parse_line(line)
            if jw_jobname:
                total_queries += 1
                query_frequencies[jw_jobname] += 1

                # Classification
                if is_typed_query(jw_jobname, autocomplete_queries):
                    all_queries_typed.add(jw_jobname)
                else:
                    all_queries_autocomplete.add(jw_jobname)

    # === 1) Analyze Typed Queries (Top 100) ===
    top_100_typed = sorted(
        [(q, query_frequencies[q]) for q in all_queries_typed],
        key=lambda x: x[1],
        reverse=True
    )[:100]

    closest_match_results = []
    not_close_typed_queries = []

    for query, freq in top_100_typed:
        closest_match, edit_dist = find_closest_match(query, autocomplete_queries)
        closest_match_results.append((query, closest_match, edit_dist, freq))
        
        # Grouping similar queries as a unique query if edit distance ≤ 6
        if edit_dist <= 6:
            unique_query_groups.add(closest_match)
        else:
            unique_query_groups.add(query)
            not_close_typed_queries.append((query, freq))

    # === 2) Print Top 100 Frequent Typed Queries with Closest Match (Formatted) ===
    print("\n=== 2) Top 100 Frequent Typed Queries with Closest Autocomplete Match ===")
    header = f"{'Typed Query'.ljust(30)} | {'Closest Match'.ljust(30)} | {'Edit Distance'.ljust(12)} | {'Frequency'.ljust(8)}"
    print(header)
    print("=" * len(header))

    for query, match, dist, freq in closest_match_results:
        print(f"{query.ljust(30)} | {match.ljust(30)} | {str(dist).ljust(12)} | {str(freq).ljust(8)}")

    # === 3) Print Top 10 Typed Queries NOT Close (Edit Distance ≥ 6) ===
    not_close_typed_queries_sorted = sorted(
        not_close_typed_queries,
        key=lambda x: x[1],
        reverse=True
    )[:10]

    print("\n=== 3) Top 10 Frequent Typed Queries NOT Close to Any Autocomplete Query ===")
    header = f"{'Typed Query'.ljust(30)} | {'Frequency'.ljust(8)}"
    print(header)
    print("=" * len(header))

    for query, freq in not_close_typed_queries_sorted:
        print(f"{query.ljust(30)} | {str(freq).ljust(8)}")

    # === 4) Unique Query Count (After Canonicalization) ===
    print("\n=== 4) Total Unique Queries After Canonicalization ===")
    print(f"Unique query count: {len(unique_query_groups)}")

    # === 5) Output Typed Queries NOT Found in Autocomplete List to CSV ===
    with open(output_typed_queries_not_found, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["query", "frequency"])  
        for query, freq in not_close_typed_queries_sorted:
            csv_writer.writerow([query, freq])

    print(f"\nTyped queries NOT close to any autocomplete list written to: {output_typed_queries_not_found}")

    # === 6) Plot Top 20 Query Distribution ===
    top_20 = sorted(query_frequencies.items(), key=lambda x: x[1], reverse=True)[:20]
    top_queries = [q for q, f in top_20]
    top_frequencies = [f for q, f in top_20]
    
    plt.figure(figsize=(10, 8))
    plt.barh(top_queries, top_frequencies, color="skyblue")
    plt.xlabel("Frequency")
    plt.title("Top 20 Query Distribution")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()


