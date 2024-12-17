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

elif section == "Search Ontology":
    st.header("Search Ontology")

    # Option to toggle between SPARQL and high-level query
    query_type = st.radio(
        "Choose Query Mode", 
        ["SPARQL Query (Advanced)", "High-Level Query (Easy)"]
    )

    if query_type == "SPARQL Query (Advanced)":
        # SPARQL query input
        query = st.text_area(
            "SPARQL Query",
            """PREFIX eli: <http://data.europa.eu/eli/ontology#>
            SELECT ?subject ?description
            WHERE {
                ?subject eli:description ?description .
                FILTER(CONTAINS(?description, "Stellen"))
            }
            """,
            height=200
        )

        # Checkbox for including linked properties
        include_linked_properties = st.checkbox("Include linked properties/articles (eli:implementation_ensured_by & eli:implementation_of)")

        if st.button("Run Query"):
            try:
                # Execute the user-provided query
                results = ontology_graph.query(query)
                st.success("Query executed successfully!")

                # Process results and optionally add linked properties
                data = []
                for row in results:
                    subject = row[0]
                    description = row[1]

                    linked = []
                    if include_linked_properties:
                        # Fetch linked properties for this subject
                        for prop, inverse in [
                            ("eli:implementation_ensured_by", "eli:implementation_of"),
                            ("eli:implementation_of", "eli:implementation_ensured_by"),
                        ]:
                            query_linked = f"""
                                PREFIX eli: <http://data.europa.eu/eli/ontology#>
                                SELECT ?linked
                                WHERE {{
                                    <{subject}> eli:{prop} ?linked .
                                }}
                            """
                            linked_results = ontology_graph.query(query_linked)
                            linked.extend([str(linked_row[0]) for linked_row in linked_results])

                    # Add result to the data list
                    data.append({
                        "Subject": subject,
                        "Description": description,
                        "Linked Properties": ", ".join(linked) if linked else "None"
                    })

                # Display results in a table
                if data:
                    st.table(data)
                else:
                    st.write("No results found.")

            except Exception as e:
                st.error(f"Error executing query: {e}")

    elif query_type == "High-Level Query (Easy)":
        st.subheader("Predefined Query Options")

        # Checkboxes for high-level options
        look_for_articles = st.checkbox("Look for specific article")
        include_linked_properties = st.checkbox("Include linked properties")

        if st.button("Run Query"):
            base_query = """
                PREFIX eli: <http://data.europa.eu/eli/ontology#>
                SELECT ?subject ?description
                WHERE {
                    ?subject eli:description ?description .
                }
            """
            # Query modifications based on checkboxes
            if look_for_articles:
                base_query = """
                    PREFIX eli: <http://data.europa.eu/eli/ontology#>
                    SELECT ?subject ?description
                    WHERE {
                        ?subject a eli:LegalResource ;
                                 eli:description ?description .
                    }
                """

            try:
                # Run query
                results = ontology_graph.query(base_query)
                st.success("Query executed successfully!")

                # Process results and add linked properties if selected
                data = []
                for row in results:
                    subject = row[0]
                    description = row[1]

                    linked = []
                    if include_linked_properties:
                        # Check for linked properties
                        for prop, inverse in [
                            ("eli:implementation_ensured_by", "eli:implementation_of"),
                            ("eli:implementation_of", "eli:implementation_ensured_by"),
                        ]:
                            query_linked = f"""
                                PREFIX eli: <http://data.europa.eu/eli/ontology#>
                                SELECT ?linked
                                WHERE {{
                                    <{subject}> eli:{prop} ?linked .
                                }}
                            """
                            linked_results = ontology_graph.query(query_linked)
                            linked.extend([str(linked_row[0]) for linked_row in linked_results])

                    data.append({
                        "Subject": subject,
                        "Description": description,
                        "Linked Properties": ", ".join(linked) if linked else "None"
                    })

                # Display results in a table
                if data:
                    st.table(data)
                else:
                    st.write("No results found.")
            except Exception as e:
                st.error(f"Error executing query: {e}")
