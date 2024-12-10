from rdflib import URIRef, Namespace
from rdflib.namespace import RDF
from handle_abstract_article import handle_abstract_article
from handle_abstract_section import handle_abstract_section
from util import extract_node_id


def handle_abstract_chapter(
    graph,
    node,
    node_uri: URIRef,
    locales: list[str],
    custom_namespaces: dict[str, Namespace],
):

    graph.add((node_uri, RDF.type, custom_namespaces["GDPR"].Chapter))

    for l in locales:
        realized_uri = URIRef(
            custom_namespaces["RGDPR"] + extract_node_id(node_uri) + "_" + l
        )
        graph.add((node_uri, custom_namespaces["ELI"].is_realized_by, realized_uri))

    for key, value in node["content"].items():
        if value["classType"] == "ARTICLE":
            article_uri = URIRef(custom_namespaces["GDPR"] + key)
            graph.add((node_uri, custom_namespaces["ELI"].has_part, article_uri))
            handle_abstract_article(
                graph,
                value,
                article_uri,
                node_uri,
                locales,
                custom_namespaces,
            )

        elif value["classType"] == "SECTION":
            section_uri = URIRef(custom_namespaces["GDPR"] + key)
            graph.add((node_uri, custom_namespaces["ELI"].has_part, section_uri))
            handle_abstract_section(
                graph,
                value,
                section_uri,
                node_uri,
                locales,
                custom_namespaces,
            )
