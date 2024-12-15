import json
import rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS
from file import make_path
from handlers.handle_chapter import handle_chapter
from handlers.handle_abstract_chapter import handle_abstract_chapter
from handlers.handle_national_chapter import handle_national_chapter
from handlers.handle_national_part import handle_national_part
from handlers.handle_national_abstract_part import handle_national_abstract_part
from handlers.handle_national_abstract_chapter import handle_national_abstract_chapter


# Create an RDF graph
graph = rdflib.Graph()

# Define namespaces
GDPR = Namespace("http://example.org/gdpr#")
RGDPR = Namespace("http://example.org/rgdpr#")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
graph.bind("gdpr", GDPR)
graph.bind("rgdpr", RGDPR)
graph.bind("eli", ELI)

# Define classes (types)
_GDPR = GDPR.GDPR
Part = GDPR.Part
Chapter = GDPR.Chapter
Section = GDPR.Section
Article = GDPR.Article
Point = GDPR.Point
SubPoint = GDPR.SubPoint
SubSubPoint = GDPR.SubSubPoint

# Add type definitions (RDF:type)
graph.add((Part, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Chapter, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Section, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Article, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Point, RDF.type, ELI.LegalResourceSubdivision))
graph.add((SubPoint, RDF.type, ELI.LegalResourceSubdivision))
graph.add((SubSubPoint, RDF.type, ELI.LegalResourceSubdivision))


# Optionally add labels
graph.add((_GDPR, RDFS.label, Literal("GDPR")))
graph.add((Part, RDFS.label, Literal("Part")))
graph.add((Chapter, RDFS.label, Literal("Chapter")))
graph.add((Section, RDFS.label, Literal("Section")))
graph.add((Article, RDFS.label, Literal("Article")))
graph.add((Point, RDFS.label, Literal("Point")))
graph.add((SubPoint, RDFS.label, Literal("SubPoint")))
graph.add((SubSubPoint, RDFS.label, Literal("SubSubPoint")))

# GENERAL STRUCTURE GDPR
graph.add((_GDPR, RDF.type, ELI.LegalResource))
graph.add((_GDPR, ELI.has_part, Chapter))
graph.add((_GDPR, ELI.has_part, Part))

graph.add((Part, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Part, ELI.is_part_of, _GDPR))
graph.add((Part, ELI.has_part, Chapter))

graph.add((Chapter, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Chapter, ELI.is_part_of, _GDPR))
graph.add((Chapter, ELI.has_part, Section))
graph.add((Chapter, ELI.has_part, Article))

graph.add((Section, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Section, ELI.is_part_of, Chapter))
graph.add((Section, ELI.has_part, Article))

graph.add((Article, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Article, ELI.is_part_of, Chapter))
graph.add((Article, ELI.is_part_of, Section))
graph.add((Article, ELI.has_part, Point))

graph.add((Point, RDF.type, ELI.LegalResourceSubdivision))
graph.add((Point, ELI.is_part_of, Article))
graph.add((Point, ELI.has_part, SubPoint))

graph.add((SubPoint, RDF.type, ELI.LegalResourceSubdivision))
graph.add((SubPoint, ELI.is_part_of, Point))
graph.add((SubPoint, ELI.has_part, SubSubPoint))

graph.add((SubSubPoint, RDF.type, ELI.LegalResourceSubdivision))
graph.add((SubSubPoint, ELI.is_part_of, SubPoint))


locales = [
    "eu_en",
    "eu_pt",
    "eu_it",
    "eu_de",
]

## ONE LEVEL DOWN ##
with open(make_path(f"src/datasets/gdpr-eu-en.json"), "r") as f:
    data = json.load(f)
    # Start the recursive function
    for key, node in data.items():
        chapter_uri = URIRef(GDPR + key)
        handle_abstract_chapter(
            graph,
            node,
            chapter_uri,
            locales,
            {
                "RGDPR": RGDPR,
                "GDPR": GDPR,
                "ELI": ELI,
            },
        )

# CONCRETE REALIZATION - USE OF rGDPR
graph.add(
    (
        URIRef(RGDPR + "gdpr_eu_en"),
        ELI.title,
        Literal(
            "Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation)"
        ),
    )
)
graph.add(
    (
        URIRef(RGDPR + "gdpr_eu_de"),
        ELI.title,
        Literal(
            "VERORDNUNG (EU) 2016/679 DES EUROPÄISCHEN PARLAMENTS UND DES RATES vom 27. April 2016 zum Schutz natürlicher Personen bei der Verarbeitung personenbezogener Daten, zum freien Datenverkehr und zur Aufhebung der Richtlinie 95/46/EG (Datenschutz-Grundverordnung)"
        ),
    )
)
graph.add(
    (
        URIRef(RGDPR + "gdpr_eu_it"),
        ELI.title,
        Literal(
            "REGOLAMENTO (UE) 2016/679 DEL PARLAMENTO EUROPEO E DEL CONSIGLIO del 27 aprile 2016 relativo alla protezione delle persone fisiche con riguardo al trattamento dei dati personali, nonché alla libera circolazione di tali dati e che abroga la direttiva 95/46/CE (regolamento generale sulla protezione dei dati)"
        ),
    )
)
graph.add(
    (
        URIRef(RGDPR + "gdpr_eu_pt"),
        ELI.title,
        Literal(
            "REGULAMENTO (UE) 2016/679 DO PARLAMENTO EUROPEU E DO CONSELHO de 27 de abril de 2016 relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais e à livre circulação desses dados e que revoga a Diretiva 95/46/CE (Regulamento Geral sobre a Proteção de Dados)"
        ),
    )
)


for locale in locales:
    rgdpr_uri = URIRef(RGDPR + f"gdpr_{locale}")
    graph.add((rgdpr_uri, RDF.type, ELI.LegalExpression))
    graph.add((rgdpr_uri, ELI.realizes, _GDPR))
    graph.add((_GDPR, ELI.is_realized_by, rgdpr_uri))
    graph.add((rgdpr_uri, ELI.language, Literal(locale.split("_")[1])))
    other_locales = [l for l in locales if l != locale]
    for l in other_locales:
        graph.add(
            (
                rgdpr_uri,
                ELI.is_translation_of,
                URIRef(RGDPR + f"gdpr_{l}"),
            )
        )
        graph.add(
            (
                rgdpr_uri,
                ELI.has_translation,
                URIRef(RGDPR + f"gdpr_{l}"),
            )
        )

    json_file_locale = locale.replace("_", "-")
    with open(make_path(f"src/datasets/gdpr-{json_file_locale}.json"), "r") as f:
        data = json.load(f)

    # Start the recursive function
    for key, node in data.items():
        chapter_uri = URIRef(RGDPR + key + "_" + locale)
        other_locales = [l for l in locales if l != locale]
        handle_chapter(
            graph,
            node,
            chapter_uri,
            locale,
            other_locales,
            {
                "RGDPR": RGDPR,
                "GDPR": GDPR,
                "ELI": ELI,
            },
        )

# National Implementation
graph.add(
    (
        URIRef(RGDPR + "gdpr_de"),
        ELI.title,
        Literal(
            "Gesetz zur Anpassung des Datenschutzrechts an die Verordnung (EU) 2016/679 und zur Umsetzung der Richtlinie (EU) 2016/680 (Datenschutz-Anpassungs- und -Umsetzungsgesetz EU – DSAnpUG-EU)"
        ),
    )
)
graph.add(
    (
        URIRef(RGDPR + "gdpr_pt"),
        ELI.title,
        Literal(
            "Aprova as regras relativas ao tratamento de dados pessoais para efeitos de prevenção, deteção, investigação ou repressão de infrações penais ou de execução de sanções penais, transpondo a Diretiva (UE) 2016/680 do Parlamento Europeu e do Conselho, de 27 de abril de 2016"
        ),
    )
)

national_locales = ["de", "pt"]
# National Abstract Implementation
for locale in national_locales:
    with open(make_path(f"src/datasets/gdpr-{locale}.json"), "r") as f:
        data = json.load(f)
        # Start the recursive function
        for key, node in data.items():
            node_uri = URIRef(GDPR + key + "_abstract_" + locale)

            if node["classType"] == "CHAPTER":
                handle_national_abstract_chapter(
                    graph,
                    node,
                    node_uri,
                    None,
                    locale,
                    {
                        "RGDPR": RGDPR,
                        "GDPR": GDPR,
                        "ELI": ELI,
                    },
                )
            elif node["classType"] == "PART":
                handle_national_abstract_part(
                    graph,
                    node,
                    node_uri,
                    locale,
                    {
                        "RGDPR": RGDPR,
                        "GDPR": GDPR,
                        "ELI": ELI,
                    },
                )

# National Concrete Implementation

for locale in national_locales:
    rgdpr_uri = URIRef(RGDPR + f"gdpr_{locale}")
    graph.add((rgdpr_uri, RDF.type, ELI.LegalExpression))
    graph.add((rgdpr_uri, ELI.language, Literal(locale)))
    graph.add(
        (
            rgdpr_uri,
            ELI.ensures_implementation_of,
            URIRef(RGDPR + "gdpr_eu_en"),
        )
    )
    graph.add(
        (
            URIRef(RGDPR + "gdpr_eu_en"),
            ELI.implementation_ensured_by,
            rgdpr_uri,
        )
    )
    graph.add((rgdpr_uri, ELI.realizes, _GDPR))
    graph.add((_GDPR, ELI.is_realized_by, rgdpr_uri))

    with open(make_path(f"src/datasets/gdpr-{locale}.json"), "r") as f:
        data = json.load(f)
        for key, node in data.items():
            node_uri = URIRef(RGDPR + key + "_" + locale)

            if node["classType"] == "CHAPTER":
                handle_national_chapter(
                    graph,
                    node,
                    node_uri,
                    None,
                    locale,
                    {
                        "RGDPR": RGDPR,
                        "GDPR": GDPR,
                        "ELI": ELI,
                    },
                )
            elif node["classType"] == "PART":
                handle_national_part(
                    graph,
                    node,
                    node_uri,
                    locale,
                    {
                        "RGDPR": RGDPR,
                        "GDPR": GDPR,
                        "ELI": ELI,
                    },
                )


# Serialize the RDF graph in Turtle format
graph.serialize(
    format="turtle",
    encoding="utf-8",
    destination=make_path("src/datasets/rdfs/abstract.ttl"),
)
