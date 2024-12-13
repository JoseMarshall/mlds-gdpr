import re
import json
import uuid

def parse_legal_document(text):
    document = {}

    # Find all chapters
    chapters = re.findall(r'(CAPO\s+([IVXLCDM]+))', text)

    for chapter_index, (full_chapter, chapter_numeral) in enumerate(chapters, 1):
        # Create chapter key
        chapter_key = f"cpt_{chapter_index}"

        # Find the chapter title
        chapter_title_match = re.search(
            rf'{full_chapter}\s*(.+?)(?=\s*Articolo|\s*Sezione|$)',
            text,
            re.DOTALL
        )
        chapter_title = chapter_title_match.group(1).strip() if chapter_title_match else "Untitled Chapter"

        # Initialize chapter dictionary
        document[chapter_key] = {
            "classType": "CHAPTER",
            "content": {
                # Chapter Title ID
                str(uuid.uuid4()): {
                    "classType": "TITLE_ID",
                    "content": full_chapter
                },
                # Chapter Title
                str(uuid.uuid4()): {
                    "classType": "TITLE",
                    "content": {
                        str(uuid.uuid4()): {
                            "classType": "TITLE",
                            "content": chapter_title
                        }
                    }
                }
            }
        }
        # Find the text for this specific chapter
        chapter_start = text.find(full_chapter)
        next_chapter_match = re.search(r'CAPO\s+[IVXLCDM]+', text[chapter_start + len(full_chapter):])

        if next_chapter_match:
            chapter_text = text[chapter_start + len(full_chapter):chapter_start + len(
                full_chapter) + next_chapter_match.start()]
        else:
            chapter_text = text[chapter_start + len(full_chapter):]

        # Find all articles with their numbers, titles, and content
        article_matches = list(re.finditer(r'Articolo (\d+)\s*(.*?)(?=\s*\(|\s*1\.|(?:\s+[A-Z][a-z]+(?!\s*Unione)))', chapter_text))

        for i, article_match in enumerate(article_matches):
            # Extract article number and title
            article_number = article_match.group(1)
            article_title = article_match.group(2).strip() if article_match.group(2) else "No Title"

            # Find the content of the article
            article_start = article_match.end()
            next_article_match = article_matches[i + 1] if i + 1 < len(article_matches) else None
            article_text = chapter_text[article_start:next_article_match.start()] if next_article_match else chapter_text[article_start:]

            # Create article key
            article_key = f"{chapter_key}.art_{article_number}"

            # Create article dictionary
            article_dict = {
                "classType": "ARTICLE",
                "content": {
                    # Article ID
                    str(uuid.uuid4()): {
                        "classType": "ARTICLE",
                        "content": f"Articolo {article_number}"
                    },
                    # Article Title
                    str(uuid.uuid4()): {
                        "classType": "TITLE",
                        "content": article_title
                    },
                    "points": {}
                }
            }

            # Parse points
            points = re.findall(r'(?<!\()\b(\d+)[\.\)]\s(.+?)(?=\d+[\.\)]\s|$)', article_text, re.DOTALL)
            for j, (point_num, point_text) in enumerate(points, 1):
                point_key = f"{article_key}.pt_{j}"
                point_dict = {
                    "classType": "POINT",
                    "content": point_text.strip()
                }
                # Check for subpoints
                subpoints = re.findall(r'\b([a-z])\)\s*(.+?)(?=\b[a-z]\)|$)', point_text, re.DOTALL | re.MULTILINE)
                if subpoints:
                    point_dict["subpoints"] = {}
                    for k, (subpoint_letter, subpoint_text) in enumerate(subpoints, 1):
                        subpoint_key = f"{point_key}.spt_{subpoint_letter}"
                        point_dict["subpoints"][subpoint_key] = {
                            "classType": "SUBPOINT",
                            "content": [f"{subpoint_letter})", subpoint_text.strip()]
                        }

                article_dict["content"]["points"][point_key] = point_dict

            document[chapter_key]["content"][article_key] = article_dict

    return document




# Example usage
# Define the file path
file_path = "gdpr_formatted.txt"

# Read the file content
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Display the content stored in the text variable



result = parse_legal_document(text)
# Save to JSON file
with open('Chapter_structured.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)