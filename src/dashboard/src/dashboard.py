import streamlit as st
from rdflib import Graph, URIRef, Literal
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from unidecode import unidecode  # For accent-insensitive filtering
import urllib.parse

def generate_hyperlink(entity_uri, label):
    encoded_uri = urllib.parse.quote(entity_uri)
    return f'<a href="?entity={encoded_uri}" target="_self">{label}</a>'



st.set_page_config(page_title="Ontology Dashboard", layout="wide")

# Helper function to determine origin based on entity name
def determine_origin(entity_name):
    if entity_name.endswith("eu_en"):
        return "EU GDPR - English"
    elif entity_name.endswith("eu_de"):
        return "EU GDPR - Deutsch"
    elif entity_name.endswith("eu_pt"):
        return "EU GDPR - Português"
    elif entity_name.endswith("eu_it"):
        return "EU GDPR - Italiano"
    elif entity_name.endswith("_en"):
        return "National GDPR - England"
    elif entity_name.endswith("_de"):
        return "National GDPR - Deutschland"
    elif entity_name.endswith("_it"):
        return "National GDPR - Italia"
    elif entity_name.endswith("_pt"):
        return "National GDPR - Portugal"
    return "Unknown Origin"

@st.cache_resource
def load_ontology():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "abstract_updated.ttl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ontology file not found at: {file_path}")
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

ontology_graph = load_ontology()

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose a section", ["Overview", "Search Ontology", "Entity Profile", "Visualize Ontology"])

# Sidebar SPARQL Help Section
st.sidebar.subheader("SPARQL Query Examples")
st.sidebar.write("### Available Properties:")
st.sidebar.write("- `eli:description` - Entity description")
st.sidebar.write("- `eli:title_alternative` - Alternative title")
st.sidebar.write("- `eli:implementation_of` - Implementation reference")
st.sidebar.write("- `eli:implementation_ensured_by` - Ensured implementation")

st.sidebar.write("### Filtering Example:")
st.sidebar.code("""
PREFIX eli: <http://data.europa.eu/eli/ontology#>
SELECT ?subject ?description ?title_alt
WHERE {
    ?subject eli:description ?description .
    FILTER(CONTAINS(?description, "example"))
}
""")

# State Management
if "selected_entity" not in st.session_state:
    st.session_state["selected_entity"] = None
    
# Function to display entity profile based on SPARQL query
def display_entity_profile(entity_uri):
    st.header("Entity Profile")
    st.write(f"Entity: **{entity_uri.split('#')[-1]}**")  # Display entity name

    # SPARQL Query to fetch predicate-object pairs for the entity
    query = f"""
    PREFIX eli: <http://data.europa.eu/eli/ontology#>
    SELECT ?predicate ?object
    WHERE {{
        <{entity_uri}> ?predicate ?object .
    }}
    """
    try:
        # Execute query
        results = ontology_graph.query(query)
        data = []

        for row in results:
            predicate = str(row[0]).split("#")[-1] if row[0] else "N/A"
            obj = str(row[1]) if row[1] else "N/A"
            data.append({"Predicate": predicate, "Object": obj})

        if data:
            st.table(data)  # Display results in a table
        else:
            st.write("No data found for the selected entity.")
    except Exception as e:
        st.error(f"Error executing SPARQL query: {e}")

# Handle Entity Profile Section
if "entity" in st.query_params:
    import urllib.parse

    # Decode the URI passed in the query parameter
    entity_uri = urllib.parse.unquote(st.query_params["entity"][0])
    if entity_uri:
        display_entity_profile(entity_uri)
    else:
        st.write("No entity selected.")

# Entity Profile Section
if "entity" in st.query_params:
    import urllib.parse

    # Decode the URI from query params
    entity_uri = urllib.parse.unquote(st.query_params["entity"][0])
    if entity_uri:
        st.header(f"Entity Profile: {entity_uri.split('#')[-1]}")

        # Ensure the entity URI is wrapped in <>
        query = f"""
        PREFIX eli: <http://data.europa.eu/eli/ontology#>
        SELECT ?predicate ?object
        WHERE {{
            <{entity_uri}> ?predicate ?object .
        }}
        """
        try:
            results = ontology_graph.query(query)
            if results:
                data = []
                for row in results:
                    predicate = str(row[0]).split("#")[-1] if row[0] else "N/A"
                    obj = str(row[1]) if row[1] else "N/A"
                    data.append({"Predicate": predicate, "Object": obj})
                st.table(data)  # Display data in a table
            else:
                st.write("No data found for the selected entity.")
        except Exception as e:
            st.error(f"Error executing SPARQL query: {e}")
    else:
        st.write("No entity selected.")




if section == "Overview":
    st.header("Ontology Overview")
    st.write(f"Number of triples: {len(ontology_graph)}")
    st.write("### Classes and Properties")
    classes = set(ontology_graph.subjects())
    st.write(f"Classes: {len(classes)}")

elif section == "Search Ontology":
    st.header("Search Ontology")

    query_mode = st.radio("Query Mode", ["SPARQL Query", "Keyword Search"])

    if query_mode == "SPARQL Query":
        query = st.text_area("Enter your SPARQL query:", """
            PREFIX eli: <http://data.europa.eu/eli/ontology#>
            SELECT ?subject ?description ?title_alt
            WHERE {
                ?subject eli:description ?description ;
                         eli:title_alternative ?title_alt .
            }
        """, height=200)
        if st.button("Run SPARQL Query"):
            try:
                results = ontology_graph.query(query)
                data = []
                for row in results:
                    entity_uri = str(row[0])
                    subject = entity_uri.split("#")[-1] if len(row) > 0 else ""
                    description = str(row[1]) if len(row) > 1 else ""
                    title_alt = str(row[2]) if len(row) > 2 else ""
                    origin = determine_origin(subject)
                    linked_query = f"""
                    PREFIX eli: <http://data.europa.eu/eli/ontology#>
                    SELECT ?related
                    WHERE {{
                        <{entity_uri}> eli:implementation_of|eli:implementation_ensured_by ?related .
                    }}
                    """
                    linked_results = ontology_graph.query(linked_query)
                    related_articles = [
                        generate_hyperlink(str(linked_row[0]), f"{str(linked_row[0]).split('#')[-1]} ({determine_origin(str(linked_row[0]).split('#')[-1])})")
                        for linked_row in linked_results
                    ]
                    data.append({
                        "Origin": origin,
                        "Entity": generate_hyperlink(entity_uri, subject),
                        "Title Alternative": title_alt,
                        "Description": description,
                        "Related Articles": "<br>".join(related_articles) if related_articles else "None"
                    })
                if data:
                    st.write("### Results")
                    st.markdown(
                        "<table border='1'>" +
                        "<tr>" + "".join(f"<th>{key}</th>" for key in data[0].keys()) + "</tr>" +
                        "".join(
                            "<tr>" + "".join(f"<td>{row[key]}</td>" for key in row.keys()) + "</tr>"
                            for row in data
                        ) +
                        "</table>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No results found.")
            except Exception as e:
                st.error(f"Error executing SPARQL query: {e}")

    elif query_mode == "Keyword Search":
        search_input = st.text_input("Enter search term", "")
        if st.button("Search"):
            query = """
            PREFIX eli: <http://data.europa.eu/eli/ontology#>
            SELECT ?subject ?description ?title_alt
            WHERE {
                ?subject eli:description ?description ;
                         eli:title_alternative ?title_alt .
            }
            """
            results = ontology_graph.query(query)
            data = []
            for row in results:
                entity_uri = str(row[0])
                subject = entity_uri.split("#")[-1] if len(row) > 0 else ""
                description = str(row[1]) if len(row) > 1 else ""
                title_alt = str(row[2]) if len(row) > 2 else ""
                normalized_description = unidecode(description).lower()
                normalized_input = unidecode(search_input).lower()
                if normalized_input in normalized_description:
                    linked_query = f"""
                    PREFIX eli: <http://data.europa.eu/eli/ontology#>
                    SELECT ?related
                    WHERE {{
                        <{entity_uri}> eli:implementation_of|eli:implementation_ensured_by ?related .
                    }}
                    """
                    linked_results = ontology_graph.query(linked_query)
                    related_articles = [
                        generate_hyperlink(str(linked_row[0]), f"{str(linked_row[0]).split('#')[-1]} ({determine_origin(str(linked_row[0]).split('#')[-1])})")
                        for linked_row in linked_results
                    ]
                    origin = determine_origin(subject)
                    data.append({
                        "Origin": origin,
                        "Entity": generate_hyperlink(entity_uri, subject),
                        "Title Alternative": title_alt,
                        "Description": description,
                        "Related Articles": "<br>".join(related_articles) if related_articles else "None"
                    })
            if data:
                st.write("### Results")
                st.markdown(
                    "<table border='1'>" +
                    "<tr>" + "".join(f"<th>{key}</th>" for key in data[0].keys()) + "</tr>" +
                    "".join(
                        "<tr>" + "".join(f"<td>{row[key]}</td>" for key in row.keys()) + "</tr>"
                        for row in data
                    ) +
                    "</table>",
                    unsafe_allow_html=True
                )
            else:
                st.write("No results found.")

elif section == "Visualize Ontology":
    st.header("Ontology Visualization")
    G = nx.DiGraph()
    
    # Query to get relationships
    query = "SELECT ?subject ?predicate ?object WHERE {?subject ?predicate ?object .}"
    results = ontology_graph.query(query)
    
    for row in results:
        subject, predicate, obj = map(str, row)
        G.add_edge(subject.split("/")[-1], 
                   obj.split("/")[-1], 
                   label=predicate.split("#")[-1])
    
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['label'] for u, v, d in G.edges(data=True)})
    st.pyplot(plt)
