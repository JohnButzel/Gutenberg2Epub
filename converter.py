import os
import sys
from ebooklib import epub
from bs4 import BeautifulSoup
import imghdr
import re
import shutil
import argparse


def extract_metadata(soup, name, http_equiv=False):
    try:
        if http_equiv:
            return soup.find('meta', {'http-equiv': name})['content']
        else:
            return soup.find('meta', {'name': name})['content']
    except (TypeError, KeyError):
        return None
    
def add_cover_image_and_first_page(book, image_dir):
    cover_image_formats = ['jpg', 'jpeg', 'png']  # Supported image formats
    for image_format in cover_image_formats:
        cover_path = os.path.join(image_dir, f'cover.{image_format}')

        if os.path.exists(cover_path):
            img_media_type = 'image/jpeg' if image_format == 'jpg' or image_format == 'jpeg' else 'image/png'
            img_item = epub.EpubItem(file_name='images/cover.' + image_format, media_type=img_media_type, content=open(cover_path, 'rb').read())
            book.add_item(img_item)
            book.set_cover('images/cover.' + image_format, open(cover_path, 'rb').read(), create_page=False)

            # Create a new EpubHtml item for the cover page
            cover_page = epub.EpubHtml(title='Cover', file_name='cover.html', lang='en')
            cover_page.content = f'''
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Cover</title>
    </head>
    <body>
        <div>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                width="100%" height="100%" viewBox="0 0 380 600"
                preserveAspectRatio="none">
                <image xlink:href="images/cover.{image_format}"/>
            </svg>
        </div>
    </body>
</html>
'''
            book.add_item(cover_page)

            # Set the cover page as the first item in the spine
            book.spine.insert(0, cover_page)

            return  # Exit after adding the cover
    

def convert_to_epub(html_directory):
    # Read and parse the index.html file for metadata and table of contents
    index_path = os.path.join(html_directory, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as index_file:
        index_content = index_file.read()
    index_soup = BeautifulSoup(index_content, 'html.parser')

    author_name = extract_metadata(index_soup, 'author')
    book_title = extract_metadata(index_soup, 'title')
    book_publisher = extract_metadata(index_soup, 'publisher')
    book_lang = extract_metadata(index_soup, 'content-language', http_equiv=True)
    book_genre = extract_metadata(index_soup, 'type')
    book_translator = extract_metadata(index_soup, 'translator')
    book_first_pub = extract_metadata(index_soup, 'firstpub')

    book = epub.EpubBook()
    book.set_identifier('unique_identifier')
    book.set_title(book_title)
    book.set_language(book_lang)
    book.add_author(author_name)
    book.add_metadata('DC', 'publisher', book_publisher)
    book.add_metadata('DC', 'subject', book_genre)
    book.add_metadata('DC', 'contributor', book_translator)
    book.add_metadata('DC', 'date', book_first_pub)


    # Create a new EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('unique_identifier')
    book.set_title(book_title)
    book.set_language(book_lang)
    book.add_author(author_name)
    book.add_metadata('DC', 'publisher', book_publisher)
    book.add_metadata('DC', 'subject', book_genre)
    book.add_metadata('DC', 'contributor', book_translator)

    if args.deletedecover:
        titelpage_path = os.path.join(html_directory, 'titlepage.html')
        try:
            with open(titelpage_path, 'r', encoding='utf-8') as titelpage_file:
                titelpage_content = titelpage_file.read()
                titel_soup = BeautifulSoup(titelpage_content, 'html.parser')
                
                covertoremove = titel_soup.find_all('img', src=lambda src: src and 'cover' in src)
                for cover in covertoremove:
                    cover.decompose()
            
            # Now, write the modified content back to the same HTML file
            with open(titelpage_path, 'w', encoding='utf-8') as titelpage_file:
                titelpage_file.write(str(titel_soup))
        except FileNotFoundError as e:
            print(f"Error: {e} - The HTML file '{titelpage_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        
    # Initialize the image directory path
    image_dir = os.path.join(html_directory)

    # Create a directory within the EPUB directory to store images
    epub_image_dir = os.path.join(html_directory, 'images')
    os.makedirs(epub_image_dir, exist_ok=True)

    # # Add the CSS file to the EPUB book's resources
    # css_path = os.path.join(html_directory, 'css', 'prosa.css')
    # css_id = 'prosa-css'
    # book.add_item(epub.EpubItem(uid=css_id, file_name=css_path, media_type='text/css', content=open(css_path).read()))

    # Find the table of contents list
    toc_list = index_soup.find('h3', string='Inhaltsverzeichnis').find_next('ul')
    toc_items = toc_list.find_all('a', href=True)

    # Create the table of contents and spine
    toc = []
    spine = ['nav']  # Initialize the spine with the 'nav' entry

    pattern = r'\\[^\\]+\\[^\\]+\\temp$'
    cover_directory = re.sub(pattern, '', html_directory)

    # Define the regular expression pattern
    pattern = r'^cover\[[^\]]+\]\$'

    # List all files in the folder
    file_list = os.listdir(epub_image_dir)

    iscover = False

    for filename in file_list:
        if re.match(pattern, filename):
            iscover = True

    target_name = 'cover.png'

    for filename in os.listdir(epub_image_dir):
        if filename.startswith('cover') and filename != target_name:
            _, extension = os.path.splitext(filename)
            new_filename = target_name[:-4] + extension
            new_path = os.path.join(epub_image_dir, new_filename)
            old_path = os.path.join(epub_image_dir, filename)
            iscover = True
            if not os.path.exists(new_path):
             shutil.copy2(old_path, new_path)


    # Iterate through the table of contents and add pages to the EPUB book
    for toc_item in toc_items:
        page_href = toc_item['href']
        page_path = os.path.join(html_directory, page_href)


        # Read and parse the page content
        with open(page_path, 'r', encoding='utf-8') as page_file:
            page_content = page_file.read()
        page_soup = BeautifulSoup(page_content, 'html.parser')

        # Extract page title
        page_title = toc_item.get_text()

        # Create a new EPUB item for the page
        page_id = page_href.replace('.html', '')  # Use page filename as ID
        page = epub.EpubHtml(title=page_title, file_name=page_href)
        # Handle images
        img_tags = page_soup.find_all('img')
        for img_tag in img_tags:
            img_src = img_tag['src']
            img_path = os.path.join(image_dir, img_src)
            img_filename = (os.path.basename(img_path))
            img_media_type = imghdr.what(img_path)
            img_media_type = 'jpeg' if img_media_type == 'jpg' else img_media_type

            # Add image to the EPUB resources
            img_id = img_src.replace('/', '_').replace('.', '_')
            img_item = epub.EpubItem(uid=img_id, file_name=os.path.join("images", img_filename), media_type=f'image/{img_media_type}', content=open(img_path, 'rb').read())
            book.add_item(img_item)

            # Update the image src path in the HTML
            img_tag['src'] = os.path.join('images', img_filename)  # Relative path to the EPUB/images directory

        # Update the modified page content in the EpubHtml object
        page.content = str(page_soup)

        # Add page to the book
        book.add_item(page)

        # Add page to the spine
        spine.append(page)

        # Add page to the table of contents
        toc.append(epub.Link(page_href, page_title, page_id))

        # Add page to the spine
        spine.append(page_href)  # Add a page entry to the spine

    # Add the table of contents to the book
    book.toc = toc

    # Add the spine (order of contents)
    book.spine = spine

    # Add the default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    if args.addcover:
        cover = args.addcover
        _, extension = os.path.splitext(cover)
        new_filename = 'cover' + extension
        new_path = os.path.join(cover_directory, new_filename)
        old_path = os.path.join(cover_directory, cover)
        
        if not os.path.exists(new_path):
            shutil.copy2(old_path, new_path)
            print("Cover copied successfully") 
            iscover = False
        
        else:
            print("Cover already exists in the temp folder")



    cover_image_formats = ['jpg', 'jpeg', 'png']  # Supported image formats
    for image_format in cover_image_formats:
        cover_path = os.path.join(cover_directory, f'cover.{image_format}')

        if os.path.exists(cover_path):
            iscover = False
            print("toootooot")

    # Add cover image if it exists and set it as the cover and the first page
    add_cover_image_and_first_page(book, cover_directory)

    if iscover == True:
        print("saaaaaaaaaaasa")
        add_cover_image_and_first_page(book, epub_image_dir)

                
    #delete the /temp from html_directory
    epub_directory = html_directory.replace('\\temp', '')
    # Create an EPUB file
    epub_file = os.path.join(epub_directory, book_title + '.epub')
    epub.write_epub(epub_file, book, {})

    if os.path.exists(html_directory):
        # Remove all files and subdirectories within the directory
        for item in os.listdir(html_directory):
            item_path = os.path.join(html_directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove files
            elif os.path.isdir(item_path):
                # Recursively remove subdirectories and their contents
                for root, dirs, files in os.walk(item_path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(item_path)  # Remove subdirectory itself

        # Once the directory is empty, remove it
        os.rmdir(html_directory)
    else:
        print(f"The directory '{html_directory}' does not exist.")
    
    #remove the cover from the temp folder
    if args.addcover:
        try:
            os.remove(new_path)
            print(f"File '{new_path}' removed successfully.")
        except Exception as e:
            try:
                    os.chmod(new_path, 0o755)
                    os.remove(new_path)
            except OSError:
                print(f"Unable to remove file '{new_path}'.")
                print(f"Error: {e}")





    print("EPUB conversion completed.")
    print(f"EPUB file saved to '{epub_directory}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertrt html to epub")
    parser.add_argument("--addcover", help="Path to cover image")
    parser.add_argument("-d", "--output-dir", default="output", help="Directory to save the output")
    parser.add_argument("--deletedecover", type=lambda x: x.lower() == 'true', default=False, help="Remove cover image from the titelpage.")
    args = parser.parse_args()
        
    html_directory = args.output_dir
    convert_to_epub(html_directory)
