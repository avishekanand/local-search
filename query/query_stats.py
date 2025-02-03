import re
import csv
from collections import defaultdict

# Pattern to extract 'jw_jobname' from a line containing the Search(...) text.
JW_JOBNAME_PATTERN = re.compile(r"'jw_jobname':\s*'([^']*)'")

def parse_line(line):
    """
    Extract 'jw_jobname' from a line containing the Search(...) text.
    Returns the jobname as a string or None if not found.
    """
    match = JW_JOBNAME_PATTERN.search(line)
    if match:
        return match.group(1).strip()
    return None

def main():
    input_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/searchType1.txt"
    output_csv = "queries_frequency.csv"  # CSV file output

    # Frequencies for ALL queries
    query_frequencies = defaultdict(int)

    # For stats across entire dataset
    total_queries = 0  # counts every parsed query

    # Sets for unique typed vs. autocomplete queries
    all_queries_typed = set()
    all_queries_autocomplete = set()

    # Counters for total typed vs. autocomplete occurrences
    typed_count_total = 0
    autocomplete_count_total = 0

    # Read the file line by line
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Search(" not in line:
                continue  # skip irrelevant lines

            jw_jobname = parse_line(line)
            if jw_jobname:
                total_queries += 1
                query_frequencies[jw_jobname] += 1

                # Classification logic: if the first character is lowercase, consider it "typed"
                if jw_jobname[0].islower():
                    all_queries_typed.add(jw_jobname)
                    typed_count_total += 1
                else:
                    all_queries_autocomplete.add(jw_jobname)
                    autocomplete_count_total += 1

    # 1) Sort ALL queries by frequency, then slice for top 20
    popular_queries_sorted = sorted(
        query_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_20 = popular_queries_sorted[:20]

    # === 1) Print TOP 20 queries (+ frequency) only ===
    print("=== 1) TOP 20 Queries by Frequency ===")
    for query, freq in top_20:
        print(f"{query!r} => {freq}")

    # === 2) Unique Query Counts (Entire Dataset) ===
    print("\n=== 2) Unique Query Counts (ALL) ===")
    print(f"Unique typed queries: {len(all_queries_typed)}")
    print(f"Unique autocomplete queries: {len(all_queries_autocomplete)}")

    # === 3) Total Query Counts (ALL) ===
    print("\n=== 3) Total Number of Queries (ALL) ===")
    print(f"Total queries processed: {total_queries}")
    print(f"Total typed queries: {typed_count_total}")
    print(f"Total autocomplete queries: {autocomplete_count_total}")

    # === 4) Duplicate Queries (ONLY in the TOP 20) ===
    print("\n=== 4) Duplicate Queries Among TOP 20 ===")
    duplicates_top_20 = [(q, f) for (q, f) in top_20 if f > 1]
    if duplicates_top_20:
        print("Found duplicate queries (frequency > 1) in the top 20:")
        for q, freq in duplicates_top_20:
            print(f"  {q!r} => frequency: {freq}")
    else:
        print("No duplicates in the top 20 queries.")

    # === 5) Top 10 Frequent Typed Queries ===
    typed_queries_with_freq = [(q, query_frequencies[q]) for q in all_queries_typed]
    typed_queries_sorted = sorted(
        typed_queries_with_freq,
        key=lambda x: x[1],
        reverse=True
    )
    top_10_typed = typed_queries_sorted[:10]
    print("\n=== 5) Top 10 Frequent Typed Queries ===")
    for query, freq in top_10_typed:
        print(f"{query!r} => {freq}")

    # === 6) Output All Query Frequencies to CSV ===
    # The CSV file will have two columns: query, frequency.
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["query", "frequency"])  # CSV header
        # Sort queries by frequency (descending order) for output
        for query, freq in sorted(query_frequencies.items(), key=lambda x: x[1], reverse=True):
            csv_writer.writerow([query, freq])
    print(f"\nCSV output written to: {output_csv}")

if __name__ == "__main__":
    main()