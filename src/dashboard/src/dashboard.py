import streamlit as st
from rdflib import Graph
import networkx as nx
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Ontology Dashboard", layout="wide")

# Dynamically locate the ontology file in the same directory as this script
@st.cache_resource
def load_ontology():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "abstract_updated.ttl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ontology file not found at: {file_path}")
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

# Load ontology
ontology_graph = load_ontology()

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose a section", ["Overview", "Search Ontology", "Visualize Data"])

# Overview Section
if section == "Overview":
    st.header("Ontology Overview")
    st.subheader("Ontology Statistics")
    
    num_triples = len(ontology_graph)
    st.write(f"Number of triples: {num_triples}")
    
    # Optional: Add counts for classes and properties
    classes = set(ontology_graph.subjects())
    properties = set(ontology_graph.predicates())
    st.write(f"Number of unique classes: {len(classes)}")
    st.write(f"Number of unique properties: {len(properties)}")

# Search Ontology Section
elif section == "Search Ontology":
    st.header("Search Ontology")
    query = st.text_area(
        "SPARQL Query",
        """PREFIX : <http://your-ontology-base-iri#>
        SELECT ?individual ?description
        WHERE {
            ?individual :description ?description .
            FILTER(CONTAINS(?description, "Stellen"))
        }
        """
    )
    if st.button("Run Query"):
        try:
            results = ontology_graph.query(query)
            st.success("Query executed successfully!")
            st.write("### Results:")
            
            # Display results in a table format
            for row in results:
                st.write(f"Individual: {row[0]}, Description: {row[1]}")
        except Exception as e:
            st.error(f"Error executing query: {e}")

# Visualize Data Section
elif section == "Visualize Data":
    st.header("Visualize Ontology")
    
    # Create a sample graph visualization
    G = nx.DiGraph()
    for subj, pred, obj in ontology_graph:
        G.add_edge(str(subj), str(obj), label=str(pred))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        edge_color="gray",
        font_size=10,
        ax=ax,
    )
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    st.pyplot(fig)
