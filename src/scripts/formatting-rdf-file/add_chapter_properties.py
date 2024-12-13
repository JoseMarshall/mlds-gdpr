import re
import json
import os

def add_chapter_tags(input_rdf, input_json, output_rdf):
    """
    Scans an RDF file to identify articles, matches them to their corresponding chapters
    using a JSON reference with nested structure, and inserts a specific tag based on the chapter.

    Args:
        input_rdf (str): Path to the RDF file to process.
        input_json (str): Path to the JSON reference file.
        output_rdf (str): Path to save the updated RDF file.
    """
    # Load the JSON reference file
    with open(input_json, "r") as json_file:
        json_data = json.load(json_file)

    # Read the RDF file
    with open(input_rdf, "r") as rdf_file:
        lines = rdf_file.readlines()

    # Regex to identify an article's NamedIndividual and its rdf:type
    article_named_individual_regex = re.compile(r'<owl:NamedIndividual rdf:about=".*#(article_\d+)">')
    article_type_regex = re.compile(r'<rdf:type rdf:resource=".*#Article"/>')

    updated_lines = []
    for i, line in enumerate(lines):
        updated_lines.append(line)
        
        # Check if the current line matches the rdf:type for an article
        if article_type_regex.search(line):
            # Go back one line to extract the article's name/id
            previous_line = lines[i - 1]
            match = article_named_individual_regex.search(previous_line)
            if match:
                article_name = match.group(1)  # Extract the article name, e.g., "article_97"
                
                # Convert article_name to its abbreviated form, e.g., "article_01" -> "art_1"
                article_number = int(article_name.split("_")[1])  # Remove leading zeros
                article_abbreviation = f"art_{article_number}"  # Format the abbreviated article name

                # Traverse the JSON to find the corresponding chapter
                for chapter_key, chapter_value in json_data.items():
                    if "content" in chapter_value:  # Ensure chapter has content
                        for key, value in chapter_value["content"].items():
                            if article_abbreviation in key:  # Match article abbreviation
                                chapter_abbr = chapter_key  # Get the chapter key, e.g., "cpt_1"
                                
                                # Convert the chapter abbreviation to full name, e.g., "chapter_11"
                                chapter_number = int(chapter_abbr.split("_")[1])
                                chapter_full_name = f"chapter_{chapter_number:02d}"
                                
                                # Create the tag to insert
                                tag_to_insert = f'<eli:is_part_of rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#{chapter_full_name}"/>'
                                
                                # Insert the tag into the RDF file
                                updated_lines.append(f"        {tag_to_insert}\n")
                                break
                        else:
                            continue
                        break

    # Save the updated RDF file
    with open(output_rdf, "w") as updated_rdf:
        updated_rdf.writelines(updated_lines)

# Example Usage
input_rdf = os.path.join(os.path.dirname(__file__), 'gdpr_ontology.rdf')
input_json = os.path.join(os.path.dirname(__file__), 'src/datasets/gdpr-eu-en.json')
output_rdf = os.path.join(os.path.dirname(__file__), 'gdpr_ontology_with_chapter_tags.rdf')

# Run the script
add_chapter_tags(input_rdf, input_json, output_rdf)
