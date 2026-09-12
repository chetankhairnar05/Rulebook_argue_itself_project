import streamlit as st
import json
import os
from core_engine import ingest_rulebook, query_rulebook

# Configure the page layout
st.set_page_config(page_title="The Rulebook That Argues With Itself", layout="wide")

# --- Session State Initialization ---
if "ingested" not in st.session_state:
    st.session_state.ingested = False
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# --- Sidebar: System Control & Test Cases ---
with st.sidebar:
    st.title("⚙️ System Control")
    if not st.session_state.ingested:
        if st.button("Ingest Rulebook (Persistent ChromaDB)"):
            with st.spinner("Chunking and indexing rulebook..."):
                if os.path.exists("data/rulebook.md"):
                    ingest_rulebook("data/rulebook.md")
                    st.session_state.ingested = True
                    st.success("Database built successfully!")
                else:
                    st.error("File not found at data/rulebook.md")
    else:
        st.success("📚 Rulebook is loaded into ChromaDB.")
        
    st.markdown("---")
    st.markdown("### 🧪 Run a Test Case")
    st.caption("Click a test case to populate the chat input.")
    
    try:
        with open("eval_set.json", "r") as f:
            test_cases = json.load(f)
            for i, tc in enumerate(test_cases):
                # When clicked, update the query and clear the old result to trigger a rerun
                if st.button(f"Test {i+1}: {tc['expected_state']}", help=tc['reasoning']):
                    st.session_state.last_query = tc['query']
                    st.session_state.last_result = None 
    except FileNotFoundError:
        st.warning("eval_set.json not found.")

# --- Main UI ---
st.title("⚖️ The Rulebook That Argues With Itself")
st.markdown("Ask a question. The system will either give a **clear answer**, admit **ignorance**, or catch a **contradiction**.")

# Chat Input
user_input = st.chat_input("Ask a question about university rules...")

if user_input:
    st.session_state.last_query = user_input
    st.session_state.last_result = None # Clear old result so AI runs again

# Render the response if we have an active query
if st.session_state.last_query:
    st.markdown(f"### **Question:** {st.session_state.last_query}")
    
    if not st.session_state.ingested:
        st.error("Please ingest the rulebook from the sidebar first.")
    else:
        # Only call the LLM if we haven't saved the result yet
        if st.session_state.last_result is None:
            with st.spinner("Retrieving clauses and cross-examining rules..."):
                st.session_state.last_result = query_rulebook(st.session_state.last_query)
                
        result = st.session_state.last_result
        
        # 1. State Visualization
        state = result.get("state", "UNANSWERABLE")
        
        if state == "CONSENSUS":
            st.success("✅ **CONSENSUS:** The rulebook is clear on this matter.")
        elif state == "UNANSWERABLE":
            st.warning("⚠️ **UNANSWERABLE:** The rulebook says nothing about this specific situation.")
        elif state == "CONTRADICTION":
            st.error("🚨 **CONTRADICTION DETECTED:** The rulebook says incompatible things.")
            
        # 2. LLM Reasoning / Final Answer
        st.markdown("#### The Verdict")
        st.write(result.get("message", "No reasoning provided."))
        
        # Display the exact quote if the LLM found one
        if result.get("exact_quote_found") and result["exact_quote_found"] != "null":
            st.info(f"**Anchoring Quote:** \"{result['exact_quote_found']}\"")
            
        st.markdown("---")
        
        # 3. Traceability Evidence (Expanders)
        if result.get("claims"):
            st.markdown("#### Traceability: The Exact Passages")
            st.caption("Every claim is backed by a specific passage. Expand to verify.")
            
            for i, claim in enumerate(result["claims"]):
                # Using the expander will no longer break the app!
                with st.expander(f"Citation {i+1}: {claim['claim'][:70]}..."):
                    st.markdown(f"**Extracted Rule:** {claim['claim']}")
                    st.markdown(f"**Source Document:** `{claim['source']['source']}` | **Chunk ID:** `{claim['source']['chunk_index']}`")
                    st.markdown("**Original Text Passage:**")
                    st.code(claim.get('raw_text', 'Raw text not returned.'), language="markdown")