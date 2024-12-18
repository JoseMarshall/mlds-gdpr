import streamlit as st
from rdflib import Graph, URIRef
import networkx as nx
import os
from collections import Counter
import matplotlib.pyplot as plt
import re
from unidecode import unidecode
import urllib.parse
from pyvis.network import Network
import streamlit.components.v1 as components


# Function to create hyperlinks
def generate_hyperlink(entity_uri, label):
    encoded_uri = urllib.parse.quote(entity_uri)
    return f'<a href="?entity={encoded_uri}" target="_self">{label}</a>'

# Streamlit page configuration
st.set_page_config(page_title="Ontology Dashboard", layout="wide")

# Load ontology with caching
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

# Initialize state for navigation
if "active_section" not in st.session_state:
    st.session_state["active_section"] = "Overview"

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to:",
    ["Overview", "Search Ontology", "Entity Profile", "Visualization"]
)
st.session_state["active_section"] = section

# Helper function: Determine origin based on entity name
def determine_origin(entity_name):
    suffix_map = {
        "eu_en": "EU GDPR - English",
        "eu_de": "EU GDPR - Deutsch",
        "eu_pt": "EU GDPR - Português",
        "eu_it": "EU GDPR - Italiano",
        "_en": "National GDPR - England",
        "_de": "National GDPR - Deutschland",
        "_it": "National GDPR - Italia",
        "_pt": "National GDPR - Portugal",
    }
    for suffix, origin in suffix_map.items():
        if entity_name.endswith(suffix):
            return origin
    return "Unknown Origin"

# Entity profile display
def display_entity_profile(entity_uri):
    st.subheader("Entity Profile")
    st.write(f"**Entity Name:** {entity_uri.split('#')[-1]}")

    # SPARQL query to fetch details
    query = f"""
    PREFIX eli: <http://data.europa.eu/eli/ontology#>
    SELECT ?predicate ?object
    WHERE {{
        <{entity_uri}> ?predicate ?object .
    }}
    """
    try:
        results = ontology_graph.query(query)
        data = [{"Predicate": str(row[0]).split("#")[-1], "Object": str(row[1])} for row in results]
        if data:
            st.table(data)
        else:
            st.write("No data available for the selected entity.")
    except Exception as e:
        st.error(f"SPARQL query error: {e}")


# Overview section
if st.session_state["active_section"] == "Overview":
    st.header("Ontology Overview")
    num_classes = len(set(ontology_graph.subjects(predicate=URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))))
    num_properties = len(set(ontology_graph.predicates()))
    num_entities = len(set(ontology_graph.subjects()) | set(ontology_graph.objects()))
    num_relationships = len(ontology_graph)
    class_counts = Counter(
        str(o).split("#")[-1]
        for s, p, o in ontology_graph.triples((None, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), None))
    )
    most_common_classes = class_counts.most_common(len(class_counts))

    st.write("### Classes")
    st.bar_chart({k: v for k, v in most_common_classes})

    sample_triples = list(ontology_graph)[2:5]
    st.write("### Example Triples")
    for triple in sample_triples:
        st.write(f"**Subject:** {triple[0]}  \n**Predicate:** {triple[1]}  \n**Object:** {triple[2]}")

    st.write(f"**Total Triples:** {len(ontology_graph)}")
    from collections import Counter

    property_counts = Counter(str(p).split("#")[-1] for p in ontology_graph.predicates())
    most_common_properties = property_counts.most_common(len(property_counts))

    st.write("### Properties")
    st.write(f"**Number of Property types:** {len(property_counts)}")
    st.bar_chart({k: v for k, v in most_common_properties})


# Search Ontology section
elif st.session_state["active_section"] == "Search Ontology":
    st.header("Search Ontology")

    # Allow the user to select the search mode
    query_mode = st.radio("Select Search Mode", ["SPARQL Query", "Keyword Search"])

    if query_mode == "SPARQL Query":
        st.subheader("SPARQL Query Search")
        st.write("Enter a custom SPARQL query to explore the ontology.")

        # Pre-filled SPARQL query as a placeholder
        query = st.text_area(
            "SPARQL Query",
            """
            PREFIX eli: <http://data.europa.eu/eli/ontology#>
            SELECT ?subject ?description ?title_alt
            WHERE {
                ?subject eli:description ?description ;
                         eli:title_alternative ?title_alt .
            }
            """,
            height=150,
        )

        # Button to execute the query
        if st.button("Run SPARQL Query"):
            try:
                results = ontology_graph.query(query)
                # Format results into a structured table
                data = [
                    {
                        "Entity": generate_hyperlink(str(row[0]), str(row[0]).split("#")[-1]),
                        "Description": str(row[1]),
                        "Title Alternative": str(row[2]),
                    }
                    for row in results
                ]
                if data:
                    st.write("### Query Results")
                    st.table(data)
                else:
                    st.info("No results found for the given query.")
            except Exception as e:
                st.error(f"Error executing SPARQL query: {e}")

    elif query_mode == "Keyword Search":
        st.subheader("Keyword Search")
        st.write("Search the ontology by entering a keyword.")

        # Input field for the keyword search
        search_term = st.text_input("Enter a keyword or phrase:")

        # Execute the search when the button is clicked
        if st.button("Search"):
            try:
                query = """
                PREFIX eli: <http://data.europa.eu/eli/ontology#>
                SELECT ?subject ?description ?title_alt
                WHERE {
                    ?subject eli:description ?description ;
                             eli:title_alternative ?title_alt .
                }
                """
                results = ontology_graph.query(query)
                search_results = []

                # Filter results based on the keyword
                for row in results:
                    if unidecode(search_term).lower() in unidecode(str(row[1])).lower():
                        search_results.append(
                            {
                                "Entity": generate_hyperlink(str(row[0]), str(row[0]).split("#")[-1]),
                                "Description": str(row[1]),
                                "Title Alternative": str(row[2]),
                            }
                        )

                if search_results:
                    st.write(f"### Results for '{search_term}'")
                    st.table(search_results)
                else:
                    st.info(f"No matches found for the keyword '{search_term}'.")
            except Exception as e:
                st.error(f"Error performing keyword search: {e}")


# Entity Profile section
elif st.session_state["active_section"] == "Entity Profile":
    if "entity" in st.query_params:
        entity_uri = urllib.parse.unquote(st.query_params["entity"][0])
        display_entity_profile(entity_uri)
    else:
        st.write("No entity selected.")


# Visualization section
elif st.session_state["active_section"] == "Visualization":
    st.header("Ontology Visualization")
    st.write("This section provides an interactive graph visualization of the ontology.")

    # Create a Pyvis Network instance
    net = Network(height="750px", width="100%", directed=True)

    query = "SELECT ?subject ?predicate ?object WHERE {?subject ?predicate ?object .}"
    with st.spinner("Generating interactive visualization..."):
        try:
            # Execute SPARQL query
            results = ontology_graph.query(query)
            count = 0
            max_triples = 1500  # Limit the number of triples for performance

            # Add nodes and edges to the graph
            for subject, predicate, obj in results:
                if count >= max_triples:
                    break
                subj_label = subject.split("/")[-1]
                obj_label = obj.split("/")[-1]
                pred_label = predicate.split("#")[-1]

                net.add_node(subj_label,
                             label=subj_label,
                             title=subject,
                             color='#4CAF50')  # Green color for subject nodes
                net.add_node(obj_label,
                             label=obj_label,
                             title=obj,
                             color='#2196F3')  # Blue color for object nodes
                net.add_edge(subj_label, obj_label, label=pred_label)
                count += 1

            if count == 0:
                st.warning("No data available to visualize. Please ensure the ontology contains triples.")
            else:
                # Customize Pyvis options
                net.set_options("""
                var options = {
                  "edges": {
                    "arrows": {
                      "to": {
                        "enabled": true
                      }
                    },
                    "color": {
                      "inherit": true
                    },
                    "smooth": false
                  },
                  "physics": {
                    "enabled": true,
                    "stabilization": {
                      "enabled": true,
                      "iterations": 200
                    }
                  }
                }
                """)

                # Generate and display the interactive visualization
                net_html = "graph.html"
                net.save_graph(net_html)
                components.html(open(net_html, "r").read(), height=750, scrolling=True)

        except Exception as e:
            st.error(f"Visualization error: {e}")

