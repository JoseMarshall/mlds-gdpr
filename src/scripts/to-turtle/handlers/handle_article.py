from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_point import handle_point
from util import extract_all_numbers

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")

# gdpr:article10 a eli:LegalResourceSubdivision,
#         GDPRtEXT:Article ;
#     eli:is_part_of gdpr:GDPR,
#         gdpr:chapterII ;
#     eli:number "10"^^xsd:string ;
#     eli:title_alternative "Article 10"^^xsd:string ;
#     eli:is_translation_of gdpr:article1-pt,
#                           gdpr:article1-fr,
#                           gdpr:article1-de ;
#     eli:has_translation gdpr:article1-pt,
#                          gdpr:article1-fr,
#                          gdpr:article1-de .


def handle_article(graph, node, node_uri, parent_uri, locale, other_locales):
    graph.add((node_uri, RDF.type, ELI.LegalResourceSubdivision))
    graph.add((node_uri, RDF.type, GDPR.Article))
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

    for key, point in node["content"].items():
        if point["classType"] == "POINT":
            point_uri = URIRef(GDPR + key + "-" + locale)
            handle_point(graph, point, point_uri, node_uri, locale, other_locales)
        elif point["classType"] == "TITLE_ID":
            number = extract_all_numbers(point["content"])
            graph.add((node_uri, ELI.number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    ELI.title_alternative,
                    Literal(point["content"]),
                )
            )
        elif point["classType"] == "TITLE":
            graph.add((node_uri, ELI.description, Literal(node["content"])))
