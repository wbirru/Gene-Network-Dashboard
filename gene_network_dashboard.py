import streamlit as st
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import urllib.parse
import datetime

st.set_page_config(page_title="Gene Network Dashboard", layout="wide")
st.title("🧠 Gene Network Tools Dashboard")

# Current date and memory/context note
current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
st.markdown(f"**📅 Date:** {current_date}")
st.info("""
This platform integrates genomic and therapeutic data, focusing on gene networks, drug-gene interactions, and dynamic network visualizations.
It uses tools such as GeneMANIA, STRING, and Cytoscape + ClueGO, emphasizing user-friendly interfaces, API integration, and transparent data sources.
Developed for advanced gene network and pathway analysis in genomic research.
""")

# Sidebar: gene input
st.sidebar.header("Enter Gene Symbols")
default_genes = "FSHR, LHCGR, CYP19A1, ESR1, INHBA, GNRHR"
genes_input = st.sidebar.text_area("Gene list (comma-separated):", value=default_genes)
genes = [g.strip() for g in genes_input.split(",") if g.strip()]
run_networks = st.sidebar.button("🚀 Run Network Analysis")

# --- STRING API (edge list for network etc) ---
@st.cache_data
def query_string_edges(genes):
    url = "https://string-db.org/api/json/network"
    params = {"identifiers": "\n".join(genes), "species": 9606}
    try:
        r = requests.get(url, params=params)
        return r.json()
    except Exception as e:
        st.error(f"STRING-db API error: {e}")
        return []

# --- NetworkX visualization helper ---
def draw_networkx_graph(edge_df, source_col, target_col, title="Network Preview"):
    if edge_df.empty: 
        st.info("No network edges to display.")
        return
    G = nx.Graph()
    for _, row in edge_df.iterrows():
        G.add_edge(str(row[source_col]), str(row[target_col]))
    plt.figure(figsize=(7,5))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=400, font_size=10, node_color='lightblue', edge_color='gray')
    st.pyplot(plt.gcf())
    plt.close()

# --- Main Output ---
if run_networks and genes:
    # 1. GeneMANIA - Web links per gene
    st.subheader("1️⃣ GeneMANIA (Web Tool)")
    st.markdown("""
    **Summary:**  
    Finds functionally associated gene networks using co-expression, physical interactions, pathway data, and co-localization.  
    **API/Automation:** ❌ Mostly web-only; API limited/unavailable for programmatic network retrieval.
    """)
    st.markdown("**Explore networks for each gene individually:**")
    for g in genes:
        gm_url = f"https://genemania.org/search/human/{urllib.parse.quote(g)}"
        st.markdown(f"- [{g} on GeneMANIA]({gm_url})")
    st.info("Open any gene link above to explore its predicted functional network interactively on GeneMANIA.")

    # 2. STRING-db (API)
    st.subheader("2️⃣ STRING-db (API Integrated)")
    st.markdown("""
    **Summary:**  
    Protein–protein interaction and functional association network with enrichment scores and evidence.  
    **API/Automation:** ✅ REST API, supports scripting and visualization.
    """)
    string_edges = query_string_edges(genes)
    if string_edges:
        se_df = pd.DataFrame(string_edges)
        node_names = set(se_df['preferredName_A']).union(set(se_df['preferredName_B']))
        st.write(f"**Nodes:** {len(node_names)} &nbsp;&nbsp;&nbsp; **Edges:** {len(se_df)}")
        st.dataframe(se_df[["preferredName_A", "preferredName_B", "score"]].head(10))
        st.markdown("**Network Visualization:**")
        draw_networkx_graph(se_df, "preferredName_A", "preferredName_B", title="STRING Network")
        string_url = "https://string-db.org/cgi/network?species=9606&identifiers=" + "%0A".join(urllib.parse.quote(g) for g in genes)
        st.markdown(f"[🌐 View Full STRING Network Online]({string_url})")
        st.download_button("⬇ Download STRING Edges for Cytoscape", se_df[["preferredName_A", "preferredName_B"]].to_csv(index=False), "string_network.csv")
    else:
        st.info("No STRING network returned for given genes.")
# GIANT
    st.subheader("3️⃣ GIANT (Global/tissue-specific gene networks, API)")
    st.markdown("""
    **Summary:**  
    GIANT offers API access for network queries, prioritization, and tissue-specific networks.  
    **API/Automation:** ✅ REST API supported.
    """)
    for g in genes:
        giant_url = f"https://giant-api.princeton.edu/api/search/genes?q={urllib.parse.quote(g)}"
        st.markdown(f"- [{g} on GIANT API]({giant_url})")

    # 3. Cytoscape + ClueGO
    st.subheader("4️⃣ Cytoscape + ClueGO (Desktop Visualization)")
    st.markdown("""
    **Summary:**  
    Cytoscape provides advanced network visualization and analysis.  
    ClueGO clusters functionally grouped GO/pathway terms within Cytoscape for detailed interpretation.  
    **API/Automation:** ✅ Via Cytoscape CyREST API (local).  
    Instructions:  
    - Download interaction edge files from STRING above.  
    - Import into Cytoscape.  
    - Install ClueGO app for pathway enrichment and clustering.  
    - Use scripting (cyREST) for automation.
    """)
    # NetworkX
    st.subheader("5️⃣ NetworkX (Python Package)")
    st.markdown("""
    **Summary:**  
    Python library for fast custom network construction, analysis, and visualization.  
    **API/Automation:** ✅ Scripting library only.  
    [NetworkX Documentation](https://networkx.org/)
    """)

    # Pathway Commons
    st.subheader("6️⃣ Pathway Commons (Web Tool)")
    st.markdown("""
    **Summary:**  
    Integrated resource for pathway data aggregation and API access.  
    **API/Automation:** ✅ Web REST API, batch mode.  
    [🌐 Pathway Commons Search](https://www.pathwaycommons.org/pc2/search.do?q={}) """.format(",".join(genes))
    )
# --- Evaluation Table ---
st.markdown("---")
st.subheader("📊 Network Tool Performance Evaluation")

criteria = {
    "🧬 Biological Context": "Relevance to FSH, folliculogenesis, endocrine system",
    "🔄 Network Connectivity": "Gene/protein network edges and evidence quality",
    "💊 Clinical Utility": "Supports drug/phenotype linkages and biomarker mapping",
    "🤖 AI-readiness": "Provides structured, ML-ready network features",
    "🛠 Interoperability": "API availability, export formats, reproducibility",
    "🧑‍⚕️ Clinical Explainability": "Ease of interpretation for clinicians",
    "🎯 Visual Insight": "Availability of clear, interactive, and exportable visuals"
}

default_scores = {
    "GeneMANIA": [5, 5, 2, 3, 5, 3, 5],
    "STRING-db": [4, 5, 3, 4, 5, 2, 5],
    "GAINT": [5, 5, 3, 4, 5, 2, 5],
    "Cytoscape+ClueGO": [4, 4, 2, 5, 5, 3, 5],
    "NetworkX": [1, 3, 1, 5, 5, 1, 2],
    "Pathway Commons": [5, 5, 2, 5, 5, 2, 4]
}

df_eval = pd.DataFrame(default_scores, index=criteria.keys()).T

for tool in df_eval.index:
    with st.expander(f"🔧 Adjust scores for {tool}"):
        for crit in criteria:
            df_eval.loc[tool, crit] = st.slider(
                label=f"{crit}",
                min_value=1,
                max_value=5,
                value=int(df_eval.loc[tool, crit]),
                help=criteria[crit],
                key=f"{tool}-{crit}"
            )
df_eval["Total Score"] = df_eval[list(criteria.keys())].sum(axis=1)
st.dataframe(df_eval.astype(int))
st.download_button("⬇ Download Evaluation Scores", df_eval.to_csv(), "gene_network_eval.csv")
