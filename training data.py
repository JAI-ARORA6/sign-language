import os
from string import ascii_uppercase

base = "dataSet/trainingData"

os.makedirs(base, exist_ok=True)

# Create '0' folder
os.makedirs(os.path.join(base, "0"), exist_ok=True)

# Create A-Z folders
for letter in ascii_uppercase:
    os.makedirs(os.path.join(base, letter), exist_ok=True)

print("Folders created successfully ✅")