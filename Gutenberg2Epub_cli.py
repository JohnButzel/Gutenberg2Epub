import argparse
import subprocess
import re
import os
import sys

def validate_url(url):
    # Validate the URL pattern
    valid_url_pattern = r'https://www\.projekt-gutenberg\.org/.+/.+/'
    if not re.match(valid_url_pattern, url):
        raise ValueError("Ungültiges URL-Format! Bitte geben Sie eine gültige Gutenberg-de-URL ein.")

def run_gscraper(url, output_directory):
    try:
        gscraper_script_path = "gScraper.py"  # Assuming gscraper.py is in the same directory

        result = subprocess.run(["python", gscraper_script_path, url, "-d", output_directory], capture_output=True, text=True, check=True)

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Scraping the book failed: {e.stderr}") from e
    except Exception as e:
        raise RuntimeError(f"An error occurred while scraping the book: {e}")

def run_converter(output_directory, cover_image_path, delete_cover):
    try:
        converter_script_path = "converter.py"  # Assuming converter.py is in the same directory

        args = ["-d", output_directory, "--deletedecover", str(delete_cover)]
        if cover_image_path:
            args.extend(["--addcover", cover_image_path])

        subprocess.run(["python", converter_script_path] + args, check=True)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Converting the book failed: {e.stderr}") from e
    except Exception as e:
        raise RuntimeError(f"An error occurred while converting the book: {e}")

def main():
    parser = argparse.ArgumentParser(description="Gutenberg2epub Command Line Tool")
    parser.add_argument("url", help="Gutenberg-de URL")
    parser.add_argument("-o", "--output", help="Output directory", default=os.getcwd())
    parser.add_argument("--cover", help="Path to a cover image file")
    parser.add_argument("--delete-cover", action="store_true", help="Remove cover image from the title page")

    args = parser.parse_args()

    try:
        validate_url(args.url)
        output_directory = run_gscraper(args.url, args.output)
        run_converter(output_directory, args.cover, args.delete_cover)
        print("Ebook conversion complete!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
