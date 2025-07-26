import asyncio
import os
import re
from urllib.parse import urlparse 
from crawl4ai import AsyncWebCrawler

# --- Helper Function to Create a Simple Filename from a URL ---
def get_simple_filename_from_url(url: str, max_length: int = 100) -> str:
    """
    Extracts the last segment of a URL's path and sanitizes it for use as a filename.
    Example: https://mosdac.gov.in/insat-3dr becomes insat-3dr.md
    Example: https://example.com/products/category/item-name/ becomes item-name.md
    Example: https://example.com/ (homepage) becomes example_com.md
    """
    parsed_url = urlparse(url)
    path_segments = [s for s in parsed_url.path.split('/') if s]

    if path_segments:
        
        filename_base = path_segments[-1]
    else:

        filename_base = parsed_url.netloc.replace('.', '_').replace('-', '_') 


    filename_safe = re.sub(r'[^\w\-\._]', '', filename_base)


    filename_safe = filename_safe.strip('_.')

 
    if not filename_safe:
        filename_safe = "untitled_page"

    max_base_length = max_length - len(".md")
    if len(filename_safe) > max_base_length:
        filename_safe = filename_safe[:max_base_length] 

    return filename_safe + ".md"

async def main():

    async with AsyncWebCrawler() as crawler:
        print("Web Scraper Ready!")
        print("Enter a URL to scrape, or type 'exit' to quit.")

        
        while True:
            # --- 1. Prompt the user for the URL ---
            target_url = input("\nEnter URL: ")
            
            
            if target_url.lower().strip() == 'exit':
                print("Exiting scraper. Goodbye!")
                break

           
            if not target_url.strip():
                print("No URL provided. Please enter a URL or 'exit'.")
                continue 

            print(f"Attempting to scrape: {target_url}")
            

            result = await crawler.arun(url=target_url)


            if result.success and result.markdown:
                markdown_content = None
                

                if hasattr(result.markdown, 'raw_markdown') and result.markdown.raw_markdown:
                    markdown_content = result.markdown.raw_markdown
                elif isinstance(result.markdown, str) and result.markdown.strip():
                    markdown_content = result.markdown
                
               
                if markdown_content:
                    
                    output_filename = get_simple_filename_from_url(target_url)
                    
                   
                    output_directory = "scraped_pages"
                  
                    os.makedirs(output_directory, exist_ok=True)

                    
                    filepath = os.path.join(output_directory, output_filename)


                    try:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(markdown_content)
                        print(f"Markdown content successfully saved to: {filepath}")
                    except IOError as e:

                        print(f"Error saving markdown to file: {e}")
                else:
                    print(f"No valid markdown content found for {target_url}.")
            else:

                print(f"Crawl failed for {target_url}.")
                if result and result.error_message: 
                    print(f"Error: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())