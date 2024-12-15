import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from handle_section import handle_section
from util import extract_romans, deep_extract_literal, extract_node_id


def handle_chapter(
    graph,
    node,
    node_uri: URIRef,
    locale: str,
    other_locales: list[str],
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalExpression))
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].realizes,
            URIRef(custom_namespaces["GDPR"] + extract_node_id(node_uri, locale)),
        )
    )
    graph.add(
        (node_uri, custom_namespaces["ELI"].language, Literal(locale.split("_")[1]))
    )

    for l in other_locales:
        node_translated_uri = URIRef(node_uri.removesuffix(f"_{locale}") + "_" + l)
        graph.add(
            (node_uri, custom_namespaces["ELI"].is_translation_of, node_translated_uri)
        )
        graph.add(
            (node_uri, custom_namespaces["ELI"].has_translation, node_translated_uri)
        )

    for key, value in node["content"].items():
        if value["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)
            handle_article(
                graph,
                value,
                article_uri,
                node_uri,
                locale,
                other_locales,
                custom_namespaces,
            )

        elif value["classType"] == "SECTION":
            section_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)
            handle_section(
                graph,
                value,
                section_uri,
                node_uri,
                locale,
                other_locales,
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
