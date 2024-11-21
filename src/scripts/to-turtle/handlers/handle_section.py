from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from util import extract_all_numbers, deep_extract_literal


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


def handle_section(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
    other_locales: list[str],
    custom_namespaces: dict[str, Namespace],
):
    last_key_cmp = node_uri.split(".")[-2:]
    if (
        last_key_cmp.__len__() == 2
        and (last_key_cmp[0] + "-" + locale) == last_key_cmp[1]
    ):
        return

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalResourceSubdivision))
    graph.add(
        (node_uri, custom_namespaces["ELI"].realizes, custom_namespaces["GDPR"].Section)
    )
    graph.add(
        (
            custom_namespaces["GDPR"].Section,
            custom_namespaces["ELI"].is_realized_by,
            node_uri,
        )
    )
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )
    graph.add(
        (
            parent_uri,
            custom_namespaces["ELI"].has_part,
            node_uri,
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

    # add all is_part_of from the parent
    for is_part_of in graph.objects(parent_uri, custom_namespaces["ELI"].is_part_of):
        graph.add((node_uri, custom_namespaces["ELI"].is_part_of, is_part_of))
        graph.add((is_part_of, custom_namespaces["ELI"].has_part, node_uri))

    for key, article in node["content"].items():
        if article["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["GDPR"] + key + "-" + locale)
            handle_article(
                graph,
                article,
                article_uri,
                node_uri,
                locale,
                other_locales,
                custom_namespaces,
            )
        elif article["classType"] == "TITLE_ID" or article["classType"] == "SECTION":
            number = extract_all_numbers(article["content"])
            graph.add((node_uri, custom_namespaces["ELI"].number, Literal(number)))
            graph.add(
                (
                    node_uri,
                    custom_namespaces["ELI"].title_alternative,
                    Literal(article["content"]),
                )
            )
        elif article["classType"] == "TITLE":
            title = deep_extract_literal(article["content"])
            graph.add((node_uri, custom_namespaces["ELI"].description, Literal(title)))
