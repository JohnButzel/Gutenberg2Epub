import subprocess
import os
import sys

def run_scraper(url):
    result = subprocess.run(["python", "gscraper.py", url], capture_output=True, text=True)
    output_directory = result.stdout.strip()
    return output_directory

def run_ebook_converter(html_directory):
    subprocess.run(["python", "converter.py", html_directory])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main_script.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    html_directory = run_scraper(url)
    run_ebook_converter(html_directory)
