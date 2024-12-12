from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_article import handle_article
from util import extract_all_numbers, deep_extract_literal, extract_node_id


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
        and (last_key_cmp[0] + "_" + locale) == last_key_cmp[1]
    ):
        return

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalExpression))
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].realizes,
            URIRef(custom_namespaces["GDPR"] + extract_node_id(node_uri)),
        )
    )

    for l in other_locales:
        node_translated_uri = URIRef(node_uri.removesuffix(f"_{locale}") + "_" + l)
        graph.add(
            (node_uri, custom_namespaces["ELI"].is_translation_of, node_translated_uri)
        )
        graph.add(
            (node_uri, custom_namespaces["ELI"].has_translation, node_translated_uri)
        )

    for key, article in node["content"].items():
        if article["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)

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
