import requests
import json
import yaml
import os

# Path to your config file (adjust the path if necessary)
CONFIG_PATH = os.path.abspath("config/config.yml")

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)

# Load configuration
config = load_config()

# Get the Ollama endpoint and model from the configuration.
ollama_config = config.get("ollama", {})
ollama_endpoint = ollama_config.get("endpoint", "http://localhost:11434/api/generate")
ollama_model = ollama_config.get("model", "deepseek-r1:8b")

print(f"Ollama Endpoint: {ollama_endpoint}")
print(f"Ollama Model: {ollama_model}")

def test_ollama():
    # Create a simple prompt for testing
    prompt = "Test prompt: Is this german advertisement with the title 'Teamleiter' and description 'Übernahme beim Kunden und langfristiger Einsatz sind möglich- Sie haben Freude daran, unser Team bei der Digitalisierung von physischen\nDokumenten zu unterstützen- Zusätzlich übernehmen Sie die Verantwortung für die Datenerfassung auf Digitaler Ebene mittels geeigneter Softwarelösungen- Darüber hinaus überwachen Sie die Kennzahlen und sind für das Terminmanagement zuständig- Ihr weiteres Aufgabenspektrum umfassen sowohl die Mitarbeiterführung als auch Die Projektleitung- Diverse Tätigkeiten in den Bereichen Materialeinsatz und PersonalressourcenStehen dabei im Fokus- Zudem sind Sie für die Sicherstellung eines effizienten Ablaufes desagesgeschäftes verantwortlich- In enger Abstimmung mit der Produktionsleitung haben Sie die Möglichkeit, Ihre Ideen bei der kontinuierlichen Optimierung, Gestaltung und Weiterentwicklung der Prozesse einzubringen' relevant to the query 'it manager'? Report your answer clearly as RELEVANT, NOT RELEVANT, or IRRELEVANT. the explanation can be written in the tags <explanation> and </explanation>"
    
    # Build the payload following the documentation:
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,  # we want the full response in one JSON object
        "options": {
            "temperature": 0.0  # if you need to control temperature, set it here
        }
    }
    
    try:
        response = requests.post(ollama_endpoint, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print("Ollama response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_ollama()