from rdflib import URIRef, Namespace, Literal
from rdflib.namespace import RDF
from handle_national_subsubpoint import handle_national_subsubpoint

from util import add_description, extract_node_id


def handle_national_subpoint(
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
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )
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

    if isinstance(node["content"], list):
        graph.add(
            (
                node_uri,
                custom_namespaces["ELI"].description,
                Literal(node["content"][1]),
            )
        )
    elif isinstance(node["content"], str):
        add_description(graph, node, node_uri, parent_uri, locale, custom_namespaces)
    else:
        for key, subsubpoint in node["content"].items():
            if subsubpoint["classType"] == "SUBPOINT":
                add_description(
                    graph, subsubpoint, node_uri, parent_uri, locale, custom_namespaces
                )
            elif subsubpoint["classType"] == "SUBSUBPOINT":
                subsubpoint_uri = URIRef(
                    custom_namespaces["RGDPR"] + key + "_" + locale
                )
                graph.add(
                    (
                        node_uri,
                        custom_namespaces["ELI"].has_part,
                        subsubpoint_uri,
                    )
                )

                handle_national_subsubpoint(
                    graph,
                    subsubpoint,
                    subsubpoint_uri,
                    node_uri,
                    locale,
                    custom_namespaces,
                )
