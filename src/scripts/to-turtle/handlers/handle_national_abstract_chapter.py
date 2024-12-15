import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_national_abstract_article import handle_national_abstract_article
from handle_national_abstract_section import handle_national_abstract_section
from util import extract_node_id


def handle_national_abstract_chapter(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Chapter))
    realized_uri = URIRef(
        custom_namespaces["RGDPR"]
        + extract_node_id(node_uri, "abstract_" + locale)
        + "_"
        + locale
    )
    graph.add((node_uri, custom_namespaces["ELI"].is_realized_by, realized_uri))

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
            article_uri = URIRef(
                custom_namespaces["GDPR"] + key + "_abstract_" + locale
            )
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].has_part,
                    article_uri,
                )
            )
            handle_national_abstract_article(
                graph,
                value,
                article_uri,
                node_uri,
                locale,
                custom_namespaces,
            )

        elif value["classType"] == "SECTION":
            section_uri = URIRef(
                custom_namespaces["GDPR"] + key + "_abstract_" + locale
            )
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].has_part,
                    section_uri,
                )
            )
            handle_national_abstract_section(
                graph,
                value,
                section_uri,
                node_uri,
                locale,
                custom_namespaces,
            )
