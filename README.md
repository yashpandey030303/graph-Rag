# CosmoQuery (MOSDAC Graph RAG Assistant-Initial prototype)

A powerful application that provides natural language querying capabilities over scientific and technical data from the MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) website using Graph RAG (Retrieval Augmented Generation) architecture.

## 🚀 Features

- **Data Ingestion**: Processes raw Markdown files (scraped MOSDAC data) to extract structured information
- **Named Entity Recognition (NER) & Relationship Extraction**: Utilizes LLM (GPT-4o Mini) with few-shot prompting to identify key entities and relationships
- **Neo4j Knowledge Graph Population**: Generates Cypher queries to efficiently load extracted data into a Neo4j graph database
- **Graph RAG Querying**: Uses LangChain's GraphCypherQAChain to translate natural language questions into Cypher queries
- **Streamlit Web Interface**: Provides an intuitive and interactive web application
- **Environment Management**: Utilizes `uv` for fast and reproducible dependency management
- **Secure Configuration**: Uses `.env` files for secure credential management

## 🛠️ Technologies Used

### Backend
- Python 3.9+
- Neo4j (Graph Database)
- OpenAI API (GPT-4o, GPT-4o Mini)
- LangChain (for RAG orchestration)
- neo4j (Python Driver for Neo4j)
- langchain-neo4j (LangChain integration for Neo4j)
- langchain-openai (LangChain integration for OpenAI)
- python-dotenv (for environment variable management)

### Frontend
- Streamlit

### Dependency Management
- uv (fast Python package installer and resolver)

## 🏗️ System Design

The MOSDAC Graph RAG Assistant follows a multi-stage architecture that combines traditional NLP techniques with modern graph databases and large language models:

### Architecture Overview

![System Architecture](https://github.com/oms0401/Graph-Rag/blob/e8054233d327f845e1c1774c3902ea3cb5e911ef/graphrag%20system%20design.png)

```
Raw Markdown Data → NER & Relationship Extraction → Cypher Generation → Neo4j Graph Database → Graph RAG Querying → Natural Language Response
```

### Components

1. **Data Ingestion Layer**: Processes raw scraped MOSDAC markdown files and prepares them for entity extraction
2. **Entity Extraction Engine**: Uses GPT-4o Mini with few-shot prompting to identify entities (Spacecraft, Instruments, Data Products, Organizations) and their relationships
3. **Graph Database Layer**: Neo4j stores the extracted knowledge as a connected graph with nodes and relationships
4. **RAG Query Engine**: LangChain's GraphCypherQAChain orchestrates the translation of natural language queries to Cypher queries
5. **Response Generation**: GPT-4o synthesizes natural language answers from graph query results
6. **Web Interface**: Streamlit provides an intuitive frontend for user interactions

### Data Flow

1. **Preprocessing**: Clean markdown files are placed in the `mosdac_scraped_data` folder
2. **Entity Recognition**: `generate_cypher.py` processes each markdown file using LLM to extract structured entities and relationships
3. **Graph Population**: `upload_to_neo4j.py` executes generated Cypher queries to build the knowledge graph
4. **Query Processing**: User queries are converted to Cypher, executed against Neo4j, and results are synthesized into natural language responses
5. **Response Delivery**: Final answers are presented through the Streamlit web interface

This architecture enables efficient querying of complex scientific data while maintaining the flexibility to handle diverse question types and data structures.

## 📋 Prerequisites

Before you begin, ensure you have the following installed and set up:

### Python 3.9+
Download from [python.org](https://python.org)

### uv Package Manager
**Recommended installation via pipx:**
```bash
pip install pipx
pipx ensurepath
pipx install uv
```

**Alternative installation:**
```bash
pip install uv
```

### Neo4j Database Instance

Choose one of the following options:

#### Option 1: Neo4j AuraDB (Cloud Service - Recommended)
1. Create a free instance at [console.neo4j.io](https://console.neo4j.io)
2. Note down your Bolt URI, Username (usually `neo4j`), and Password

#### Option 2: Neo4j Desktop (Local Application)
1. Download from [neo4j.com/download/neo4j-desktop](https://neo4j.com/download/neo4j-desktop)
2. Start a local database
3. Default Bolt URI: `bolt://localhost:7687`, username: `neo4j`

#### Option 3: Docker Container (Local)
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/password \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest
```

### OpenAI API Key
Obtain an API key from [platform.openai.com](https://platform.openai.com)

## 🔧 Setup & Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd mosdac_rag
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:

```env
# .env
NEO4J_URI="neo4j+s://your_aura_bolt_uri.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_neo4j_password"
OPENAI_API_KEY="sk-your_openai_api_key_here"
```

> **Important**: Replace the placeholder values with your actual credentials.

### 3. Install Dependencies

Ensure your `pyproject.toml` file contains:

```toml
[project]
name = "mosdac-rag"
version = "0.1.0"
description = "MOSDAC Graph RAG Application"
requires-python = ">=3.9"
dependencies = [
    "neo4j",
    "langchain-neo4j",
    "langchain-openai",
    "streamlit",
    "python-dotenv",
    "openai",
    "crawl4ai",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Generate and install dependencies:
```bash
# Generate requirements.txt with locked dependencies
uv pip compile pyproject.toml -o requirements.txt

# Install dependencies
uv pip install -r requirements.txt
```

### 4. Prepare Your Data
1. Create a folder named `mosdac_scraped_data` in your project root
2. Place all your clean, scraped MOSDAC website data (in Markdown format) into this folder

### 5. Extract Entities & Generate Cypher Queries
```bash
uv run python generate_cypher.py
```

This creates a `neo4j_cypher_queries` folder containing `.cypher` files for each Markdown input.

### 6. Populate Your Neo4j Database
```bash
uv run python upload_to_neo4j.py
```

This executes all `.cypher` files, populating your graph database.

## 🚀 Running the Application

Once your Neo4j database is populated:

```bash
uv run streamlit_app.py
```

The application will:
- Launch the Streamlit web interface
- Initialize the Neo4j Graph connection
- Set up the GraphCypherQAChain
- Open your web browser to the app interface

## 📁 Project Structure

```
mosdac_rag/
├── .env                          # Environment variables
├── pyproject.toml                # Project metadata and dependencies
├── requirements.txt              # Locked dependencies
├── mosdac_scraped_data/          # Input folder for raw markdown data
│   ├── insat_3d.md
│   ├── scatsat_1.md
│   └── ...
├── neo4j_cypher_queries/         # Output folder for generated Cypher queries
│   ├── insat_3d.cypher
│   ├── scatsat_1.cypher
│   └── ...
├── generate_cypher.py            # Script to perform NER and generate Cypher
├── upload_to_neo4j.py            # Script to upload Cypher queries to Neo4j
├── graph_rag_service.py          # Core RAG logic
└── streamlit_app.py              # Streamlit web interface
```

## 🔄 How It Works

1. **Data Preparation**: Raw Markdown data is cleaned and stored
2. **NER & Cypher Generation**: The `generate_cypher.py` script uses an LLM to identify entities and relationships, translating them into Neo4j Cypher MERGE statements
3. **Graph Population**: The `upload_to_neo4j.py` script executes Cypher statements, building a knowledge graph in Neo4j
4. **Graph RAG Querying**:
   - User submits a natural language query via Streamlit
   - LLM converts the query into a Cypher query based on the Neo4j graph schema
   - Cypher query is executed against the Neo4j database
   - Results are synthesized into a human-readable answer by another LLM
5. **Answer Display**: The natural language answer is displayed in the Streamlit interface

## 🐛 Troubleshooting

### Environment Variable Errors
- Ensure your `.env` file is in the same directory as the script
- Check for typos or extra spaces in your `.env` file
- Verify `load_dotenv()` is called at the beginning of your Python scripts

### Neo4j Connection Issues
- **AuraDB**: Ensure your database instance is in "Running" state in the Neo4j Aura Console
- **Credentials**: Double-check your `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD`
- **Network**: Test connectivity to Neo4j host on port 7687

### OpenAI API Issues
- Ensure `OPENAI_API_KEY` is correctly set in your `.env` file
- Check your OpenAI API key validity and sufficient credits

### Streamlit App Issues
- Check terminal output for Python tracebacks or error messages
- Ensure all dependencies are correctly installed
- Verify `graph_rag_service.py` imports and initializes without errors


### Components

1. **Data Ingestion Layer**: Processes raw scraped MOSDAC markdown files and prepares them for entity extraction
2. **Entity Extraction Engine**: Uses GPT-4o Mini with few-shot prompting to identify entities (Spacecraft, Instruments, Data Products, Organizations) and their relationships
3. **Graph Database Layer**: Neo4j stores the extracted knowledge as a connected graph with nodes and relationships
4. **RAG Query Engine**: LangChain's GraphCypherQAChain orchestrates the translation of natural language queries to Cypher queries
5. **Response Generation**: GPT-4o synthesizes natural language answers from graph query results
6. **Web Interface**: Streamlit provides an intuitive frontend for user interactions

### Data Flow

1. **Preprocessing**: Clean markdown files are placed in the `mosdac_scraped_data` folder
2. **Entity Recognition**: `generate_cypher.py` processes each markdown file using LLM to extract structured entities and relationships
3. **Graph Population**: `upload_to_neo4j.py` executes generated Cypher queries to build the knowledge graph
4. **Query Processing**: User queries are converted to Cypher, executed against Neo4j, and results are synthesized into natural language responses
5. **Response Delivery**: Final answers are presented through the Streamlit web interface

This architecture enables efficient querying of complex scientific data while maintaining the flexibility to handle diverse question types and data structures.

## 🔮 Future Enhancements

- **More Sophisticated Schema Mapping**: Implement advanced techniques for mapping extracted entities to graph schema
- **Error Handling & User Feedback**: Enhance error messages and user feedback
- **Data Updates**: Implement periodic graph updates with new MOSDAC data
- **Query History**: Add feature to store and display user query history
- **Multi-tenancy**: Support multiple users or data sources
- **Performance Monitoring**: Track LLM usage, query latency, and database performance
- **Advanced RAG Techniques**: Explore query rewriting, multi-hop reasoning, and vector embeddings
