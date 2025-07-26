import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts.prompt import PromptTemplate


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- LLM Configuration ---
CYPHER_LLM_MODEL = "gpt-4o-mini"
QA_LLM_MODEL = "gpt-4o"

# --- Cypher Generation Prompt Template ---
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:
# How many spacecraft are there?
MATCH (s:Spacecraft) RETURN count(s) AS totalSpacecraft

# What instruments does INSAT-3D carry?
MATCH (s:Spacecraft {{name:"INSAT-3D"}})-[:CARRIES_INSTRUMENT]->(i:Instrument) RETURN i.name AS instrumentName

# Which data products are processed by ISRO?
MATCH (dp:DataProduct)-[:PROCESSED_BY]->(o:Organization {{name:"ISRO"}}) RETURN dp.name AS dataProductName

# What is the launch mass of INSAT-3D?
MATCH (s:Spacecraft {{name:"INSAT-3D"}}) RETURN s.launch_mass_kg AS launchMass

The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

class GraphRAGService:
    """
    Manages the GraphCypherQAChain for RAG, assuming a connected Neo4jGraph is provided.
    """
    def __init__(self, neo4j_graph: Neo4jGraph):
        self.graph = neo4j_graph
        self.qa_chain = None
        self._initialize_qa_chain()

    def _initialize_qa_chain(self):
        """
        Initializes the GraphCypherQAChain.
        """
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY environment variable is not set. Cannot initialize LLM chains.")
            return
        if not self.graph:
            logger.warning("Neo4jGraph not provided. Cannot initialize QA chain.")
            return

        try:
            cypher_llm = ChatOpenAI(temperature=0, model=CYPHER_LLM_MODEL, openai_api_key=OPENAI_API_KEY)
            qa_llm = ChatOpenAI(temperature=0, model=QA_LLM_MODEL, openai_api_key=OPENAI_API_KEY)

            self.qa_chain = GraphCypherQAChain.from_llm(
                graph=self.graph,
                cypher_llm=cypher_llm,
                qa_llm=qa_llm,
                cypher_prompt=CYPHER_GENERATION_PROMPT,
                verbose=True, 
                return_intermediate_steps=True, 
                allow_dangerous_requests=True 
            )
            logger.info("GraphCypherQAChain initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing GraphCypherQAChain: {e}")
            self.qa_chain = None

    def query_graph(self, query_text: str) -> dict:
        """
        Executes a natural language query against the graph RAG chain.
        Returns a dictionary containing the result and intermediate steps.
        """
        if not self.qa_chain:
            logger.error("QA Chain is not initialized. Cannot process query.")
            return {"result": "Error: RAG service not ready. Please check logs.", "intermediate_steps": []}

        try:
            logger.info(f"Processing query: '{query_text}'")
            result = self.qa_chain.invoke({"query": query_text})
            logger.info(f"Query processed. Result: {result.get('result')}")
            return result
        except Exception as e:
            logger.error(f"Error during graph query for '{query_text}': {e}")
            return {"result": f"An error occurred while querying the graph: {e}", "intermediate_steps": []}

# Global instance of the service (initially None)
graph_rag_service = None

if __name__ == "__main__":
    print("--- Initializing Neo4j Graph Connection ---")
    neo4j_graph_instance = None

    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        logger.error("Neo4j connection details (URI, Username, Password) are not fully set in environment variables. Please check your .env file.")
    else:
        try:
            # Test basic connectivity first
            temp_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
            temp_driver.verify_connectivity()
            temp_driver.close() # Close temporary driver

            neo4j_graph_instance = Neo4jGraph(
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
                enhanced_schema=True
            )
            neo4j_graph_instance.refresh_schema()
            logger.info("Successfully created and refreshed Neo4jGraph instance.")
            logger.info(f"Neo4j Graph Schema: \n{neo4j_graph_instance.schema}")

        except Exception as e:
            logger.error(f"An unexpected error occurred during Neo4jGraph initialization: {e}")

 
    if neo4j_graph_instance:
        graph_rag_service = GraphRAGService(neo4j_graph_instance)
    else:
        logger.critical("GraphRAGService cannot be initialized due to Neo4j connection failure.")

    # --- Testing Graph RAG Service ---
    print("\n--- Testing Graph RAG Service ---")
    if graph_rag_service and graph_rag_service.qa_chain:
        test_query = "What is the launch mass of INSAT-3D?"
        response = graph_rag_service.query_graph(test_query)
        print("\n--- Test Query Result ---")
        print(f"Query: {test_query}")
        print(f"Result: {response.get('result')}")
        print(f"Intermediate Steps: {response.get('intermediate_steps')}")

        test_query_2 = "Tell me about the instruments on INSAT-3D."
        response_2 = graph_rag_service.query_graph(test_query_2)
        print("\n--- Test Query 2 Result ---")
        print(f"Query: {test_query_2}")
        print(f"Result: {response_2.get('result')}")
        print(f"Intermediate Steps: {response_2.get('intermediate_steps')}")
    else:
        print("Graph RAG Service failed to initialize. Check previous error messages.")

