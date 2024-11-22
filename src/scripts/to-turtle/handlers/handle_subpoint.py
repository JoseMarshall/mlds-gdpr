from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from util import extract_node_id


def handle_subpoint(
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
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )
    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].description,
            Literal(node["content"][1]),
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

    for parent_title_alternative in graph.objects(
        parent_uri, custom_namespaces["ELI"].title_alternative
    ):
        graph.add(
            (
                node_uri,
                custom_namespaces["ELI"].title_alternative,
                Literal(parent_title_alternative + "-" + node["content"][0]),
            )
        )
