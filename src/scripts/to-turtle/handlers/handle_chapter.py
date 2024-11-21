import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from handle_section import handle_section
from util import extract_romans, deep_extract_literal


# gdpr:chapterI a eli:LegalResourceSubdivision,
#         GDPRtEXT:Chapter ;
#     eli:is_part_of gdpr:GDPR ;
#     eli:number "I"^^xsd:string ;
#     eli:title "General provisions"^^xsd:string ;
#     eli:title_alternative "Chapter I"^^xsd:string ;
#     eli:is_translation_of gdpr:chapterI-pt,
#                           gdpr:chapterI-fr,
#                           gdpr:chapterI-de ;
#     eli:has_translation gdpr:chapterI-pt,
#                          gdpr:chapterI-fr,
#                          gdpr:chapterI-de .


def handle_chapter(
    graph,
    node,
    node_uri: URIRef,
    locale: str,
    other_locales: list[str],
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalResourceSubdivision))
    graph.add(
        (node_uri, custom_namespaces["ELI"].realizes, custom_namespaces["GDPR"].Chapter)
    )
    graph.add(
        (
            custom_namespaces["GDPR"].Chapter,
            custom_namespaces["ELI"].is_realized_by,
            node_uri,
        )
    )
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            custom_namespaces["GDPR"]._GDPR,
        )
    )
    for l in other_locales:
        node_translated_uri = URIRef(node_uri.removesuffix(f"-{locale}") + "-" + l)
        graph.add(
            (node_uri, custom_namespaces["ELI"].is_translation_of, node_translated_uri)
        )
        graph.add(
            (node_uri, custom_namespaces["ELI"].has_translation, node_translated_uri)
        )

    for key, value in node["content"].items():
        # print(key, value, "\n\n")
        if value["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["GDPR"] + key + "-" + locale)
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
            section_uri = URIRef(custom_namespaces["GDPR"] + key + "-" + locale)
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
