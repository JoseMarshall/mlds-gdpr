from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from util import extract_all_numbers, deep_extract_literal

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")

# gdpr:chapterIV-5 a eli:LegalResourceSubdivision,
#         GDPRtEXT:Section ;
#     eli:is_part_of gdpr:GDPR,
#         gdpr:chapterIV ;
#     eli:number "5"^^xsd:string ;
#     eli:title "Codes of conduct and certification"^^xsd:string ;
#     eli:title_alternative "Section 5"^^xsd:string ;
#     eli:is_translation_of gdpr:section1-pt,
#                           gdpr:section1-fr,
#                           gdpr:section1-de ;
#     eli:has_translation gdpr:section1-pt,
#                          gdpr:section1-fr,
#                          gdpr:section1-de .


def handle_section(graph, node, node_uri, parent_uri, locale, other_locales):
    graph.add((node_uri, RDF.type, ELI.LegalResourceSubdivision))
    graph.add((node_uri, RDF.type, GDPR.Section))
    graph.add(
        (
            node_uri,
            ELI.is_part_of,
            parent_uri,
        )
    )
    graph.add(
        (
            parent_uri,
            ELI.has_part,
            node_uri,
        )
    )
    for l in other_locales:
        node_translated_uri = URIRef(
            GDPR + node_uri.removesuffix(f"-{locale}") + "-" + l
        )
        graph.add((node_uri, ELI.is_translation_of, node_translated_uri))
        graph.add((node_uri, ELI.has_translation, node_translated_uri))

    # add all is_part_of from the parent
    for is_part_of in graph.objects(parent_uri, ELI.is_part_of):
        graph.add((node_uri, ELI.is_part_of, is_part_of))
        graph.add((is_part_of, ELI.has_part, node_uri))

    for key, article in node["content"].items():
        if article["classType"] == "ARTICLE":
            article_uri = URIRef(GDPR + key + "-" + locale)
            handle_article(graph, article, article_uri, node_uri, locale, other_locales)
        elif article["classType"] == "TITLE_ID" or article["classType"] == "SECTION":
            number = extract_all_numbers(article["content"])
            graph.add((node_uri, ELI.number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    ELI.title_alternative,
                    Literal(article["content"]),
                )
            )
        elif article["classType"] == "TITLE":
            title = deep_extract_literal(article["content"])
            graph.add((node_uri, ELI.description, Literal(title)))
