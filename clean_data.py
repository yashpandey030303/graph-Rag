import os
import re

def extract_main_description_by_structural_markers(
    source_directory: str, 
    output_directory: str, 
    start_heading_pattern: str = r'^#\s(.+?)\n', 
    # This pattern now combines finding an H2+ heading OR a list item with a link.
    # It marks the end of the main description.
    # The \s* now correctly handles all Unicode whitespace thanks to re.U flag.
    end_marker_pattern: str = r'(?:^\s*##+\s.*?\n)|(?:^\s*[\*\-]\s*\[(?:!\[.*?\]\(.*?\)|.*?\]\(.*?\)).*?\n)'
) -> None:
    """
    Reads markdown files from a source directory and extracts the main description block.
    This block starts from the first H1 heading in the document and ends just before
    the first subsequent H2 (##) or higher heading, OR the first list item containing a link.

    Args:
        source_directory (str): Path to the directory containing the original markdown files.
        output_directory (str): Path to the directory where cleaned markdown files will be saved.
        start_heading_pattern (str): Regex pattern for the H1 heading that marks the start
                                     of the desired content block.
        end_marker_pattern (str): Regex pattern for the *first* structural element (H2+ heading
                                  or list item with link) that marks the end of the main description.
    """
    os.makedirs(output_directory, exist_ok=True)
    print(f"Starting general description extraction from '{source_directory}'...")

    for filename in os.listdir(source_directory):
        if filename.endswith(".md"):
            source_filepath = os.path.join(source_directory, filename)
            output_filepath = os.path.join(output_directory, filename)

            print(f"\nProcessing '{filename}'...")

            try:
                with open(source_filepath, 'r', encoding='utf-8') as f_read:
                    full_content = f_read.read()

                # Define common regex flags:
                # re.M (MULTILINE): Makes ^ and $ match start/end of lines.
                # re.S (DOTALL): Makes . match newlines as well (important for .*?).
                # re.U (UNICODE): Makes \s match all Unicode whitespace (CRUCIAL for non-breaking spaces).
                regex_flags = re.M | re.S | re.U

                # Step 1: Find the first H1 heading in the *entire document*.
                h1_match = re.search(start_heading_pattern, full_content, regex_flags)

                if not h1_match:
                    print(f"  Warning: No main H1 heading found (pattern: '{start_heading_pattern}') in '{filename}'. Skipping.")
                    continue

                # The content we want starts from the beginning of this H1 line.
                content_start_index = h1_match.start()
                
                # We need to search for the end marker *after* the H1 heading has finished.
                # This prevents accidentally matching an end marker within the H1 line itself.
                search_after_h1_index = h1_match.end() 
                
                # Search for the end marker pattern from this point onwards.
                # The regex_flags (especially re.U) are now applied here.
                end_match = re.search(end_marker_pattern, full_content[search_after_h1_index:], regex_flags)

                if end_match:
                    # Calculate the global end index.
                    # This is the start of the matched end_marker_pattern in the original content.
                    global_end_index = search_after_h1_index + end_match.start()
                    
                    # Extract content from the H1 start up to (but not including) the end marker.
                    extracted_content = full_content[content_start_index:global_end_index].strip()
                else:
                    # If no general end marker is found, take everything from H1 to the end of the file.
                    print(f"  Warning: No general end marker found after H1 in '{filename}'. Saving from H1 to end of file.")
                    extracted_content = full_content[content_start_index:].strip()

                # Save the extracted content if it's not empty
                if extracted_content:
                    with open(output_filepath, 'w', encoding='utf-8') as f_write:
                        f_write.write(extracted_content)
                    print(f"  Extracted description block saved to '{output_filepath}'")
                else:
                    print(f"  No extractable content found in '{filename}' using the defined patterns. Skipping.")

            except FileNotFoundError:
                print(f"  Error: File not found at '{source_filepath}'.")
            except Exception as e:
                print(f"  An unexpected error occurred while processing '{filename}': {e}")

    print("\nExtraction process completed. Check the 'extracted_descriptions_general' folder.")

if __name__ == "__main__":
    SOURCE_DIR = "cleaned_scraped_pages" 
    OUTPUT_DIR = "extracted_data" 

    extract_main_description_by_structural_markers(
        SOURCE_DIR, 
        OUTPUT_DIR,
        start_heading_pattern=r'^#\s.+?\n', 
        # This combines:
        # 1. Start of a new H2/H3/etc. heading (##, ###, etc.)
        # 2. Start of an unordered list item that contains a Markdown link (e.g., * [Text](URL) or * ![Alt](URL))
        end_marker_pattern=r'(?:^\s*##+\s.*?\n)|(?:^\s*[\*\-]\s*\[(?:!\[.*?\]\(.*?\)|.*?\]\(.*?\)).*?\n)'
    )