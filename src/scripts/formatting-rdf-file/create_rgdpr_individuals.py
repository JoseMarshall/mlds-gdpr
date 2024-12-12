import re
import os

def process_rdf_with_individuals(input_file, output_file):
    """
    Processes an RDF file to find <owl:NamedIndividual rdf:about=...CONTENT_OF_INTEREST...>,
    extracts the CONTENT_OF_INTEREST, and creates three new individual entities with variations.

    Args:
        input_file (str): Path to the RDF file to process.
        output_file (str): Path to save the updated RDF file.
    """
    # Regex to match the specific line and capture CONTENT_OF_INTEREST
    pattern = re.compile(r'<owl:NamedIndividual rdf:about="http://www\.semanticweb\.org/knorri/ontologies/2024/11/rgdpr#([^"]+)">')

    # Read the RDF file
    with open(input_file, "r") as rdf_file:
        lines = rdf_file.readlines()

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        updated_lines.append(line)

        # Look for matches in the current line
        match = pattern.search(line)
        if match:
            content_of_interest = match.group(1)  # Extract CONTENT_OF_INTEREST
            # Generate new versions with different endings
            versions = [f"{content_of_interest}_de", f"{content_of_interest}_it", f"{content_of_interest}_pt"]

            # Find <rdf:type rdf:resource="http://data.europa.eu/eli/ontology#LegalExpression"/>
            while i + 1 < len(lines):
                i += 1
                updated_lines.append(lines[i])
                if lines[i].strip() == '<rdf:type rdf:resource="http://data.europa.eu/eli/ontology#LegalExpressionX"/>':
                    # Add translations and realizations
                    for version in versions:
                        updated_lines.append(f'        <eli:has_translation rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/rgdpr#{version}"/>\n')
                    updated_lines.append(f'        <eli:realizes rdf:resource="http://www.semanticweb.org/knorri/ontologies/2024/11/gdpr#{content_of_interest}"/>\n')
                    break

            # Locate the next closing tag for the individual
            while i + 1 < len(lines):
                i += 1
                updated_lines.append(lines[i])
                if lines[i].strip() == "</owl:NamedIndividual>":
                    # Add three empty lines after the closing tag
                    updated_lines.append("\n\n\n")
                    # Add the new individuals
                    for version in versions:
                        updated_lines.append(f'    <!-- http://www.semanticweb.org/knorri/ontologies/2024/11/rgdpr#{version} -->\n')
                        updated_lines.append(f'    <owl:NamedIndividual rdf:about="http://www.semanticweb.org/knorri/ontologies/2024/11/rgdpr#{version}">\n')
                        updated_lines.append(f'          <rdf:type rdf:resource="http://data.europa.eu/eli/ontology#LegalExpression"/>\n')
                        updated_lines.append(f'    </owl:NamedIndividual>\n\n\n')
                    break

        i += 1  # Continue to the next line

    # Save the updated RDF file
    with open(output_file, "w") as updated_rdf:
        updated_rdf.writelines(updated_lines)

# Example Usage
input_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology.rdf')
output_rdf = os.path.join(os.path.dirname(__file__), 'rgdpr_ontology_with_language_individuals.rdf')

# Run the function
process_rdf_with_individuals(input_rdf, output_rdf)
