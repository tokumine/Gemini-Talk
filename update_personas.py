import os
import yaml

# The text to append
append_text = " NEVER output timestamps or other metadata. Just output the conversation. if you use lists, use numbered lists."

# Directory containing the YAML files
directory = "persona"

# Iterate through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".yaml"):
        filepath = os.path.join(directory, filename)
        
        # Read the YAML file
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        
        # Append the text to the persona field
        if 'persona' in data:
            data['persona'] += append_text
        
        # Write the updated data back to the file
        with open(filepath, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)

print("All YAML files in the 'persona' directory have been updated.")