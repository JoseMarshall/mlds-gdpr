import json
import rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, DCTERMS, RDFS
from file import make_path
from handlers.handle_chapter import handle_chapter


# Create an RDF graph
graph = rdflib.Graph()

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
graph.bind("gdpr", GDPR)
graph.bind("eli", ELI)
graph.bind("dct", DCTERMS)

# Define classes (types)
_GDPR = GDPR._GDPR
Chapter = GDPR.Chapter
Section = GDPR.Section
Article = GDPR.Article
Point = GDPR.Point
SubPoint = GDPR.SubPoint

# Add type definitions (RDF:type)
graph.add((_GDPR, RDF.type, ELI.LegalResource))
graph.add((Chapter, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Section, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Article, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Point, RDF.type, ELI.LegalResourceSubdivision))
graph.add((SubPoint, RDF.type, ELI.LegalResourceSubdivision))


# Optionally add labels
graph.add((_GDPR, RDFS.label, Literal("GDPR")))
graph.add((Chapter, RDFS.label, Literal("Chapter")))
graph.add((Section, RDFS.label, Literal("Section")))
graph.add((Article, RDFS.label, Literal("Article")))
graph.add((Point, RDFS.label, Literal("Point")))
graph.add((SubPoint, RDFS.label, Literal("SubPoint")))

locales = [
    "en",
    "pt",
    "it",
    "de",
]

for locale in locales:
    with open(make_path(f"src/datasets/gdpr-eu-{locale}.json"), "r") as f:
        data = json.load(f)

    # Start the recursive function
    for key, node in data.items():
        chapter_uri = URIRef(GDPR + key + "-" + locale)
        other_locales = [l for l in locales if l != locale]
        handle_chapter(graph, node, chapter_uri, locale, other_locales)

# Serialize the RDF graph in Turtle format
graph.serialize(
    format="turtle",
    encoding="utf-8",
    destination=make_path("src/datasets/rdfs/abstract.ttl"),
)
