import json

with open("data/processed_chunks_with_metadata.json", "r") as f:
    chunks = json.load(f)

sample = chunks[0]

print("Sample Chunk\n")
for k, v in sample.items():
    if k == "content":
        print(f"{k}: {v[:300]}...")
    else:
        print(f"{k}: {v}")
