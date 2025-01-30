import re

# Updated regex patterns based on your actual text structure
patterns = {
    "jw_jobname": r"'jw_jobname':\s*'([^']*)'",
    "piwik_time": r"piwik_time=['\"]([^'\"]+)['\"]",
    "piwik_visitor_id": r"piwik_visitor_id=['\"]([^'\"]+)['\"]",
    "piwik_user_opened_advertisement_list": r"piwik_user_opened_advertisement_list=\[([^\]]*)\]"
}

def parse_line(line):
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, line)
        if match:
            # Capture group 1
            extracted[key] = match.group(1).strip()
        else:
            extracted[key] = None

    # If the user_opened_advertisement_list is not empty, split on commas
    if extracted["piwik_user_opened_advertisement_list"]:
        # Example: '051209036', '051209036' => split by comma
        raw = extracted["piwik_user_opened_advertisement_list"]
        # Remove potential quotes/spaces
        ads = [x.strip().strip("'").strip('"') for x in raw.split(",")]
        # Filter out any empty strings
        extracted["piwik_user_opened_advertisement_list"] = [ad for ad in ads if ad]

    return extracted

if __name__ == "__main__":
    input_file = "/Users/avishekanand/Library/CloudStorage/Dropbox/CONSULTING/JOBWARE/DATA/searchType1.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Search(" in line:
                data = parse_line(line)
                print("Extracted Data:", data)