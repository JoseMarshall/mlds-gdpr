import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from handle_section import handle_section
from util import extract_romans, deep_extract_literal


# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")

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
    graph, node, node_uri: URIRef, locale: str, other_locales: list[str]
):

    graph.add((node_uri, RDF.type, ELI.LegalResourceSubdivision))
    graph.add((node_uri, RDF.type, GDPR.Chapter))
    graph.add(
        (
            node_uri,
            ELI.is_part_of,
            GDPR._GDPR,
        )
    )
    for l in other_locales:
        node_translated_uri = URIRef(
            GDPR + node_uri.removesuffix(f"-{locale}") + "-" + l
        )
        graph.add((node_uri, ELI.is_translation_of, node_translated_uri))
        graph.add((node_uri, ELI.has_translation, node_translated_uri))

    for key, value in node["content"].items():
        # print(key, value, "\n\n")
        if value["classType"] == "ARTICLE":
            article_uri = URIRef(GDPR + key + "-" + locale)
            handle_article(graph, value, article_uri, node_uri, locale, other_locales)

        elif value["classType"] == "SECTION":
            section_uri = URIRef(GDPR + key + "-" + locale)
            handle_section(graph, value, section_uri, node_uri, locale, other_locales)

        elif value["classType"] == "TITLE_ID" or value["classType"] == "CHAPTER":
            number = extract_romans(value["content"])
            graph.add((node_uri, ELI.number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    ELI.title_alternative,
                    Literal(value["content"]),
                )
            )

        elif value["classType"] == "TITLE":
            title = deep_extract_literal(value["content"])
            graph.add((node_uri, ELI.title, Literal(title)))
