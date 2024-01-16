import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(description="Web scraper with output directory option")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("-d", "--output-dir", default="output", help="Directory to save the output")
    return parser.parse_args()

def checkurl(url):
    pattern = r'https://www\.projekt-gutenberg\.org/(.*?)/(.*?)/.*?\.html'
    # Match the pattern against the URL
    match = re.match(pattern, url)

    if match:
        # Extract the first and second groups from the match
        group1 = match.group(1)
        group2 = match.group(2)
        
        # Construct the modified URL
        modified_url = f'https://www.projekt-gutenberg.org/{group1}/{group2}/'
        url = modified_url
    return url

def download_html(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Use UTF-8 encoding
    return response.text

def create_output_directory(output_dir, author_name, book_title):
    output_directory = os.path.join(output_dir, author_name, book_title, "temp")
    os.makedirs(output_directory, exist_ok=True)
    return output_directory

def download_and_save_css(css_link, url, css_directory):
    css_url = urljoin(url, css_link['href'])
    css_response = requests.get(css_url)
    css_content = css_response.content.decode('utf-8')
    css_filename = os.path.join(css_directory, os.path.basename(css_url))
    with open(css_filename, 'w', encoding='utf-8') as css_file:
        css_file.write(css_content)
    css_link['href'] = os.path.join('css', os.path.basename(css_url))

def remove_unwanted_elements(soup):
    classes_to_remove = ['dropdown', 'main-nav', 'mainnav', 'top', 'center', 'bottomnavi-gb', 'anzeige-chap']
    for class_to_remove in classes_to_remove:
        elements_to_remove = soup.find_all(class_=class_to_remove)
        for element in elements_to_remove:
            element.extract()
            
def find_and_modify_unwanted_links(soup):
    pattern = re.compile(r'/autoren/namen/.+\.html')
    unwanted_links = soup.find_all('a', href=pattern)
    for unwanted_link in unwanted_links:
        unwanted_link.replace_with(unwanted_link.text)  # Replace the link with its text content

def save_html_content_to_file(soup, output_directory):
    index_filename = os.path.join(output_directory, 'index.html')
    with open(index_filename, 'w', encoding='utf-8') as index_file:
        index_file.write(str(soup))
            
def find_and_process_chapters(url, output_directory, author_name, book_title, soup):

    contents_heading = soup.find('h3', string='Inhaltsverzeichnis')
    if contents_heading:
        # Finde alle Links zu den Kapiteln nach dem Inhaltsverzeichnis
        chapter_links = contents_heading.find_next('ul').find_all('a', href=True)

    # Create the "images" directory if it doesn't exist
    images_directory = os.path.join(output_directory, 'images')
    os.makedirs(images_directory, exist_ok=True)

    def modify_chapter_content(chapter_soup):
        nonlocal images_directory
        # Find and replace the CSS link for the chapter
        chapter_css_link = chapter_soup.find('link', rel='stylesheet', href=True)
        if chapter_css_link:
            chapter_css_link['href'] = os.path.join('css', os.path.basename(chapter_css_link['href']))

        # Find and download images
        img_tags = chapter_soup.find_all('img', src=True)
        for img_tag in img_tags:
            img_src = urljoin(chapter_url, img_tag['src'])
            img_name = os.path.basename(img_src)
            img_path = os.path.join(images_directory, img_name)

            # Download and save the image
            img_response = requests.get(img_src)
            with open(img_path, 'wb') as img_file:
                img_file.write(img_response.content)

            # Replace the image src with the local path
            img_tag['src'] = os.path.join('images', img_name)

        # Remove unwanted <h5> elements
        for h5 in chapter_soup.find_all('h5'):
            if author_name in h5.get_text() or book_title in h5.get_text():
                h5.extract()

        # Find and replace <a> tags with <span> tags; Replace Pages with Pagebreaks
        for a_tag in chapter_soup.find_all('a'):
            if a_tag.has_attr('id') and a_tag.has_attr('name') and a_tag.has_attr('title'):
                new_tag = chapter_soup.new_tag('span', **{'epub:type': 'pagebreak', 'id': a_tag['id'], 'title': a_tag['name']})
                a_tag.replace_with(new_tag)

        # Apply regex to remove unwanted content
        patterns = [
            r'<a href="/autoren/namen(.*?)&gt;&gt;</a>',
            r'<a href="(.*?).html">&lt;&lt; zurück</a>',
            r'<a href="(.*?).html" style="float: right;">weiter &gt;&gt;</a>'
        ]
        for pattern in patterns:
            chapter_soup = BeautifulSoup(re.sub(pattern, '', str(chapter_soup)), 'html.parser')

        # Remove unwanted elements based on classes and attributes
        classes_and_attributes_to_remove = [
            ['dropdown', 'main-nav', 'mainnav', 'top', 'bottomnavi-gb', 'anzeige-chap'],
            {'hr': {'color': '#808080', 'size': '1'}, 'a': {'href': 'titlepage.html'}, 'a': {'href': 'chap002.html', 'style': 'float: right;'}, 'a': {'href': '/info/texte/index.html'}}
        ]
        for item in classes_and_attributes_to_remove:
            if isinstance(item, list):
                for class_name in item:
                    for element in chapter_soup.find_all(class_=class_name):
                        element.extract()
            elif isinstance(item, dict):
                for tag, attributes in item.items():
                    for element in chapter_soup.find_all(tag, attributes):
                        element.extract()

        # Remove the navigation links for previous and next chapters
        for link in chapter_soup.find_all('a', {'href': re.compile(r'^chap\d+.html')}):
            link.extract()

        # Remove the � symbols
        chapter_soup = BeautifulSoup(str(chapter_soup).replace('�', ''), 'html.parser')

        # Find all empty table and paragraph tags and remove them
        for tag in chapter_soup.find_all(lambda t: t.name in ['table', 'p'] and not t.contents):
            tag.decompose()

        return chapter_soup

    with requests.Session() as session:
        for chapter_link in chapter_links:
            chapter_url = urljoin(url, chapter_link['href'])
            chapter_response = requests.get(chapter_url)
            chapter_response.encoding = 'utf-8'
            chapter_content = chapter_response.text
            chapter_soup = BeautifulSoup(chapter_content, 'html.parser')

            chapter_soup = modify_chapter_content(chapter_soup)

            # Save the chapter as a separate HTML file
            chapter_filename = os.path.join(output_directory, chapter_link['href'])
            with open(chapter_filename, 'w', encoding='utf-8') as chapter_file:
                chapter_file.write(str(chapter_soup.prettify()))


def main():
    args = get_arguments()
    url = args.url
    url = checkurl(url)
    html_content = download_html(url)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    book_title = soup.find('meta', {'name': 'title'})['content']
    author_name = soup.find('meta', {'name': 'author'})['content']
    
    output_directory = create_output_directory(args.output_dir, author_name, book_title)
    
    css_links = soup.find_all('link', rel='stylesheet', href=True)
    css_directory = os.path.join(output_directory, 'css')
    os.makedirs(css_directory, exist_ok=True)
    
    for css_link in css_links:
        download_and_save_css(css_link, url, css_directory)
    
    remove_unwanted_elements(soup)
    find_and_modify_unwanted_links(soup)
    save_html_content_to_file(soup, output_directory)
    find_and_process_chapters(url, output_directory, author_name, book_title, soup)
    print(output_directory)
     

if __name__ == "__main__":
    main()