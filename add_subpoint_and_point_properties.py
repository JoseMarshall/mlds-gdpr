import re
import os

def add_terms_with_capturing_groups(input_rdf, output_rdf, regex_patterns, tag_templates):
    """
    Scans an RDF file, identifies individuals using regex with capturing groups,
    and adds a dynamically generated tag one line after the match.

    Args:
        input_rdf (str): Path to the RDF file to process.
        output_rdf (str): Path to save the updated RDF file.
        regex_patterns (list): List of regex patterns with capturing groups to search for.
        tag_templates (list): List of tag templates with placeholders to use for matching patterns.
    """
    # Ensure regex_patterns and tag_templates are the same length
    assert len(regex_patterns) == len(tag_templates), "Patterns and templates must have the same length."

    # Compile the regex patterns
    compiled_patterns = [re.compile(pattern) for pattern in regex_patterns]

    # Read the RDF file
    with open(input_rdf, "r") as rdf_file:
        lines = rdf_file.readlines()

    updated_lines = []
    skip_next_insert = False  # A flag to insert the tag in the next line
    tag_to_insert = ""  # Placeholder for the tag to insert

    for idx, line in enumerate(lines):
        # Append the current line to updated_lines
        updated_lines.append(line)
        
        if skip_next_insert:
            # Insert the tag after skipping the previous line
            updated_lines.append(f"        {tag_to_insert}\n")
            skip_next_insert = False  # Reset the flag
            tag_to_insert = ""  # Clear the tag
            continue
        
        # Check for matches in the current line
        for i, pattern in enumerate(compiled_patterns):
            match = pattern.search(line)
            if match:
                # Extract captured groups
                groups = match.groups()
                # Format the tag using the extracted values
                tag_to_insert = tag_templates[i].format(*groups)
                skip_next_insert = True  # Set the flag to skip the next line
                break  # Avoid duplicate matches for the same line

    # Save the updated RDF file
    with open(output_rdf, "w") as updated_rdf:
        updated_rdf.writelines(updated_lines)

# Example Usage
input_rdf = os.path.join(os.path.dirname(__file__), 'gdpr_ontology.rdf')
output_rdf = os.path.join(os.path.dirname(__file__), 'gdpr_ontology_updated_with_subpoint_and_point_properties.rdf')

# Regex patterns with capturing groups
regex_patterns = [
    r'<owl:NamedIndividual rdf:about="http://www\.semanticweb\.org/knorri/ontologies/2024/11/gdpr#article_(\d+)_point_(\d+)_subpoint_([a-z])">',
    r'<owl:NamedIndividual rdf:about="http://www\.semanticweb\.org/knorri/ontologies/2024/11/gdpr#article_(\d+)_point_(\d+)">'
]

# Corresponding tag templates with placeholders for captured values
tag_templates = [
    '<eli:is_part_of rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#article_{0}_point_{1}"/>',
    '<eli:is_part_of rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#article_{0}"/>'
]

# Run the script
add_terms_with_capturing_groups(input_rdf, output_rdf, regex_patterns, tag_templates)
