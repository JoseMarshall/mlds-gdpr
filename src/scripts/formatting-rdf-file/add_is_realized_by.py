import os
import re

def add_is_realized_by(input_file, output_file):
    """
    Processes an RDF file to find instances of <eli:realizes rdf:resource="...">
    and adds <eli:is_realized_by rdf:resource="..._en"/> to the corresponding
    individuals one line before their closing tag.

    Args:
        input_file (str): Path to the RDF file to process.
        output_file (str): Path to save the updated RDF file.
    """
    # Regex to find <eli:realizes rdf:resource="...">
    realizes_pattern = re.compile(r'<eli:realizes rdf:resource="([^"]+)"')

    # Read the RDF file
    with open(input_file, "r") as rdf_file:
        lines = rdf_file.readlines()

    # Collect realized resources
    realized_resources = []
    for line in lines:
        match = realizes_pattern.search(line)
        if match:
            realized_resources.append(match.group(1))

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        updated_lines.append(line)

        # Check for <owl:NamedIndividual rdf:about="...">
        if line.strip().startswith('<owl:NamedIndividual rdf:about="'):
            # Extract the rdf:about content
            rdf_about_match = re.search(r'<owl:NamedIndividual rdf:about="([^"]+)"', line)
            if rdf_about_match:
                rdf_about = rdf_about_match.group(1)

                # If this rdf:about is in the realized resources
                if rdf_about in realized_resources:
                    # Locate the closing </owl:NamedIndividual> tag
                    for j in range(i + 1, len(lines)):
                        updated_lines.append(lines[j])
                        if lines[j].strip() == "</owl:NamedIndividual>":
                            # Insert <eli:is_realized_by> before the closing tag
                            i = j  # Update the outer loop index
                            updated_lines.insert(len(updated_lines) - 1, 
                                f'        <eli:is_realized_by rdf:resource="{rdf_about}_en"/>\n')                          
                            break

        i += 1

    # Save the updated RDF file
    with open(output_file, "w") as updated_rdf:
        updated_rdf.writelines(updated_lines)


# Example Usage
input_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology.rdf')
output_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology_with_is_realized_by.rdf')

# Run the function
add_is_realized_by(input_rdf, output_rdf)
