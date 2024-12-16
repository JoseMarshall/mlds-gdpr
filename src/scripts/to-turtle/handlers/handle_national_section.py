from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_national_article import handle_national_article
from util import extract_all_numbers, deep_extract_literal, extract_node_id


def handle_national_section(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locale: str,
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
            URIRef(
                custom_namespaces["GDPR"]
                + extract_node_id(node_uri, locale)
                + "_abstract_"
                + locale
            ),
        )
    )

    for key, article in node["content"].items():
        if article["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)

            handle_national_article(
                graph,
                article,
                article_uri,
                node_uri,
                locale,
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
