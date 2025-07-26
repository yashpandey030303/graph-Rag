import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FOLDER = 'extracted_data'  
OUTPUT_FOLDER = 'neo4j_cypher_queries' 
MODEL_NAME = 'gpt-4o-mini'


PROMPT_MESSAGES = [
    {
        "role": "system",
        "content": """You are an expert Knowledge Graph engineer. Your task is to extract all relevant entities and their relationships from the provided scientific and technical text. Then, translate these extractions directly into Neo4j Cypher queries for knowledge graph population.

Strictly adhere to the output format: Only provide the Cypher query. Do not include any conversational text, explanations, or thought processes in the final output.

Identify and Categorize Entities: Extract all named entities and categorize them into appropriate node labels (e.g., `Spacecraft`, `Instrument`, `Component`, `Technology`, `Location`, `Date`, `Organization`, `DataProduct`, `Parameter`, `Phenomenon`, `Property`, `Value`, `Unit`, `Orbit`, `MeasurementPoint`, `Application`). Invent new labels if necessary but keep them generalized.

Define Properties: For each entity, extract relevant properties (attributes) and assign them as key-value pairs on the node. Use meaningful property names. For numerical values with units, consider either:
    - Adding unit as a separate property (e.g., `value: 2000, unit: 'kg'`) or
    - If applicable, including the unit in the property name (e.g., `launch_mass_kg: 2000`).

Identify Relationships: Determine how entities connect and create directed relationships between them. Use descriptive relationship types (e.g., `HAS_INSTRUMENT`, `CARRIES_PAYLOAD`, `ORBITS_IN`, `HAS_PROPERTY`, `INCORPORATES_TECHNOLOGY`, `COOLED_BY`, `MAINTAINED_AT_TEMPERATURE`, `HAS_CHANNEL`, `DISTRIBUTED_BY`, `USED_FOR`).

Generate Cypher: Construct a single, cohesive Neo4j Cypher query using `MERGE` clauses for nodes (to prevent duplicates) and relationships. Ensure that unique identifiers (like `name`) are used for `MERGE`."""
    },
    {
        "role": "user",
        "content": """Input: "The INSAT-3D is a momentum-biased 3-axis stabilized spacecraft using star trackers for precise pointing control. The spacecraft has a launch mass of 2000 kg with a dry mass of 907 kg. The nominal design life is 7.7 years. It is in Geostationary orbit, altitude of ~35, 786 km, location at 82° East. The three-axis stabilized geostationary satellite carries two meteorological instruments: a six channel Imager and an IR Sounder. Along with the channels in Visible, Middle Infrared, Water Vapor and Thermal Infrared bands, the Imager includes a SWIR channel for wider applications. The Sounder will have eighteen narrow spectral channels in three IR bands in addition to a channel in visible band. It also has a Data Relay Transponder and Satellite based Search & Rescue Payload. A passive radiant cooler is used to cool the infrared detectors of imager and sounder instruments. The detectors temperature is maintained at 95 K (BOL) and 100 K (EOL). The passive cooler is also to maintain the sounder filter wheel temperature at 213 K."""
    },
    {
        "role": "assistant",
        "content": """```cypher
MERGE (s:Spacecraft {name: 'INSAT-3D'})
SET s.stabilization = 'momentum-biased 3-axis stabilized',
    s.pointing_control_system = 'star trackers',
    s.launch_mass_kg = 2000,
    s.dry_mass_kg = 907,
    s.design_life_years = 7.7,
    s.altitude_km = 35786,
    s.longitude_deg_east = 82;

MERGE (o:Orbit {name: 'Geostationary'}) MERGE (s)-[:ORBITS_IN]->(o);

MERGE (imager:Instrument {name: 'Imager', function: 'meteorological', channels_count: 6})
MERGE (sounder:Instrument {name: 'IR Sounder', function: 'meteorological', channels_count: 18})
MERGE (drt:Payload {name: 'Data Relay Transponder'})
MERGE (sarp:Payload {name: 'Satellite based Search & Rescue Payload'})

MERGE (s)-[:CARRIES_INSTRUMENT]->(imager)
MERGE (s)-[:CARRIES_INSTRUMENT]->(sounder)
MERGE (s)-[:CARRIES_PAYLOAD]->(drt)
MERGE (s)-[:CARRIES_PAYLOAD]->(sarp);

MERGE (im_vis:Channel {name: 'Visible'}) MERGE (imager)-[:HAS_CHANNEL]->(im_vis);
MERGE (im_midIR:Channel {name: 'Middle Infrared'}) MERGE (imager)-[:HAS_CHANNEL]->(im_midIR);
MERGE (im_wv:Channel {name: 'Water Vapor'}) MERGE (imager)-[:HAS_CHANNEL]->(im_wv);
MERGE (im_thIR:Channel {name: 'Thermal Infrared'}) MERGE (imager)-[:HAS_CHANNEL]->(im_thIR);
MERGE (im_swir:Channel {name: 'SWIR'}) MERGE (imager)-[:HAS_CHANNEL]->(im_swir);

MERGE (so_ir_bands:Channel {name: 'three IR bands', count: 3}) MERGE (sounder)-[:HAS_CHANNEL]->(so_ir_bands);
MERGE (so_vis_band:Channel {name: 'visible band'}) MERGE (sounder)-[:HAS_CHANNEL]->(so_vis_band);

MERGE (cooler:Component {name: 'passive radiant cooler', type: 'CoolingSystem'})
MERGE (detectors:Component {name: 'infrared detectors', type: 'Detector'})
MERGE (filter_wheel:Component {name: 'sounder filter wheel', type: 'FilterWheel'})

MERGE (imager)-[:HAS_COMPONENT]->(detectors)
MERGE (sounder)-[:HAS_COMPONENT]->(detectors)
MERGE (sounder)-[:HAS_COMPONENT]->(filter_wheel)
MERGE (detectors)-[:COOLED_BY]->(cooler);

MERGE (temp_95K:Temperature {value_kelvin: 95}) MERGE (bol:MeasurementPoint {name: 'BOL'})
MERGE (detectors)-[:MAINTAINED_AT_TEMPERATURE]->(temp_95K) MERGE (temp_95K)-[:AT_POINT]->(bol);

MERGE (temp_100K:Temperature {value_kelvin: 100}) MERGE (eol:MeasurementPoint {name: 'EOL'})
MERGE (detectors)-[:MAINTAINED_AT_TEMPERATURE]->(temp_100K) MERGE (temp_100K)-[:AT_POINT]->(eol);

MERGE (temp_213K:Temperature {value_kelvin: 213})
MERGE (cooler)-[:MAINTAINS_TEMPERATURE_OF]->(filter_wheel)
MERGE (filter_wheel)-[:MAINTAINED_AT_TEMPERATURE]->(temp_213K);
```"""
    },
    {
        "role": "user",
        "content": """Input: "SCATSAT-1 provided ocean surface wind vector data for the Bay of Bengal from March 1, 2024 to March 31, 2024. This Level-3 Binned Data is crucial for cyclone monitoring. Data processed at SAC."""
    },
    {
        "role": "assistant",
        "content": """```cypher
MERGE (s:Satellite {name: 'SCATSAT-1'})
MERGE (p:Parameter {name: 'ocean surface wind vector', type: 'Oceanographic'})
MERGE (l:Location {name: 'Bay of Bengal', type: 'Oceanic'})
MERGE (dps:Date {iso_value: '2024-03-01'})
MERGE (dpe:Date {iso_value: '2024-03-31'})
MERGE (dp:DataProduct {name: 'Level-3 Binned Data', level: 3, format: 'Binned'})
MERGE (app:Application {name: 'cyclone monitoring'})
MERGE (org:Organization {name: 'SAC'})

MERGE (s)-[:COLLECTS_PARAMETER]->(p)
MERGE (p)-[:COLLECTED_AT]->(l)
MERGE (p)-[:COLLECTED_FROM_DATE]->(dps)
MERGE (p)-[:COLLECTED_TO_DATE]->(dpe)
MERGE (s)-[:GENERATES_PRODUCT]->(dp)
MERGE (dp)-[:IS_USED_FOR]->(app)
MERGE (dp)-[:PROCESSED_BY]->(org);
```"""
    },
    {
        "role": "user",
        "content": """Input: "Remote sensing plays a crucial role in monitoring atmospheric aerosols. ISRO uses data from its satellites for studying aerosol optical depth. The data aids in climate modeling."""
    },
    {
        "role": "assistant",
        "content": """```cypher
MERGE (sm:Method {name: 'Remote sensing', type: 'Scientific'})
MERGE (phen:Phenomenon {name: 'atmospheric aerosols', type: 'Atmospheric'})
MERGE (org:Organization {name: 'ISRO'})
MERGE (sat_gen:Satellite {name: 'ISRO Satellites', type: 'Fleet'})
MERGE (param:Parameter {name: 'aerosol optical depth', type: 'Atmospheric'})
MERGE (app:Application {name: 'climate modeling'})

MERGE (sm)-[:USED_FOR_MONITORING]->(phen)
MERGE (org)-[:UTILIZES]->(sat_gen)
MERGE (sat_gen)-[:PROVIDES_DATA_FOR_STUDYING]->(param)
MERGE (org)-[:STUDIES]->(param)
MERGE (param)-[:AIDS_IN]->(app);
```"""
    }
]

def process_markdown_files(input_folder, output_folder, model_name):
    """
    Reads markdown files from an input folder, sends their content to an LLM for NER
    and Cypher generation, and saves the results to an output folder.
    """
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    print(f"Processing Markdown files from '{input_folder}'...")
    print(f"Generated Cypher queries will be saved to '{output_folder}'.")

    processed_count = 0
    skipped_count = 0
    error_count = 0

    for filename in os.listdir(input_folder):
        if filename.endswith(".md"):
            input_filepath = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".cypher"
            output_filepath = os.path.join(output_folder, output_filename)

            print(f"\n--- Processing '{filename}' ---")

            try:
                with open(input_filepath, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()


                messages_for_api = list(PROMPT_MESSAGES)
                
                messages_for_api.append({
                    "role": "user",
                    "content": f"Process the following input text and generate the Neo4j Cypher query:\n\n{markdown_content}"
                })

                print("Sending request to OpenAI API...")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_for_api,
                    temperature=0.1,  
                    max_tokens=2000,
                )

                cypher_query = response.choices[0].message.content.strip()

                
                if cypher_query.startswith("```cypher") and cypher_query.endswith("```"):
                    cypher_query = cypher_query[len("```cypher"):-len("```")].strip()
                elif cypher_query.startswith("```") and cypher_query.endswith("```"):
                    cypher_query = cypher_query[len("```"):-len("```")].strip()


                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(cypher_query)

                print(f"Successfully generated Cypher for '{filename}' and saved to '{output_filepath}'")
                processed_count += 1

            except openai.APIError as e:
                print(f"OpenAI API Error for '{filename}': {e}")
                error_count += 1
            except Exception as e:
                print(f"An unexpected error occurred while processing '{filename}': {e}")
                error_count += 1
        else:
            print(f"Skipping non-markdown file: '{filename}'")
            skipped_count += 1

    print("\n--- Processing Complete ---")
    print(f"Total files processed: {processed_count}")
    print(f"Total files skipped: {skipped_count}")
    print(f"Total files with errors: {error_count}")
    print("Please review the generated .cypher files in the output folder.")

# --- Run the processing ---
if __name__ == "__main__":


    process_markdown_files(INPUT_FOLDER, OUTPUT_FOLDER, MODEL_NAME)