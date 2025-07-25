import json

with open("terraform_output.json") as f:
    data = json.load(f)

with open(".env", "w") as f:
    for key, val in data.items():
        env_key = key.upper()
        env_value = val["value"]
        f.write(f"{env_key}={env_value}\n")

print(".env file created successfully.")
