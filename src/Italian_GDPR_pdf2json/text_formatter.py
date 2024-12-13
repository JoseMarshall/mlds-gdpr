import re

def format_legal_document(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Define patterns for different parts of the document
    capo_pattern = re.compile(r'(CAPO\s+[IVXLCDM]+)', re.IGNORECASE)
    article_pattern = re.compile(r'(Articolo\s+\d+)', re.IGNORECASE)
    point_pattern = re.compile(r'(\d+\.)')
    subpoint_pattern = re.compile(r'(\b[a-z]\)\s)')

    # Split the text into lines and format
    formatted_lines = []
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        # Format CAPO
        if capo_pattern.match(line):
            formatted_lines.append(f"\n{line}\n")
        # Format Articolo
        elif article_pattern.match(line):
            formatted_lines.append(f"\n{line}\n")
        # Format numbered points
        elif point_pattern.match(line):
            formatted_lines.append(f"{line}\n")
        # Format subpoints
        elif subpoint_pattern.match(line):
            formatted_lines.append(f"    {line}\n")
        # Handle regular lines
        else:
            formatted_lines.append(f"{line}")

    # Join formatted lines and write to output file
    formatted_text = '\n'.join(formatted_lines)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(formatted_text)

    print(f"Formatted document saved to {output_file}")

# Example usage

