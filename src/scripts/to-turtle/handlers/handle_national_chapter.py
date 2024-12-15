import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_national_article import handle_national_article
from handle_national_section import handle_national_section
from util import extract_romans, deep_extract_literal


def handle_national_chapter(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalExpression))
    graph.add((node_uri, custom_namespaces["ELI"].language, Literal(locale)))

    if parent_uri:
        graph.add(
            (
                node_uri,
                custom_namespaces["ELI"].is_part_of,
                parent_uri,
            )
        )

    for key, value in node["content"].items():
        if value["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].has_part,
                    article_uri,
                )
            )
            handle_national_article(
                graph,
                value,
                article_uri,
                node_uri,
                locale,
                custom_namespaces,
            )

        elif value["classType"] == "SECTION":
            section_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].has_part,
                    section_uri,
                )
            )
            handle_national_section(
                graph,
                value,
                section_uri,
                node_uri,
                locale,
                custom_namespaces,
            )

        elif value["classType"] == "TITLE_ID" or value["classType"] == "CHAPTER":
            number = extract_romans(value["content"])
            graph.add((node_uri, custom_namespaces["ELI"].number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].title_alternative,
                    Literal(value["content"]),
                )
            )

        elif value["classType"] == "TITLE":
            title = deep_extract_literal(value["content"])
            graph.add((node_uri, custom_namespaces["ELI"].title, Literal(title)))
