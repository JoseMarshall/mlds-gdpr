from rdflib import URIRef, Namespace
from rdflib.namespace import RDF
from handle_abstract_point import handle_abstract_point
from util import extract_node_id


def handle_abstract_article(
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

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Article))
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

    for key, point in node["content"].items():
        if point["classType"] == "POINT":
            point_uri = URIRef(custom_namespaces["GDPR"] + key)
            graph.add((node_uri, custom_namespaces["ELI"].has_part, point_uri))

            handle_abstract_point(
                graph,
                point,
                point_uri,
                node_uri,
                locales,
                custom_namespaces,
            )
