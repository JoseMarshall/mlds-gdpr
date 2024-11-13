from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_subpoint import handle_subpoint
from util import extract_all_numbers

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")

# gdpr:article27-2 a eli:LegalResourceSubdivision,
#         GDPRtEXT:Point ;
#     eli:description "The obligation laid down in paragraph 1 of this Article shall not apply to:"^^xsd:string ;
#     eli:is_part_of gdpr:GDPR,
#         gdpr:article27,
#         gdpr:chapterIV,
#         gdpr:chapterIV-1 ;
#     eli:number "2"^^xsd:string ;
#     eli:title_alternative "Article27(2)"^^xsd:string ;
#     eli:is_translation_of gdpr:point1-pt,
#                           gdpr:point1-fr,
#                           gdpr:point1-de ;
#     eli:has_translation gdpr:point1-pt,
#                          gdpr:point1-fr,
#                          gdpr:point1-de .


def add_description(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
):
    graph.add((node_uri, ELI.description, Literal(node["content"])))
    # get the number from the beginning of the string using regex

    number = extract_all_numbers(node["content"][0:5])
    graph.add((node_uri, ELI.number, Literal(number)))
    for parent_title_alternative in graph.objects(parent_uri, ELI.title_alternative):
        graph.add(
            (
                node_uri,
                ELI.title_alternative,
                Literal(parent_title_alternative + "-" + number),
            )
        )


def handle_point(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    other_locales: list[str],
):
    last_key_cmp = node_uri.split(".")[-2:]
    if (
        last_key_cmp.__len__() == 2
        and (last_key_cmp[0] + "-" + locale) == last_key_cmp[1]
    ):
        return

    graph.add((node_uri, RDF.type, ELI.LegalResourceSubdivision))
    graph.add((node_uri, RDF.type, GDPR.Point))
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

    if isinstance(node["content"], str):
        add_description(graph, node, node_uri, parent_uri)
    else:
        for key, subpoint in node["content"].items():
            if subpoint["classType"] == "POINT":
                add_description(graph, subpoint, node_uri, parent_uri)

            subpoint_uri = URIRef(GDPR + key + "-" + locale)
            handle_subpoint(
                graph, subpoint, subpoint_uri, node_uri, locale, other_locales
            )
