import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import argparse


parser = argparse.ArgumentParser(description="Web scraper with output directory option")
parser.add_argument("url", help="URL to scrape")
parser.add_argument("-d", "--output-dir", default="output", help="Directory to save the output")

args = parser.parse_args()

url = args.url
output_dir = args.output_dir



# Define the regex pattern
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

# Hole den HTML-Inhalt der Webseite und beachte das Encoding
response = requests.get(url)
response.encoding = 'utf-8'  # Use UTF-8 encoding
html_content = response.text


# Erstelle ein BeautifulSoup-Objekt zum Parsen des HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Buchtitel extrahieren
book_title = soup.find('meta', {'name': 'title'})['content']

# Autorennamen extrahieren
author_name = soup.find('meta', {'name': 'author'})['content']

# Modify the output directory creation
output_directory = os.path.join(output_dir, author_name, book_title, "temp")
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# Find and download linked CSS files
css_links = soup.find_all('link', rel='stylesheet', href=True)
css_directory = os.path.join(output_directory, 'css')
if not os.path.exists(css_directory):
    os.makedirs(css_directory)

for css_link in css_links:
    css_url = urljoin(url, css_link['href'])
    css_response = requests.get(css_url)
    css_content = css_response.text

    # Extract the CSS file name from the URL and save the content
    css_filename = os.path.join(css_directory, os.path.basename(css_url))
    with open(css_filename, 'w', encoding='utf-8') as css_file:
        css_file.write(css_content)

    # Update the href attribute to point to the local CSS file
    css_link['href'] = os.path.join('css', os.path.basename(css_url))


# Entferne die Navigationselemente
classes_to_remove = ['dropdown', 'main-nav', 'mainnav', 'top', 'center', 'bottomnavi-gb']
for class_to_remove in classes_to_remove:
    elements_to_remove = soup.find_all(class_=class_to_remove)
    for element in elements_to_remove:
        element.extract()

    # Find and modify unwanted links matching the pattern
pattern = re.compile(r'/autoren/namen/.+\.html')
unwanted_links = soup.find_all('a', href=pattern)
for unwanted_link in unwanted_links:
    unwanted_link.replace_with(unwanted_link.text)  # Replace the link with its text content



#Speichere index.html
index_filename = os.path.join(output_directory, 'index.html')
with open(index_filename, 'w', encoding='utf-8') as index_file:
    index_file.write(str(soup))


# Finde das Inhaltsverzeichnis
contents_heading = soup.find('h3', string='Inhaltsverzeichnis')
if contents_heading:
    # Finde alle Links zu den Kapiteln nach dem Inhaltsverzeichnis
    chapter_links = contents_heading.find_next('ul').find_all('a', href=True)

# Create the "images" directory if it doesn't exist
images_directory = os.path.join(output_directory, 'images')
if not os.path.exists(images_directory):
    os.makedirs(images_directory)

    
for chapter_link in chapter_links:
    chapter_url = urljoin(url, chapter_link['href'])
  #  print(chapter_url)

#    # Write chapter links to a text file
#     chapter_links_filename = os.path.join(output_directory, 'chapter_links.txt')
#     with open(chapter_links_filename, 'w', encoding='utf-8') as chapter_links_file:
#         for chapter_link in chapter_links:
#             if chapter_link['href'] == 'chap001.html':
#                 chapter_links_file.write('index.html\n')  # Insert index.html before chap001.html
#             chapter_links_file.write(chapter_link['href'] + '\n')
        

    chapter_response = requests.get(chapter_url)
    chapter_response.encoding = 'utf-8'  # Use UTF-8 encoding
    chapter_content = chapter_response.text
    
    # Create a BeautifulSoup object for the chapter content
    chapter_soup = BeautifulSoup(chapter_content, 'html.parser')

    
    
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
    h5_elements = chapter_soup.find_all('h5')
    for h5 in h5_elements:
        if author_name in h5.get_text() or book_title in h5.get_text():
            h5.extract()
    
    # Find and replace <a> tags with <span> tags
    a_tags = chapter_soup.find_all('a')
    for a_tag in a_tags:
        if a_tag.has_attr('id') and a_tag.has_attr('name') and a_tag.has_attr('title'):
            new_tag = chapter_soup.new_tag('span', **{'epub:type': 'pagebreak', 'id': a_tag['id'], 'title': a_tag['name']})
            a_tag.replace_with(new_tag)

    # Get the modified HTML content
    modified_chapter_content = str(chapter_soup)


    # Apply regex to remove the unwanted content
    pattern1 = r'<a href="/autoren/namen(.*?)&gt;&gt;</a>'
    modified_chapter_content = re.sub(pattern1, '', str(chapter_soup))
    
    pattern2 = r'<a href="(.*?).html">&lt;&lt; zurück</a>'
    modified_chapter_content = re.sub(pattern2, '', modified_chapter_content)


    pattern3 = r'<a href="(.*?).html" style="float: right;">weiter &gt;&gt;</a>'
    modified_chapter_content = re.sub(pattern3, '', modified_chapter_content)


    # Create a new BeautifulSoup object for the modified content
    modified_chapter_soup = BeautifulSoup(modified_chapter_content, 'html.parser')
    
    # Remove unwanted elements based on classes as before
    classes_to_remove = ['dropdown', 'main-nav', 'mainnav', 'top', 'center', 'bottomnavi-gb']
    for class_to_remove in classes_to_remove:
        elements_to_remove = modified_chapter_soup.find_all(class_=class_to_remove)
        for element in elements_to_remove:
            element.extract()

    elements_to_remove = modified_chapter_soup.find_all(class_='toc')
    for element in elements_to_remove:
        element.extract()

    # Remove unwanted elements by tag and attributes
    elements_to_remove = modified_chapter_soup.find_all('hr', {'color': '#808080', 'size': '1'})
    for element in elements_to_remove:
        element.extract()

    elements_to_remove = modified_chapter_soup.find_all('a', href='titlepage.html')
    for element in elements_to_remove:
        element.extract()

    elements_to_remove = modified_chapter_soup.find_all('a', {'href': 'chap002.html', 'style': 'float: right;'})
    for element in elements_to_remove:
        element.extract()

    # Remove the navigation links for previous and next chapters
    navigation_links = modified_chapter_soup.find_all('a', {'href': re.compile(r'^chap\d+.html')})
    for link in navigation_links:
        link.extract()




    # Remove the � symbols
    modified_chapter_content = modified_chapter_content.replace('�', '')

    # Save the chapter as a separate HTML file
    chapter_filename = os.path.join(output_directory, f"{chapter_link['href']}")
    with open(chapter_filename, 'w', encoding='utf-8') as chapter_file:
        chapter_file.write(str(modified_chapter_soup))
#print(author_name)

# Create an EPUB book open converter2book.py
print(output_directory)

