import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF
from handle_national_chapter import handle_national_chapter

from util import deep_extract_literal, extract_node_id


def handle_national_part(
    graph,
    node,
    node_uri: URIRef,
    locale: str,
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["ELI"].LegalExpression))
    graph.add((node_uri, custom_namespaces["ELI"].language, Literal(locale)))
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

    for key, value in node["content"].items():

        if value["classType"] == "PART":
            title = deep_extract_literal(value["content"])
            graph.add((node_uri, custom_namespaces["ELI"].title, Literal(title)))

        elif value["classType"] == "CHAPTER":
            chapter_uri = URIRef(custom_namespaces["RGDPR"] + key + "_" + locale)

            handle_national_chapter(
                graph,
                value,
                chapter_uri,
                node_uri,
                locale,
                custom_namespaces,
            )
