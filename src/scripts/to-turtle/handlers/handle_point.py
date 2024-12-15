from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_subpoint import handle_subpoint
from util import extract_node_id, add_description


def handle_point(
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
            URIRef(custom_namespaces["GDPR"] + extract_node_id(node_uri, locale)),
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

    if isinstance(node["content"], str):
        add_description(graph, node, node_uri, parent_uri, locale, custom_namespaces)
    else:
        for key, subpoint in node["content"].items():
            if subpoint["classType"] == "POINT":
                add_description(
                    graph, subpoint, node_uri, parent_uri, locale, custom_namespaces
                )
            elif subpoint["classType"] == "SUBPOINT":
                subpoint_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)

                handle_subpoint(
                    graph,
                    subpoint,
                    subpoint_uri,
                    node_uri,
                    locale,
                    other_locales,
                    custom_namespaces,
                )
