from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_abstract_article import handle_abstract_article
from util import extract_node_id


def handle_abstract_section(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    locales: list[str],
    custom_namespaces: dict[str, Namespace],
):
    last_key_cmp = node_uri.split(".")[-2:]
    if last_key_cmp.__len__() == 2 and (last_key_cmp[0]) == last_key_cmp[1]:
        return

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Section))
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )
    for l in locales:
        realized_uri = URIRef(
            custom_namespaces["RGDPR"] + extract_node_id(node_uri) + "_" + l
        )
        graph.add((node_uri, custom_namespaces["ELI"].is_realized_by, realized_uri))

    for key, article in node["content"].items():
        if article["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["GDPR"] + key)
            handle_abstract_article(
                graph,
                article,
                article_uri,
                node_uri,
                locales,
                custom_namespaces,
            )