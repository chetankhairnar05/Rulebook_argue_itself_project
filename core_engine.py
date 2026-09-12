import os
import json
import warnings
import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
import hashlib

warnings.filterwarnings("ignore", message="Direct use of automatic function calling")

def get_file_hash(filepath):
    """Generate an MD5 hash of the file to detect changes."""
    with open(filepath, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash

client = genai.Client()
# Use your current working model
MODEL_ID = "gemini-3.5-flash-lite"  # or gemini-2.0-flash / gemini-3.1-flash-lite depending on your quota

chroma_client = chromadb.PersistentClient(path="./chroma_db")


def ingest_rulebook(filepath):
    """Ingests the rulebook ONLY if the file has changed since last ingestion."""
    current_hash = get_file_hash(filepath)
    
    # Check if collection exists and matches our current file hash
    try:
        collection = chroma_client.get_collection(name="rulebook")
        if collection.metadata and collection.metadata.get("file_hash") == current_hash:
            print("Rulebook unchanged. Using cached ChromaDB collection.")
            return False  # Skip ingestion
            
        print("Rulebook changes detected. Rebuilding index...")
        chroma_client.delete_collection(name="rulebook")
    except chromadb.errors.InvalidCollectionException:
        print("No existing database found. Building fresh index...")
    except Exception:
        try:
            chroma_client.delete_collection(name="rulebook")
        except:
            pass

    # Create new collection AND save the hash in its metadata
    collection = chroma_client.create_collection(
        name="rulebook", 
        metadata={"file_hash": current_hash}
    )
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 20]
    
    docs, ids, metadatas = [], [], []
    for i, chunk in enumerate(chunks):
        docs.append(chunk)
        ids.append(f"chunk_{i}")
        metadatas.append({"source": filepath, "chunk_index": i})
        
    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    print(f"Ingested {len(chunks)} chunks into persistent ChromaDB.")


def query_rulebook(user_query):
    collection = chroma_client.get_collection(name="rulebook")
    
    # Retrieve top 6 most relevant chunks
    results = collection.query(query_texts=[user_query], n_results=6)
    retrieved_chunks = results['documents'][0]
    retrieved_metadata = results['metadatas'][0]
    
    passages_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        passages_text += f"--- Passage {i} ---\n{chunk}\n\n"
        
    # MASTER PROMPT: Strictly grounded adjudicator
    # MASTER PROMPT: Strictly grounded adjudicator
    system_instruction = (
        "You are a strict, neutral academic regulations auditor. "
        "Your task is to classify a query against rulebook passages into EXACTLY one of three states: "
        "CONSENSUS, UNANSWERABLE, or CONTRADICTION. "
        "You must base your decision SOLELY on the provided text. You are permitted to recognize direct synonyms "
        "and read Markdown tables, but you are FORBIDDEN from making logical leaps, negative inferences, or assumptions."
    )

    prompt = f"""
Query: "{user_query}"

Corpus Passages:
{passages_text}

Follow these steps in your evaluation:

STEP 1: RELEVANCE & DIRECT ENTAILMENT TEST (Check for UNANSWERABLE)
Does the text EXPLICITLY answer the exact question?
- "Negative inference" is UNANSWERABLE. (e.g., Text says "tardiness > 15 mins is absence". Query asks about 10 mins. Answer is UNANSWERABLE).
- "Unlisted exceptions" are UNANSWERABLE. (e.g., Text covers medical absence. Query asks about a wedding. Answer is UNANSWERABLE).
- If no passage directly states the answer, set state to "UNANSWERABLE" and leave claims empty.

STEP 2: CONTRADICTION DETECTION (Check ALL passages)
If the text does contain the answer, you MUST check ALL retrieved passages for conflicts before declaring CONSENSUS.
- If Passage A establishes a strict rule (e.g., "no exceptions", "no committee has authority"), and Passage B overrides, waives, or breaks that rule, you MUST set state to "CONTRADICTION".
- If multiple passages give different answers to the same question, set state to "CONTRADICTION".
- Only if the text answers the question AND no passages conflict, set state to "CONSENSUS".

Output strictly valid JSON matching this schema:
{{
    "state": "CONSENSUS" | "UNANSWERABLE" | "CONTRADICTION",
    "exact_quote_found": "<exact text from passage or null>",
    "message": "<Concise explanation of verdict>",
    "claims": [
        {{"passage_index": <int>, "claim": "<specific direct statement from text>"}}
    ]
}}
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
            response_mime_type="application/json"
        )
    )
    
    try:
        output = json.loads(response.text.strip())
    except Exception:
        return {"state": "UNANSWERABLE", "message": "Failed to parse system response.", "claims": []}
        
    formatted_claims = []
    for c in output.get("claims", []):
        idx = c.get("passage_index")
        if idx is not None and 0 <= idx < len(retrieved_chunks):
            formatted_claims.append({
                "claim": c["claim"],
                "source": retrieved_metadata[idx],
                "raw_text": retrieved_chunks[idx]
            })
            
    output["claims"] = formatted_claims
    return output