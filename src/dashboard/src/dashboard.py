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


query_params = st.query_params



# def show_entity_profile(entity_uri):
#     """Display detailed information about a specific entity"""
#     print(entity_uri)
#
#     entity_query = """
#     PREFIX eli: <http://data.europa.eu/eli/ontology#>
#     SELECT ?predicate ?object
#     WHERE {
#         <%s> ?predicate ?object .
#     }
#     """ % entity_uri
#
#     try:
#         results = ontology_graph.query(entity_query)
#         st.write(f"SPARQL Results: {list(results)}")
#         properties = {}
#         for row in results:
#             predicate = str(row[0])
#             obj = str(row[1])
#             if predicate not in properties:
#                 properties[predicate] = []
#             properties[predicate].append(obj)
#         for predicate, objects in properties.items():
#             st.markdown(f"**Property:** {predicate}")
#             for obj in objects:
#                 st.write(f"- {obj}")
#
#     except Exception as e:
#         st.error(f"Error loading entity profile: {e}")


def show_entity_profile(entity_uri):
    """Display detailed information about a specific entity"""
    st.header("Entity Profile")

    # Query to get all information about the entity
    entity_query = """
    PREFIX eli: <http://data.europa.eu/eli/ontology#>
    SELECT ?predicate ?object
    WHERE {
        <%s> ?predicate ?object .
    }
    """

    try:
        results = ontology_graph.query(entity_query % entity_uri)

        # Group the results by predicate for better organization
        entity_data = {}
        for row in results:
            pred = str(row[0]).split('#')[-1]  # Get the predicate name
            obj = str(row[1])
            if pred not in entity_data:
                entity_data[pred] = []
            entity_data[pred].append(obj)

        # Display entity information
        st.subheader(f"Entity: {entity_uri.split('#')[-1]}")

        # Create tabs for different types of information
        tabs = st.tabs(["Basic Info", "Related Articles", "Implementation Details"])

        with tabs[0]:
            if "description" in entity_data:
                st.markdown("### Description")
                st.write(entity_data["description"][0])

            if "title_alternative" in entity_data:
                st.markdown("### Alternative Title")
                st.write(entity_data["title_alternative"][0])

        with tabs[1]:
            # Query for related articles
            related_query = """
            PREFIX eli: <http://data.europa.eu/eli/ontology#>
            SELECT ?related ?description
            WHERE {
                <%s> eli:implementation_of|eli:implementation_ensured_by ?related .
                OPTIONAL { ?related eli:description ?description }
            }
            """ % entity_uri

            related_results = ontology_graph.query(related_query)

            st.markdown("### Related Articles")
            for row in related_results:
                with st.expander(f"{str(row[0]).split('#')[-1]}"):
                    if len(row) > 1 and row[1]:
                        st.write(str(row[1]))
                    else:
                        st.write("No description available")

        with tabs[2]:
            st.markdown("### Implementation Details")
            implementation_details = {k: v for k, v in entity_data.items()
                                      if "implementation" in k.lower()}
            if implementation_details:
                for pred, objs in implementation_details.items():
                    st.markdown(f"**{pred}:**")
                    for obj in objs:
                        st.write(f"- {obj}")
            else:
                st.write("No implementation details available")

    except Exception as e:
        st.error(f"Error loading entity profile: {e}")


# Function to create hyperlinks
def generate_hyperlink(entity_uri, label):
    # st.write(f"Entity URI: {entity_uri}")

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
if "entity" in query_params:
    if st.session_state["active_section"] != "Entity Profile":
        st.session_state["previous_section"] = st.session_state["active_section"]
    section = "Entity Profile"
else:
    # Your existing navigation code
    section = st.sidebar.radio(
        "Go to:",
        ["Overview", "Keyword Search", "Advanced Search", "Visualization"]
    )
st.session_state["active_section"] = section
# if st.session_state["active_section"] == "Entity Profile":
#     entity_uri = urllib.parse.unquote(query_params["entity"][0])
#     show_entity_profile(entity_uri)

    # if st.button("Back to Search"):
    #     st.query_params.clear()
    #     st.session_state["active_section"] = st.session_state["previous_section"]  # Restore previous section
    #     st.rerun()


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
st.sidebar.code("""
PREFIX eli: <http://data.europa.eu/eli/ontology#>
SELECT ?subject ?description ?title_alt ?implement
WHERE {
    ?subject eli:description ?description ;
                       eli:implementation_ensured_by ?implement .
}
""")
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
# def display_entity_profile(entity_uri):
#     st.subheader("Entity Profile")
#     st.write(f"**Entity Name:** {entity_uri.split('#')[-1]}")
#
#     # SPARQL query to fetch details
#     query = f"""
#     PREFIX eli: <http://data.europa.eu/eli/ontology#>
#     SELECT ?predicate ?object
#     WHERE {{
#         <{entity_uri}> ?predicate ?object .
#     }}
#     """
#     try:
#         results = ontology_graph.query(query)
#         data = [{"Predicate": str(row[0]).split("#")[-1], "Object": str(row[1])} for row in results]
#         if data:
#             st.table(data)
#         else:
#             st.write("No data available for the selected entity.")
#     except Exception as e:
#         st.error(f"SPARQL query error: {e}")


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

elif st.session_state["active_section"] == "Keyword Search":
    st.header(" Keyword Search")
    st.write("Search the ontology by entering a keyword.")

    # Input field for the keyword search
    search_input = st.text_input("Enter a keyword or phrase:")

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
                        generate_hyperlink(str(linked_row[0]),
                                           f"{str(linked_row[0]).split('#')[-1]} ({determine_origin(str(linked_row[0]).split('#')[-1])})")
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
        except Exception as e:
            st.error(f"Error performing keyword search: {e}")



# Search Ontology section
elif st.session_state["active_section"] == "Advanced Search":
    st.header("Advanced Search")




    st.subheader("SPARQL Query Search")
    st.write("Enter a custom SPARQL query to explore the ontology.")

    # Pre-filled SPARQL query as a placeholder
    query = st.text_area(
        "SPARQL Query",
        """
        PREFIX eli: <http://data.europa.eu/eli/ontology#>
        SELECT ?subject ?description ?title_alt ?implement
        WHERE {
            ?subject eli:description ?description ;
                       eli:implementation_ensured_by ?implement .
        }
        """,
        height=150,
    )

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
                st.info("No results found for the given query.")
        except Exception as e:
            st.error(f"Error executing SPARQL query: {e}")




# Entity Profile section
elif st.session_state["active_section"] == "Entity Profile":

    if "entity" in st.query_params:
        entity_uri = urllib.parse.unquote(st.query_params["entity"])
        show_entity_profile(entity_uri)
    else:
        st.write("No entity selected.")




# Visualization section
elif st.session_state["active_section"] == "Visualization":
    st.header("Ontology Visualization")
    st.write("This section provides an interactive graph visualization of the ontology.")

    # Create a Pyvis Network instance
    net = Network(height="750px", width="100%", directed=True)

    query = """
    SELECT ?subject ?predicate ?object 
    WHERE {
        ?subject ?predicate ?object .
        FILTER(
            ?predicate IN (
                <http://data.europa.eu/eli/ontology#is_realized_by>,
                <http://data.europa.eu/eli/ontology#has_part>,
                <http://data.europa.eu/eli/ontology#is_part_of>
            ) || 
            ?object IN (
                <http://example.org/gdpr#GDPR>,
                <http://example.org/rgdpr#>
            )
        )
    }
    """
    with st.spinner("Generating interactive visualization..."):
        try:
            results = ontology_graph.query(query)
            count = 0
            max_triples = 11000  # Adjust as needed for performance

            # Dictionary to track added nodes and avoid duplicates
            added_nodes = set()

            for subject, predicate, obj in results:
                subj_label = subject.split("/")[-1]
                obj_label = obj.split("/")[-1]
                pred_label = predicate.split("#")[-1]

                # Add subject node if not already added
                if subj_label not in added_nodes:
                    net.add_node(subj_label,
                                 label=subj_label,
                                 title=subject,
                                 color='#4CAF50')  # Green for classes
                    added_nodes.add(subj_label)

                # Add object node if not already added
                if obj_label not in added_nodes:
                    net.add_node(obj_label,
                                 label=obj_label,
                                 title=obj,
                                 color='#2196F3')  # Blue for individuals
                    added_nodes.add(obj_label)

                # Add edge
                net.add_edge(subj_label, obj_label, label=pred_label)
                count += 1

                if count >= max_triples:
                    break

            # Check if the graph has at least 10 nodes
            if len(added_nodes) < 10:
                st.warning("The generated graph contains fewer than 10 nodes. No visualization will be displayed.")
            elif count == 0:
                st.warning("No data available to visualize. Please ensure the ontology contains relevant triples.")
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





