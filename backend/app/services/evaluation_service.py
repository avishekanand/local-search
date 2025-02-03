import requests
import re

class EvaluationService:
    """
    This service evaluates SER on queries using a locally hosted Ollama LLM to evaluate the relevance
    of a search result.
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
        Extracts and returns only the content inside the <Relevance> tag.
        
        :param text: The full response text from the LLM.
        :return: The text inside the <Relevance> tag, or the full text if no tag is found.
        """
        # Use a regular expression to search for content within <Relevance>...</Relevance>
        match = re.search(r"<Relevance>(.*?)</Relevance>", text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # If the tag isn't found, return the full response trimmed.
            return text.strip()

    def evaluate(self, query: str, title: str, description: str) -> str:
        """
        Build a prompt from the input parameters and query the LLM.
        
        :param query: The search query.
        :param title: The title of the search result.
        :param description: The description of the search result.
        :return: The evaluated relevance string extracted from within the <Relevance> tag.
                 Expected outputs are: 'relevant', 'partially relevant', or 'not relevant'.
        """
        prompt = (
            f"Query: {query}\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            "Evaluate the relevance of this search result with respect to the query. "
            "Return one of the following labels exactly: 'relevant', 'partially relevant', or 'not relevant' "
            "inside tags <Relevance>."
        )
        
        # Build the payload following the documentation.
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # We want a single JSON response.
            "options": {
                "temperature": 0.0  # Deterministic output.
            }
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            if response.status_code != 200:
                return f"Error: status code {response.status_code}"
            data = response.json()
            full_response = data.get("response", "").strip()
            # Extract only the value within the <Relevance> tag.
            return self.extract_relevance(full_response)
        except Exception as e:
            return f"Exception: {e}"