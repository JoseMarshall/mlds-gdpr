import os
import re

file_name = os.path.join(os.path.dirname(__file__), 'gdpr_ontology.rdf')

def add_type(input_file, output_file, target_patterns, tags_to_add):
    """
    Scans through an RDF file, identifies a target name or regex pattern, and adds a tag after it.
    
    Args:
        input_file (str): Path to the RDF file to process.
        output_file (str): Path to save the updated RDF file.
        target_patterns (list): Regex patterns to search for in the RDF file.
        tags_to_add (list): Tags to add after each matching pattern.
    """
    # Ensure target patterns and tags are the same length
    assert len(target_patterns) == len(tags_to_add), "Patterns and tags must be of the same length."

    # Compile regex patterns
    compiled_patterns = [re.compile(pattern) for pattern in target_patterns]

    with open(input_file, 'r') as rdf:
        lines = rdf.readlines()

    updated_lines = []
    for line in lines:
        updated_lines.append(line)
        for i, pattern in enumerate(compiled_patterns):
            if pattern.search(line):  # Check for regex match
                updated_lines.append(f"        {tags_to_add[i]}\n    ")  # Add the corresponding tag
                break  # Avoid duplicate matches for the same line

    # Save the updated RDF file
    with open(output_file, 'w') as updated_rdf:
        updated_rdf.writelines(updated_lines)

# Example Usage:
output_rdf = os.path.join(os.path.dirname(__file__), 'gdpr_ontology_updated.rdf')

# Regex patterns to match specific entities
names_to_check = [
        r'subpoint_[a-z]+"',
        r'point_\d+"',
        r'<owl:NamedIndividual rdf:about="http://www\.semanticweb\.org/knorri/ontologies/2024/11/gdpr#article_'
]

# Corresponding tags to insert
tags_to_insert = [
    '<rdf:type rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#Subpoint"/>',
    '<rdf:type rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#Point"/>',
    '<rdf:type rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#Article"/>'
]

# Run the function
add_type(file_name, output_rdf, names_to_check, tags_to_insert)
