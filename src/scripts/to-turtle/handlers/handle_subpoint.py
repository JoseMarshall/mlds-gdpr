from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")

# gdpr:article12-5-b a eli:LegalResourceSubdivision,
#         GDPRtEXT:SubPoint ;
#     eli:description "refuse to act on the request."^^xsd:string ;
#     eli:is_part_of gdpr:GDPR,
#         gdpr:article12,
#         gdpr:article12-5,
#         gdpr:chapterIII,
#         gdpr:chapterIII-1 ;
#     eli:number "b"^^xsd:string ;
#     eli:title_alternative "Article12(5)(b)"^^xsd:string ;
#     eli:is_translation_of gdpr:subpoint1-pt,
#                           gdpr:subpoint1-fr,
#                           gdpr:subpoint1-de ;
#     eli:has_translation gdpr:subpoint1-pt,
#                          gdpr:subpoint1-fr,
#                          gdpr:subpoint1-de .


def handle_subpoint(
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
    graph.add((node_uri, RDF.type, GDPR.SubPoint))
    graph.add((node_uri, ELI.number, Literal(node["content"][0])))
    graph.add((node_uri, ELI.description, Literal(node["content"][1])))

    for l in other_locales:
        node_translated_uri = URIRef(
            GDPR + node_uri.removesuffix(f"-{locale}") + "-" + l
        )
        graph.add((node_uri, ELI.is_translation_of, node_translated_uri))
        graph.add((node_uri, ELI.has_translation, node_translated_uri))

    for parent_title_alternative in graph.objects(parent_uri, ELI.title_alternative):
        graph.add(
            (
                node_uri,
                ELI.title_alternative,
                Literal(parent_title_alternative + "-" + node["content"][0]),
            )
        )
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

    # add all is_part_of from the parent
    for is_part_of in graph.objects(parent_uri, ELI.is_part_of):
        graph.add((node_uri, ELI.is_part_of, is_part_of))
        graph.add((is_part_of, ELI.has_part, node_uri))
