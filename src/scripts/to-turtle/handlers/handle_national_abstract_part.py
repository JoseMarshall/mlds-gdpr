import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Namespace
from rdflib.namespace import RDF
from handle_national_abstract_chapter import handle_national_abstract_chapter

from util import extract_node_id


def handle_national_abstract_part(
    graph,
    node,
    node_uri: URIRef,
    locale: str,
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Part))
    realized_uri = URIRef(
        custom_namespaces["RGDPR"]
        + extract_node_id(node_uri, "abstract_" + locale)
        + "_"
        + locale
    )
    graph.add((node_uri, custom_namespaces["ELI"].is_realized_by, realized_uri))

    for key, value in node["content"].items():

        if value["classType"] == "CHAPTER":
            chapter_uri = URIRef(
                custom_namespaces["GDPR"] + key + "_abstract_" + locale
            )
            graph.add((node_uri, custom_namespaces["ELI"].has_part, chapter_uri))
            handle_national_abstract_chapter(
                graph,
                value,
                chapter_uri,
                node_uri,
                locale,
                custom_namespaces,
            )
