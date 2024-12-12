import re
import os

def add_en_suffix(input_file, output_file):
    """
    Processes an RDF file to find <owl:NamedIndividual rdf:about=...>
    URIs starting with 'http://www.semanticweb.org/knorri/ontologies/2024/11/rgdpr#',
    appends '_en' to those not ending with '_de', '_it', or '_pt', and updates the
    commented-out declaration as well.

    Args:
        input_file (str): Path to the RDF file to process.
        output_file (str): Path to save the updated RDF file.
    """
    # Regex pattern to match and capture the relevant parts
    pattern = re.compile(
        r'(<!--\s*http://www\.semanticweb\.org/knorri/ontologies/2024/11/rgdpr#([^\s]+?)\s*-->)\n\n'
        r'(\s*<owl:NamedIndividual rdf:about="http://www\.semanticweb\.org/knorri/ontologies/2024/11/rgdpr#([^\"]+?)">)'
    )

    # Substitution function to modify matched lines
    def substitute_match(match):
        original_comment = match.group(1)  # The full commented-out line
        original_name = match.group(2)     # The name within the comment
        individual_declaration = match.group(3)  # The full owl:NamedIndividual line
        rdf_name = match.group(4)          # The name in the rdf:about attribute

        # Check if the name already ends with '_de', '_it', or '_pt'
        if rdf_name.endswith(('_de', '_it', '_pt')):
            return match.group(0)  # Return the original text unmodified

        # Add '_en' to the names
        updated_comment = original_comment.replace(original_name, f"{original_name}_en")
        updated_individual = individual_declaration.replace(rdf_name, f"{rdf_name}_en")

        # Return the updated lines
        return f"{updated_comment}\n\n{updated_individual}"

    # Read the RDF file
    with open(input_file, "r") as rdf_file:
        rdf_content = rdf_file.read()

    # Apply the regex substitution
    updated_content = pattern.sub(substitute_match, rdf_content)

    # Save the updated RDF file
    with open(output_file, "w") as updated_rdf:
        updated_rdf.write(updated_content)

# Example Usage
input_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology.rdf')
output_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology_with_en.rdf')

# Run the function
add_en_suffix(input_rdf, output_rdf)
