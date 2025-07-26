import streamlit as st
import logging
from graph_rag_service import graph_rag_service 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title="MOSDAC Graph RAG Assistant", layout="wide")

st.title("🛰️ MOSDAC Graph RAG Assistant")
st.markdown("""
Welcome to the MOSDAC Graph RAG Assistant! Ask questions about MOSDAC spacecraft, instruments, data products, and more.
The assistant uses a Neo4j knowledge graph and OpenAI's LLMs to provide accurate answers.
""")


if not graph_rag_service.graph or not graph_rag_service.qa_chain:
    st.error("RAG service failed to initialize. Please check the backend logs (`graph_rag_service.py`) for connection or API key issues.")
    st.stop()


query = st.text_input("Enter your query here:", placeholder="e.g., What is the design life of INSAT-3D?")

if st.button("Get Answer"):
    if query:
        with st.spinner("Thinking... Generating Cypher and fetching data..."):
            response = graph_rag_service.query_graph(query)

        st.subheader("Answer:")
        if response.get("result"):
            st.success(response["result"])
        else:
            st.warning("Could not generate a direct answer. Please try rephrasing your query or check intermediate steps for errors.")

        st.subheader("Intermediate Steps (for Debugging/Transparency):")
        intermediate_steps = response.get("intermediate_steps", [])
        if intermediate_steps:
            for step in intermediate_steps:
                if "query" in step:
                    st.code(f"Generated Cypher:\n{step['query']}", language="cypher")
                if "context" in step:
                    st.json({"Full Context from DB": step["context"]})
                if "answer" in step:
                    st.info(f"LLM's Answer Generation Input: {step['answer']}")
        else:
            st.info("No intermediate steps available or an error occurred before steps could be generated.")
    else:
        st.warning("Please enter a query to get an answer.")

st.markdown("---")
st.markdown("Built with Neo4j, OpenAI, and Streamlit.")