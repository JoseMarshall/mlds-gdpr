from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_point import handle_point
from util import extract_all_numbers, extract_node_id, deep_extract_literal
import os
import json

def handle_article(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    other_locales: list[str],
    custom_namespaces: dict[str, Namespace],
):
    last_key_cmp = node_uri.split(".")[-2:]
    if (
        last_key_cmp.__len__() == 2
        and (last_key_cmp[0] + "_" + locale) == last_key_cmp[1]
    ):
        return

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalExpression))
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].realizes,
            URIRef(custom_namespaces["GDPR"] + extract_node_id(node_uri)),
        )
    )
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )
    
# New loop to handle relatedArticles
    if "relatedArticles" in node:
        # Load all articles from the JSON file
        json_file_path = os.path.join(os.path.dirname(__file__), "all_articles.json")
        with open(json_file_path, "r") as json_file:
            all_articles = json.load(json_file)

        for related_article in node["relatedArticles"]:
            pattern = "art_" + related_article
            matching_strings = [s for s in all_articles if pattern in s]
            # Find the matching article in all_articles
            if matching_strings:  # Check if the key contains the related article value
                related_article_uri = URIRef(custom_namespaces["RGDPR"] + matching_strings[0])
                graph.add(
                    (
                        node_uri,
                        custom_namespaces["ELI"].ensures_implementation_of,
                        related_article_uri,
                    )
                )
                
    for l in other_locales:
        node_translated_uri = URIRef(node_uri.removesuffix(f"_{locale}") + "_" + l)
        graph.add(
            (node_uri, custom_namespaces["ELI"].is_translation_of, node_translated_uri)
        )
        graph.add(
            (node_uri, custom_namespaces["ELI"].has_translation, node_translated_uri)
        )

    for key, point in node["content"].items():
        if point["classType"] == "POINT":
            point_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].has_part,
                    point_uri,
                )
            )
            handle_point(
                graph,
                point,
                point_uri,
                node_uri,
                locale,
                other_locales,
                custom_namespaces,
            )
        elif point["classType"] == "TITLE_ID" or point["classType"] == "ARTICLE":
            number = extract_all_numbers(point["content"])
            graph.add((node_uri, custom_namespaces["ELI"].number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].title_alternative,
                    Literal(deep_extract_literal(point["content"])),
                )
            )
        elif point["classType"] == "TITLE":
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].description,
                    Literal(deep_extract_literal(point["content"])),
                )
            )