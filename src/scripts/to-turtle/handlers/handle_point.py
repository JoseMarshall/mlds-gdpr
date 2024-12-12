from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_subpoint import handle_subpoint
from util import extract_all_numbers, extract_node_id


def add_description(
    graph,
    node,
    node_uri: URIRef,
    parent_uri: URIRef,
    custom_namespaces: dict[str, Namespace],
):
    graph.add(
        (node_uri, custom_namespaces["ELI"].description, Literal(node["content"]))
    )
    # get the number from the beginning of the string using regex

    number = extract_all_numbers(node["content"][0:5])
    graph.add((node_uri, custom_namespaces["ELI"].number, Literal(number)))
    for parent_title_alternative in graph.objects(
        parent_uri, custom_namespaces["ELI"].title_alternative
    ):
        graph.add(
            (
                node_uri,
                custom_namespaces["ELI"].title_alternative,
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

    if isinstance(node["content"], str):
        add_description(graph, node, node_uri, parent_uri, custom_namespaces)
    else:
        for key, subpoint in node["content"].items():
            if subpoint["classType"] == "POINT":
                add_description(
                    graph, subpoint, node_uri, parent_uri, custom_namespaces
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
