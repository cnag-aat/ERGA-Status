import requests
import json

# Fetch the BioSample JSON
url = "https://www.ebi.ac.uk/biosamples/samples/SAMEA114349505"
response = requests.get(url)
data = response.json()

# Extract characteristics
characteristics = data.get("characteristics", {})

# Parse into a dict: key -> list of text values
parsed = {}
for key, values in characteristics.items():
    # Each value is a dict with 'text' and optional 'tag'
    parsed[key] = [v["text"] for v in values]

# Optional: flatten single-element lists to strings
parsed_flat = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

# Example: print
for k, v in parsed_flat.items():
    print(f"{k}: {v}")
