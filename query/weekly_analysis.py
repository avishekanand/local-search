import os
import re
import csv
import editdistance
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import date, timedelta

# 1) Regex for searchParam style: 'jw_jobname': 'Value'
JW_JOBNAME_PATTERN = re.compile(r"'jw_jobname':\s*'([^']*)'")

# 2) Regex for event_url style: jw_jobname=Value
JW_JOBNAME_URL_PATTERN = re.compile(r"jw_jobname=([^&]+)")

def parse_line(line):
    """
    Try to extract jw_jobname from:
      1) 'jw_jobname': 'VALUE'    (searchParam style)
      2) jw_jobname=VALUE        (event_url style)
    Returns the jobname as a string or None if not found.
    """
    # First attempt: 'jw_jobname': 'SomeValue'
    match = JW_JOBNAME_PATTERN.search(line)
    if match:
        return match.group(1).strip()

    # Second attempt: ?jw_jobname=SomeValue&...
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
        return None, float("inf")  # No valid match in the set

    closest_match = min(
        autocomplete_queries,
        key=lambda x: editdistance.eval(query, x)
    )
    edit_distance = editdistance.eval(query, closest_match)
    return closest_match, edit_distance

def main():
    # -------------------------------------------------------------------------
    # 1) Define the date range and subfolder naming convention
    #    e.g. /.../Querydata/20250110/searchType1.txt
    # -------------------------------------------------------------------------
    start_date = date(2025, 1, 10)
    end_date   = date(2025, 1, 17)

    data_dir = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/Querydata"

    # Hard-coded path to the autocomplete queries file
    autocomplete_queries_file = (
        "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/"
        "JOBWARE/DATA/typeahead_suggestions.txt"
    )
    
    # CSV to store typed queries that don't match any autocomplete suggestion
    output_typed_queries_not_found = "typed_queries_not_found.csv"

    filenames = []
    current = start_date
    while current <= end_date:
        folder_name = current.strftime('%Y%m%d')  # e.g. "20250110"
        full_path = os.path.join(data_dir, folder_name, "searchType1.txt")
        
        if os.path.exists(full_path):
            filenames.append(full_path)
        else:
            print(f"WARNING: File not found: {full_path}")
        
        current += timedelta(days=1)

    # -------------------------------------------------------------------------
    # 2) Load autocomplete queries
    # -------------------------------------------------------------------------
    autocomplete_queries = load_autocomplete_queries(autocomplete_queries_file)

    # Data structures for combined analysis over the date range
    query_frequencies = defaultdict(int)
    total_queries = 0

    # For typed vs. autocomplete classification
    all_queries_typed = set()
    all_queries_autocomplete = set()

    # For canonicalization grouping
    unique_query_groups = set()

    # -------------------------------------------------------------------------
    # 3) Parse each discovered file
    # -------------------------------------------------------------------------
    for input_file in filenames:
        print(f"Processing {input_file}...")
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if "Search(" not in line:
                    continue
                jw_jobname = parse_line(line)
                if jw_jobname:
                    total_queries += 1
                    query_frequencies[jw_jobname] += 1

                    # Typed vs. autocomplete classification
                    if is_typed_query(jw_jobname, autocomplete_queries):
                        all_queries_typed.add(jw_jobname)
                    else:
                        all_queries_autocomplete.add(jw_jobname)

    # -------------------------------------------------------------------------
    # 4) Analyze top 100 typed queries
    # -------------------------------------------------------------------------
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

        # If within distance <= 6, treat as "close"
        if edit_dist <= 6:
            unique_query_groups.add(closest_match)
        else:
            unique_query_groups.add(query)
            not_close_typed_queries.append((query, freq))

    # -------------------------------------------------------------------------
    # 5) Print analysis results
    # -------------------------------------------------------------------------
    print("\n=== 1) Top 100 Frequent Typed Queries (All Days) with Closest Autocomplete Match ===")
    header = f"{'Typed Query'.ljust(30)} | {'Closest Match'.ljust(30)} | {'Edit Dist'.ljust(10)} | {'Freq'.ljust(8)}"
    print(header)
    print("=" * len(header))
    for query, match, dist, freq in closest_match_results:
        print(f"{query.ljust(30)} | {match.ljust(30)} | {str(dist).ljust(10)} | {str(freq).ljust(8)}")

    # Sort typed queries that are not close
    not_close_typed_queries_sorted = sorted(
        not_close_typed_queries,
        key=lambda x: x[1],
        reverse=True
    )[:10]

    print("\n=== 2) Top 10 Frequent Typed Queries NOT Close (Edit Dist ≥ 7) ===")
    header = f"{'Typed Query'.ljust(30)} | {'Frequency'.ljust(8)}"
    print(header)
    print("=" * len(header))
    for query, freq in not_close_typed_queries_sorted:
        print(f"{query.ljust(30)} | {str(freq).ljust(8)}")

    print("\n=== 3) Total Unique Queries After Canonicalization ===")
    print(f"Unique query count: {len(unique_query_groups)}")

    print("\n=== 4) Total Queries (All Days Combined) ===")
    print(f"Total queries processed: {total_queries}")
    print(f"Total typed queries (unique): {len(all_queries_typed)}")
    print(f"Total autocomplete queries (unique): {len(all_queries_autocomplete)}")

    # Write typed queries not found in autocomplete to CSV
    with open(output_typed_queries_not_found, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["query", "frequency"])
        for query, freq in not_close_typed_queries_sorted:
            csv_writer.writerow([query, freq])

    print(f"\nTyped queries NOT close to any autocomplete list are in: {output_typed_queries_not_found}")

    # -------------------------------------------------------------------------
    # 6) Plot the TOP 20 Query Distribution
    # -------------------------------------------------------------------------
    top_20 = sorted(query_frequencies.items(), key=lambda x: x[1], reverse=True)[:20]
    top_queries_20 = [q for q, f in top_20]
    top_frequencies_20 = [f for q, f in top_20]

    plt.figure(figsize=(10, 8))
    plt.barh(top_queries_20, top_frequencies_20, color="skyblue")
    plt.xlabel("Frequency")
    plt.title("Top 20 Query Distribution (All Days)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    # === 7) Plot the TOP 100 Query Distribution (Landscape Orientation) ===
    top_100 = sorted(query_frequencies.items(), key=lambda x: x[1], reverse=True)[:100]
    top_queries_100 = [q for q, f in top_100]
    top_frequencies_100 = [f for q, f in top_100]

    plt.figure(figsize=(16, 8))  # Wider figure for 100 queries
    # Plot queries on the x-axis:
    plt.bar(top_queries_100, top_frequencies_100, color="skyblue")

    # Adjusting font sizes to ~0.75 of normal
    plt.xticks(rotation=90, fontsize=8)  # Rotate labels if they’re long
    plt.yticks(fontsize=8)
    plt.xlabel("Queries", fontsize=9)
    plt.ylabel("Frequency", fontsize=9)
    plt.title("Top 100 Query Distribution (All Days)", fontsize=10)

    plt.tight_layout()  # Ensures labels and ticks fit nicely
    plt.show()

if __name__ == "__main__":
    main()