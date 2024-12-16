from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_national_point import handle_national_point
from util import extract_all_numbers, deep_extract_literal, extract_node_id
import os
import json


def handle_national_article(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
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
            URIRef(
                custom_namespaces["GDPR"]
                + extract_node_id(node_uri, locale)
                + "_abstract_"
                + locale
            ),
        )
    )

    # New loop to handle relatedArticles
    if "relatedArticles" in node:
        # Load all articles from the JSON file
        json_file_path = os.path.join(os.path.dirname(__file__), "eu_articles.json")
        with open(json_file_path, "r") as json_file:
            eu_articles = json.load(json_file)

        for related_article in node["relatedArticles"]:
            pattern = "art_" + related_article
            # Find the matching article in eu_articles
            matching_strings = [s for s in eu_articles if pattern in s]

            related_article_uri = URIRef(
                custom_namespaces["RGDPR"] + matching_strings[0] + "_eu_en"
            )
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].ensures_implementation_of,
                    related_article_uri,
                )
            )
            graph.add(
                (
                    related_article_uri,
                    custom_namespaces["ELI"].implementation_ensured_by,
                    node_uri,
                )
            )

    for key, point in node["content"].items():
        if point["classType"] == "POINT":
            point_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)

            handle_national_point(
                graph,
                point,
                point_uri,
                node_uri,
                locale,
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
