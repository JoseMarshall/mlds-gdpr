import re


def extract_all_numbers(text):
    # Find all sequences of digits in the text
    numbers = re.findall(r"\d+", text)
    # Convert them to integers
    return "".join(numbers).strip()


def extract_romans(text):
    # Find all sequences of roman numerals in the text
    romans = re.findall(r" [IVXLCDM]+", text)
    # Convert them to integers
    return "".join(romans).strip()


def deep_extract_literal(obj):
    if isinstance(obj, dict):
        # get keys from obj
        keys = list(obj.keys())
        return (
            deep_extract_literal(obj["content"])
            if "content" in keys
            else deep_extract_literal(obj[keys[0]]["content"])
        )

    elif isinstance(obj, list):
        return " ".join(deep_extract_literal(item) for item in obj)
    elif isinstance(obj, str):
        return obj
    else:
        return ""
