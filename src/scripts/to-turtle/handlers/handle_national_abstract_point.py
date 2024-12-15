from rdflib import URIRef, Namespace
from rdflib.namespace import RDF
from handle_national_abstract_subpoint import handle_national_abstract_subpoint
from util import extract_node_id


def handle_national_abstract_point(
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

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Point))
    realized_uri = URIRef(
        custom_namespaces["RGDPR"]
        + extract_node_id(node_uri, "abstract_" + locale)
        + "_"
        + locale
    )
    graph.add((node_uri, custom_namespaces["ELI"].is_realized_by, realized_uri))

    graph.add(
        (
            node_uri,
            custom_namespaces["ELI"].is_part_of,
            parent_uri,
        )
    )

    if not isinstance(node["content"], str):
        for key, subpoint in node["content"].items():

            if subpoint["classType"] == "SUBPOINT":
                subpoint_uri = URIRef(
                    custom_namespaces["GDPR"] + key + "_abstract_" + locale
                )
                graph.add(
                    (
                        node_uri,
                        custom_namespaces["ELI"].has_part,
                        subpoint_uri,
                    )
                )

                handle_national_abstract_subpoint(
                    graph,
                    subpoint,
                    subpoint_uri,
                    node_uri,
                    locale,
                    custom_namespaces,
                )