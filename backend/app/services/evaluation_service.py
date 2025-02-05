# import requests
# import re

# class EvaluationService:
#     """
#     This service evaluates SER on queries using a locally hosted Ollama LLM to evaluate the relevance
#     of a search result.
#     """
#     def __init__(self, endpoint: str, model: str):
#         """
#         Initialize the service with the Ollama endpoint URL and model name.
        
#         :param endpoint: The URL for the Ollama LLM API endpoint.
#         :param model: The model name to use in the request.
#         """
#         self.endpoint = endpoint
#         self.model = model

#     def extract_relevance(self, text: str) -> str:
#         """
#         Extracts and returns only the content inside the <Relevance> tag.
        
#         :param text: The full response text from the LLM.
#         :return: The text inside the <Relevance> tag, or the full text if no tag is found.
#         """
#         # Use a regular expression to search for content within <Relevance>...</Relevance>
#         match = re.search(r"<Relevance>(.*?)</Relevance>", text, re.IGNORECASE | re.DOTALL)
#         if match:
#             return match.group(1).strip()
#         else:
#             # If the tag isn't found, return the full response trimmed.
#             return text.strip()

#     def evaluate(self, query: str, title: str, description: str) -> str:
#         """
#         Build a prompt from the input parameters and query the LLM.
        
#         :param query: The search query.
#         :param title: The title of the search result.
#         :param description: The description of the search result.
#         :return: The evaluated relevance string extracted from within the <Relevance> tag.
#                  Expected outputs are: 'relevant', 'partially relevant', or 'not relevant'.
#         """
#         prompt = (
#             f"Query: {query}\n"
#             f"Title: {title}\n"
#             f"Description: {description}\n\n"
#             "Evaluate the relevance of this search result with respect to the query. "
#             "Return one of the following labels exactly: 'relevant', 'partially relevant', or 'not relevant' "
#             "inside tags <Relevance>."
#         )
        
#         # Build the payload following the documentation.
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "stream": False,  # We want a single JSON response.
#             "options": {
#                 "temperature": 0.0  # Deterministic output.
#             }
#         }
        
#         try:
#             response = requests.post(self.endpoint, json=payload)
#             if response.status_code != 200:
#                 return f"Error: status code {response.status_code}"
#             data = response.json()
#             full_response = data.get("response", "").strip()
#             # Extract only the value within the <Relevance> tag.
#             return self.extract_relevance(full_response)
#         except Exception as e:
#             return f"Exception: {e}"

import requests
import re

class EvaluationService:
    """
    This service evaluates search engine results using a locally hosted Ollama LLM.
    It supports both single and batched evaluations.
    """
    def __init__(self, endpoint: str, model: str):
        """
        Initialize the service with the Ollama endpoint URL and model name.
        
        :param endpoint: The URL for the Ollama LLM API endpoint.
        :param model: The model name to use in the request.
        """
        self.endpoint = endpoint
        self.model = model

    def extract_relevance(self, text: str) -> str:
        """
        Extracts and returns only the content inside the <Relevance> tag from a single evaluation.
        
        :param text: The full response text from the LLM.
        :return: The text inside the <Relevance> tag, or the full text if no tag is found.
        """
        match = re.search(r"<Relevance>(.*?)</Relevance>", text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return text.strip()

    def evaluate(self, query: str, title: str, description: str) -> str:
        """
        Evaluate a single result document.
        
        :param query: The search query.
        :param title: The title of the search result.
        :param description: The description of the search result.
        :return: The evaluated relevance label extracted from the response.
        """
        prompt = (
            f"Query: {query}\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            "Evaluate the relevance of this search result with respect to the query. "
            "Return one of the following labels exactly: 'relevant', 'partially relevant', or 'not relevant' "
            "inside tags <Relevance>."
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        try:
            response = requests.post(self.endpoint, json=payload)
            if response.status_code != 200:
                return f"Error: status code {response.status_code}"
            data = response.json()
            full_response = data.get("response", "").strip()
            return self.extract_relevance(full_response)
        except Exception as e:
            return f"Exception: {e}"

    def evaluate_batch(self, query: str, results: list, top_k: int) -> list:
        """
        Evaluate a batch of top-k search results for a given query.
        
        :param query: The search query.
        :param results: A list of dictionaries where each dictionary contains the keys "title" and "description".
        :param top_k: The number of top results to include in the prompt.
        :return: A list of evaluated relevance labels (as strings) in the same order as the input results.
        """
        # Limit to the first top_k results.
        batch_results = results[:top_k]
        
        # Build a combined prompt.
        prompt_lines = [f"Query: {query}\n",
                        f"Below are the top {top_k} search results. For each result, evaluate its relevance with respect to the query. "
                        "Return each label (exactly one of 'relevant', 'partially relevant', or 'not relevant') enclosed in <Relevance> tags.\n"]
        
        for idx, doc in enumerate(batch_results, start=1):
            title = doc.get("title", "")
            description = doc.get("description", "")
            prompt_lines.append(f"Result {idx}:\nTitle: {title}\nDescription: {description}\n")
        
        prompt_lines.append("Provide your answers in order as:\n<Result1>: <Relevance>label</Relevance>\n<Result2>: <Relevance>label</Relevance>\n... etc.")
        full_prompt = "\n".join(prompt_lines)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            if response.status_code != 200:
                return [f"Error: status code {response.status_code}"]
            data = response.json()
            full_response = data.get("response", "").strip()
            
            # Use a regex to extract all labels in order.
            # The regex will find all occurrences of <Relevance>...</Relevance>.
            labels = re.findall(r"<Relevance>(.*?)</Relevance>", full_response, re.IGNORECASE | re.DOTALL)
            # Return only as many labels as requested (top_k).
            if len(labels) < top_k:
                # Optionally, you could log a warning if fewer labels than expected.
                return labels
            return labels[:top_k]
        except Exception as e:
            return [f"Exception: {e}"]