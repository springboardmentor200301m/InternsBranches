import json

def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

tagged_chunks = load_jsonl("processed/chunks_tagged.jsonl")

print("Total tagged chunks:", len(tagged_chunks))

print("\nSample Chunk Text:\n", tagged_chunks[0]["text"][:300])

print("\nSample Metadata:\n", {
    "department": tagged_chunks[0]["department"],
    "file_name": tagged_chunks[0]["file_name"],
    "accessible_roles": tagged_chunks[0]["accessible_roles"]
    
})
