import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="GDPR Dashboard", layout="wide")

# Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose a section", ["Overview", "Search Ontology", "Visualize Data"])

if section == "Overview":
    st.header("Ontology Overview")
    st.subheader("Ontology Statistics")
    st.write("Number of classes: 50")
    st.write("Number of properties: 200")
    st.write("Number of triples: 10,000")

elif section == "Search Ontology":
    st.header("Search Ontology")
    query = st.text_area("SPARQL Query", "SELECT ?s ?p ?o WHERE {?s ?p ?o} LIMIT 10")
    if st.button("Run Query"):
        st.success("Query executed successfully!")
        st.write("[Mock Data] Example triples here")

elif section == "Visualize Data":
    st.header("Visualize Ontology")
    G = nx.DiGraph()
    G.add_edge("Person", "hasName")
    G.add_edge("Person", "hasEmail")
    G.add_edge("Organization", "employs", "Person")
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_size=1500, node_color="lightblue", ax=ax)
    st.pyplot(fig)
