from pdfminer.high_level import extract_text
import re
from collections import defaultdict
import json
import os





def process_pdf_text(raw_text):
    """
    Process extracted PDF text to improve formatting and readability.
    
    :param raw_text: Raw text extracted from PDF using pdfminer
    :return: Cleaned and formatted text
    """
    # Remove multiple consecutive whitespace characters
    text = re.sub(r'\s+', ' ', raw_text)
    
    # Remove hyphenation at line breaks
    text = re.sub(r'-\s+', '', text)
    
    # Split text into paragraphs
    # This regex looks for multiple newlines or combination of newlines and spaces
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Clean up individual paragraphs
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        # Strip leading/trailing whitespace
        paragraph = paragraph.strip()
        
        # Skip empty paragraphs
        if not paragraph:
            continue
        
        # Capitalize first letter of paragraph if it's a letter
        if paragraph and paragraph[0].islower():
            paragraph = paragraph[0].upper() + paragraph[1:]
        
        cleaned_paragraphs.append(paragraph)
    
    # Join paragraphs with double newline for clear separation
    formatted_text = '\n\n'.join(cleaned_paragraphs)
    
    # Optional: Remove extra whitespace around punctuation
    formatted_text = re.sub(r'\s+([.,;:!?])', r'\1', formatted_text)
    
    return formatted_text



# def split_into_chapters(formatted_text):
#     """
#     Split the formatted text into chapters based on CAPO headings.
#
#     :param formatted_text: Preprocessed text from previous processing
#     :return: Dictionary of chapters with Roman numeral keys
#     """
#     # Regex to find CAPO headings with Roman numerals
#     chapter_pattern = re.compile(r'(CAPO\s+([IVXLCDM]+))')
#
#     # Split the text using the chapter pattern
#     chapter_splits = chapter_pattern.split(formatted_text)
#
#     # Dictionary to store chapters
#     chapters = {}
#
#     # Process the splits
#     for i in range(1, len(chapter_splits), 3):
#         # Check if we have a valid chapter heading
#         if 'CAPO' in chapter_splits[i]:
#             # Get the Roman numeral
#             roman_numeral = chapter_splits[i+1]
#
#             # Find the content for this chapter
#             # Look ahead to the next chapter or end of text
#             next_chapter_index = chapter_splits[i+2:].index(chapter_splits[i]) if chapter_splits[i] in chapter_splits[i+2:] else None
#
#             if next_chapter_index is not None:
#                 chapter_content = chapter_splits[i+2][:next_chapter_index]
#             else:
#                 chapter_content = chapter_splits[i+2]
#
#             # Clean up the content (remove leading/trailing whitespace)
#             chapter_content = chapter_content.strip()
#
#             # Store in chapters dictionary
#             chapters[roman_numeral] = {
#                 'heading': f'CAPO {roman_numeral}',
#                 'content': chapter_content
#             }
#
#     return chapters
#
# def save_chapters_to_files(chapters, base_filename='gdpr_chapter'):
#     """
#     Save each chapter to a separate text file.
#
#     :param chapters: Dictionary of chapters
#     :param base_filename: Base filename for output files
#     """
#
#     # Create the 'chapters' directory if it doesn't exist
#     folder_name = 'chapters'
#     os.makedirs(folder_name, exist_ok=True)
#
#     for roman_numeral, chapter_info in chapters.items():
#         filename = os.path.join(folder_name, f'{base_filename}_capo_{roman_numeral}.txt')
#         with open(filename, 'w', encoding='utf-8') as f:
#             # Write chapter heading and content
#             f.write(f"{chapter_info['heading']}\n\n")
#             f.write(chapter_info['content'])
#
#         print(f"Saved chapter {roman_numeral} to {filename}")
#
#


def parse_gdpr_text(chapters_dir='chapters'):
    """
    Parse GDPR chapters and convert to structured JSON
    
    :param chapters_dir: Directory containing chapter text files
    :return: Structured JSON representation of GDPR
    """
    gdpr_structure = []
    
    # Sort chapter files to ensure correct order
    chapter_files = sorted([f for f in os.listdir(chapters_dir) 
                             if f.startswith('gdpr_chapter_capo_') and f.endswith('.txt')],
                            key=lambda x: x.split('_')[-1].replace('.txt', ''))
    
    for chapter_index, chapter_file in enumerate(chapter_files, 1):
        with open(os.path.join(chapters_dir, chapter_file), 'r', encoding='utf-8') as f:
            chapter_content = f.read()
        
        # Extract chapter title (if exists)
        chapter_title_match = re.search(r'^CAPO\s+[IVXLCDM]+\s*\n(.+)', chapter_content, re.MULTILINE)
        chapter_title = chapter_title_match.group(1).strip() if chapter_title_match else f"Chapter {chapter_index}"
        
        # Prepare chapter structure
        chapter_struct = {
            "type": "CHAPTER",
            "id": f"CHAPTER_{chapter_index}",
            "title": chapter_title,
            "sections": []
        }
        
        # Find sections within the chapter
        section_matches = list(re.finditer(r'Sezione\s+(\d+)\s*\n(.+?)(?=Sezione|\n\n|$)', chapter_content, re.DOTALL | re.IGNORECASE))
        
        # If no sections found, parse chapter content directly for articles
        if not section_matches:
            articles = parse_articles(chapter_content)
            chapter_struct["sections"].append({
                "type": "SECTION",
                "id": f"SECTION_1",
                "title": chapter_title,
                "articles": articles
            })
        else:
            # Parse sections
            for section_index, section_match in enumerate(section_matches, 1):
                section_number = section_match.group(1)
                section_title = section_match.group(2).strip().split('\n')[0]
                
                # Extract section content
                section_content = section_match.group(0)
                
                section_struct = {
                    "type": "SECTION",
                    "id": f"SECTION_{section_index}",
                    "title": section_title,
                    "articles": parse_articles(section_content)
                }
                
                chapter_struct["sections"].append(section_struct)
        
        gdpr_structure.append(chapter_struct)
    
    return {"gdpr": gdpr_structure}

def parse_articles(text):
    """
    Parse articles from text
    
    :param text: Text containing articles
    :return: List of article structures
    """
    articles = []
    
    # Find articles
    article_matches = list(re.finditer(r'Articolo\s+(\d+)\s*\n(.+?)(?=Articolo|\n\n|$)', text, re.DOTALL | re.IGNORECASE))
    
    for article_index, article_match in enumerate(article_matches, 1):
        article_number = article_match.group(1)
        article_title_match = re.match(r'([^\n]+)', article_match.group(2))
        article_title = article_title_match.group(1).strip() if article_title_match else f"Article {article_number}"
        
        # Parse points and subpoints
        article_content = article_match.group(2)
        points = parse_points(article_content)
        
        article_struct = {
            "type": "ARTICLE",
            "id": f"ARTICLE_{article_number}",
            "title": article_title,
            "points": points
        }
        
        articles.append(article_struct)
    
    return articles

def parse_points(text):
    """
    Parse points and subpoints from text
    
    :param text: Text containing points
    :return: List of point structures
    """
    points = []
    
    # Regex to find points
    point_matches = list(re.finditer(r'^(\d+)\.\s*(.+?)(?=(?:\n\d+\.|\n\n|$))', text, re.MULTILINE | re.DOTALL))
    
    for point_index, point_match in enumerate(point_matches, 1):
        point_number = point_match.group(1)
        point_text = point_match.group(2).strip()
        
        # Find subpoints
        subpoints = []
        subpoint_matches = list(
            re.finditer(r'(^[a-z])\)\s*(.+?)(?=(?:\n[a-z]\)|\n\n|$))', point_match.group(2), re.MULTILINE | re.DOTALL))

        for subpoint_index, subpoint_match in enumerate(subpoint_matches, 1):
            subpoint_letter = subpoint_match.group(1)
            subpoint_text = subpoint_match.group(2).strip()
            
            subpoints.append({
                "type": "SUBPOINT",
                "id": f"SUBPOINT_{subpoint_index}",
                "text": subpoint_text
            })
        
        point_struct = {
            "type": "POINT",
            "id": f"POINT_{point_number}",
            "text": point_text,
            "subpoints": subpoints
        }
        
        points.append(point_struct)
    
    return points

def remove_text_within_parentheses(text):
    # Regular expression to match everything between parentheses
    pattern = r'\(.*?\)'

    # Substitute all matches with an empty string
    result = re.sub(pattern, '', text)

    return result




pdf_path = 'it_gdpr.pdf'
raw_text = extract_text(pdf_path)
processed_text = process_pdf_text(raw_text)
processed_text = remove_text_within_parentheses(processed_text)

with open('gdpr_formatted.txt', 'w', encoding='utf-8') as f:
        f.write(processed_text)


with open('gdpr_formatted.txt', 'r', encoding='utf-8') as f:
        formatted_text = f.read()
    

gdpr_json = parse_gdpr_text()

# Save to JSON file
with open('gdpr_structured.json', 'w', encoding='utf-8') as f:
    json.dump(gdpr_json, f, ensure_ascii=False, indent=2)