import re
from rdflib import URIRef, Literal, Namespace


def add_description(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    custom_namespaces: dict[str, Namespace],
):
    graph.add(
        (node_uri, custom_namespaces["ELI"].description, Literal(node["content"]))
    )
    # get the number from the beginning of the string using regex
    number = (
        extract_all_numbers(node["content"][0:5])
        if "content" in node and isinstance(node["content"], str)
        else None
    )

    number = number if number else extract_number_from_id(node_uri, locale)
    graph.add((node_uri, custom_namespaces["ELI"].number, Literal(number)))
    for parent_title_alternative in graph.objects(
        parent_uri, custom_namespaces["ELI"].title_alternative
    ):
        graph.add(
            (
                node_uri,
                custom_namespaces["ELI"].title_alternative,
                Literal(parent_title_alternative + "-" + number),
            )
        )


def extract_all_numbers(text):
    # Find all sequences of digits in the text
    numbers = re.findall(r"\d+", text)
    # Convert them to integers
    return "".join(numbers).strip()


def extract_romans(text):
    # Find all sequences of roman numerals in the text
    romans = re.findall(r" [IVXLCDM0-9]+", text)
    # Convert them to integers
    return "".join(romans).strip()


def extract_node_id(node_uri: str, locale: str = ""):
    # exclude the locale
    return re.sub(rf"_{locale}$", "", node_uri.split("#")[-1])


def extract_number_from_id(node_id: str, locale: str = ""):
    return extract_node_id(node_id, locale).split("_").pop()


# print(extract_number_from_id("cpt_1.art_4.pt_1_eu_de", "eu_de"))


def deep_extract_literal(
    obj,
):
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
