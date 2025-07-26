import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv




NEO4J_URI = os.getenv("NEO4J_URI") 
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")       
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")               

CYPHER_QUERIES_FOLDER = 'neo4j_cypher_queries'

class Neo4jUploader:
    """
    A class to connect to Neo4j and upload Cypher queries from files.
    """
    def __init__(self, uri, username, password):
        self.driver = None
        if not password:
            print("Error: NEO4J_PASSWORD environment variable is not set. Cannot connect to Neo4j.")
            return

        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            print(f"Successfully connected to Neo4j at {uri}")
        except Exception as e:
            print(f"Failed to connect to Neo4j at {uri}. Please ensure the database is running and accessible.")
            print(f"Error: {e}")
            self.driver = None
        except Exception as e:
            print(f"An unexpected error occurred during Neo4j connection: {e}")
            self.driver = None

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed.")

    def upload_cypher_file(self, file_path):
        """
        Reads a Cypher query from a file and executes it in Neo4j.
        """
        if not self.driver:
            print(f"Skipping upload for '{file_path}': No active Neo4j connection.")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cypher_query = f.read()

            if not cypher_query.strip():
                print(f"Warning: '{file_path}' is empty or contains only whitespace. Skipping.")
                return True # Consider it processed successfully if empty

            with self.driver.session() as session:
                session.run(cypher_query)
            print(f"Successfully uploaded '{file_path}' to Neo4j.")
            return True
        except FileNotFoundError:
            print(f"Error: File not found at '{file_path}'.")
            return False
        except Exception as e:
            print(f"Error uploading '{file_path}' to Neo4j: {e}")
            return False

def upload_all_cypher_queries(cypher_folder, uri, username, password):
    """
    Iterates through all .cypher files in a folder and uploads them to Neo4j.
    """
    uploader = Neo4jUploader(uri, username, password)

    if not uploader.driver:
        print("Aborting upload process due to failed Neo4j connection.")
        return

    if not os.path.exists(cypher_folder):
        print(f"Error: Cypher queries folder '{cypher_folder}' does not exist.")
        uploader.close()
        return

    uploaded_count = 0
    failed_count = 0
    skipped_count = 0

    print(f"\n--- Starting upload of Cypher queries from '{cypher_folder}' ---")

    for filename in os.listdir(cypher_folder):
        if filename.endswith(".cypher"):
            file_path = os.path.join(cypher_folder, filename)
            print(f"Attempting to upload: '{filename}'")
            if uploader.upload_cypher_file(file_path):
                uploaded_count += 1
            else:
                failed_count += 1
        else:
            print(f"Skipping non-.cypher file: '{filename}'")
            skipped_count += 1

    uploader.close()
    print("\n--- Upload Process Complete ---")
    print(f"Total files uploaded: {uploaded_count}")
    print(f"Total files failed: {failed_count}")
    print(f"Total files skipped: {skipped_count}")
    print("Please check your Neo4j browser or logs for verification.")


if __name__ == "__main__":
    upload_all_cypher_queries(CYPHER_QUERIES_FOLDER, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)