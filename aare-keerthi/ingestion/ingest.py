# ingestion/ingest.py
import os
from pathlib import Path
import re
import json
import pandas as pd
from tqdm import tqdm
from uuid import uuid4
from transformers import AutoTokenizer

# CONFIG
REPO_DIR = Path("data/raw")
OUT_PATH = Path("data/processed_chunks.parquet")
TOKENIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # tokenizer only
MIN_TOKENS = 300
MAX_TOKENS = 512
OVERLAP_TOKENS = 64

# Role mapping heuristic (extend this to suit your repo)
ROLE_MAP = {
    'finance': ['finance','qtr','quarter','balance','income','financial'],
    'marketing': ['market','campaign','brand','marketing','seo','ad'],
    'hr': ['hr','employee','payroll','handbook','policy'],
    'engineering': ['architecture','design','api','engineering','tech','architecture'],
    'general': ['handbook','policy','company','general']
}

def guess_role_from_path(path_str):
    s = path_str.lower()
    for role, keywords in ROLE_MAP.items():
        for kw in keywords:
            if kw in s:
                return role
    return 'general'

def clean_text(text):
    # normalize newlines, remove repeated whitespace, strip BOM
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\uFEFF', '', text)  # BOM
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def parse_markdown(path: Path):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except:
        text = path.read_text(encoding='latin-1', errors='ignore')
    return clean_text(text)

def parse_csv(path: Path):
    df = pd.read_csv(path, dtype=str, encoding='utf-8', engine='python').fillna('')
    # concat text columns into a single long string per file
    texts = []
    for _, row in df.iterrows():
        texts.append(' '.join(row.astype(str).tolist()))
    return clean_text("\n".join(texts))

def tokenize_and_chunk(text, tokenizer):
    """
    Tokenize the input text and return a list of chunk strings.
    We temporarily set tokenizer.model_max_length to a large value to avoid the
    "longer than max length" warning because we are chunking manually.
    """
    # avoid warning about sequence > model_max_length
    try:
        original_max = tokenizer.model_max_length
    except Exception:
        original_max = None
    try:
        tokenizer.model_max_length = int(1e12)
    except Exception:
        pass

    # encode entire text into token ids
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    # restore original value
    if original_max is not None:
        try:
            tokenizer.model_max_length = original_max
        except Exception:
            pass

    chunks = []
    i = 0
    n = len(token_ids)
    if n == 0:
        return []

    while i < n:
        j = min(i + MAX_TOKENS, n)
        chunk_ids = token_ids[i:j]

        # If the final chunk would be too short, merge it into previous
        if len(chunk_ids) < MIN_TOKENS and j == n and chunks:
            prev_ids = chunks.pop()['ids']
            merged_ids = prev_ids + chunk_ids
            chunks.append({'ids': merged_ids})
            break

        chunks.append({'ids': chunk_ids})
        i += (MAX_TOKENS - OVERLAP_TOKENS)

    # Decode token ids into text for each chunk
    texts = []
    for c in chunks:
        try:
            chunk_text = tokenizer.decode(c['ids'], clean_up_tokenization_spaces=True)
        except Exception:
            # fallback: convert ids to tokens then join (works for both fast & slow tokenizers)
            tokens = [tokenizer.convert_ids_to_tokens(tid) for tid in c['ids']]
            chunk_text = tokenizer.convert_tokens_to_string(tokens)
        texts.append(chunk_text)

    return texts

def main():
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
    rows = []
    for root, _, files in os.walk(REPO_DIR):
        for f in files:
            if not (f.endswith('.md') or f.endswith('.markdown') or f.endswith('.csv') or f.endswith('.txt')):
                continue
            p = Path(root) / f
            rel = str(p.relative_to(REPO_DIR))
            dept = guess_role_from_path(rel)
            if f.endswith('.csv'):
                text = parse_csv(p)
            else:
                text = parse_markdown(p)
            if not text:
                continue
            chunk_texts = tokenize_and_chunk(text, tokenizer)
            for seq, chunk in enumerate(chunk_texts):
                allowed_roles = [dept, 'c_level'] if dept != 'general' else ['employees','general','c_level']
                rows.append({
                    'id': str(uuid4()),
                    'source_file': rel,
                    'department': dept,
                    'allowed_roles': allowed_roles,
                    'chunk_seq': seq,
                    'text': chunk
                })
    if rows:
        df = pd.DataFrame(rows)
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUT_PATH, index=False)
        print(f"Saved {len(df)} chunks to {OUT_PATH}")
    else:
        print("No documents found or no chunks created.")

if __name__ == "__main__":
    main()