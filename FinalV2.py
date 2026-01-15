import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from collections import defaultdict
import datetime
import os
from scipy.sparse.csgraph import laplacian
from scipy.sparse import csr_matrix

# Configuration
plt.switch_backend('Agg')

# ---------------------- Graph Visualization ----------------------
def plot_static_graph(G, pos=None, highlighted_nodes=[], title="Graph"):
    """Static graph visualization with improved layout for large graphs"""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
    
    
    if len(G) > 500:
        if pos is None:
            pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)  
        node_size = 20
        edge_alpha = 0.3
        edge_width = 0.1
    else:
        if pos is None:
            pos = nx.spring_layout(G, seed=42)  
        node_size = 50 if len(G) > 100 else 300
        edge_alpha = 0.5
        edge_width = 0.5
    
    node_colors = ['orange' if n in highlighted_nodes else 'lightblue' for n in G.nodes()]
    
    nx.draw_networkx_nodes(
        G, pos, 
        node_color=node_colors, 
        node_size=node_size, 
        edgecolors='black',
        linewidths=0.3,
        ax=ax
    )
    nx.draw_networkx_edges(
        G, pos, 
        alpha=edge_alpha, 
        width=edge_width, 
        ax=ax
    )
    
    if len(G) <= 100:
        nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', ax=ax)
    
    ax.set_title(title, fontsize=14, pad=20)
    ax.axis('off')
    st.pyplot(fig)
    plt.close(fig)

def plot_dynamic_graph(G, pos, highlighted_nodes=[], title="Interactive Graph"):
    """Interactive graph visualization"""
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), 
                           hoverinfo='none', mode='lines')

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_text = [str(n) for n in G.nodes()]
    node_colors = ['orange' if n in highlighted_nodes else 'lightblue' for n in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        textfont=dict(size=12, color='black'),
        marker=dict(color=node_colors, size=18, line=dict(width=0.5, color='black')),
        hoverinfo='text',
        hovertext=node_text
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=30),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- Optimized Core Functions ----------------------
def robust_effective_resistance(G, u, v, L_pinv=None):
    """effective resistance"""
    if L_pinv is None:
        try:
            L = laplacian(csr_matrix(nx.adjacency_matrix(G)))
            L_pinv = np.linalg.pinv(L.toarray())
        except:
            return 0
    return L_pinv[u, u] + L_pinv[v, v] - 2 * L_pinv[u, v]

def calculate_information_centrality(G):
    """centrality calculation"""
    try:
        n = G.number_of_nodes()
        L = laplacian(csr_matrix(nx.adjacency_matrix(G)))
        L_pinv = np.linalg.pinv(L.toarray())
        
        diagonal = np.diag(L_pinv)
        denominator = n * diagonal - np.sum(L_pinv)
        denominator[denominator == 0] = 1e-10
        centrality = 1 / denominator
        
        return {node: centrality[i] for i, node in enumerate(G.nodes())}
    except Exception as e:
        st.warning(f"Centrality calculation warning: {str(e)}")
        return {node: 1 for node in G.nodes()}

def find_critical_nodes(G, centrality):
    """critical node detection"""
    if not centrality:
        return []
    
    values = np.array(list(centrality.values()))
    if len(values) == 0:
        return []
    
    avg = np.mean(values)
    std = np.std(values)
    
    if std < 1e-6:
        return list(G.nodes())[:min(10, len(G))]
    
    threshold = avg + 0.5 * std
    critical_nodes = [node for node, cent in centrality.items() if cent > threshold]
    
    if not critical_nodes:
        top_n = min(10, len(G))
        critical_nodes = sorted(centrality, key=centrality.get, reverse=True)[:top_n]
    
    return critical_nodes

def process_node(G, node, L_pinv):
    """Edge removal with connectivity check"""
    edges = list(G.edges(node))
    if not edges:
        return G, [], 0
    
    edge_resistances = []
    for edge in edges:
        try:
            resistance = robust_effective_resistance(G, *edge, L_pinv)
            edge_resistances.append((edge, resistance))
        except:
            continue
    
    if not edge_resistances:
        return G, [], 0
    
    edge_resistances.sort(key=lambda x: x[1], reverse=True)
    
    removed_edges = []
    for edge, resistance in edge_resistances:
        G_temp = G.copy()
        G_temp.remove_edge(*edge)
        if nx.is_connected(G_temp):
            G = G_temp
            removed_edges.append((edge, resistance))
    
    return G, removed_edges, len(removed_edges)

def write_log_file(G, critical_nodes, removed_edges_info, initial_edges, filename="graph_analysis_log.txt"):
    """Your exact log format"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== Critical Node Edge Removal Log ===\n\n")
        f.write(f"Analysis performed at: {datetime.datetime.now()}\n\n")
        f.write(f"Total Nodes: {G.number_of_nodes()}\n")
        f.write(f"Total Edges Before Removal: {initial_edges}\n")
        f.write(f"Total Edges After Removal: {G.number_of_edges()}\n")
        f.write(f"Total Removed Edges: {initial_edges - G.number_of_edges()}\n")
        f.write(f"Identified Critical Nodes: {sorted(critical_nodes)}\n\n")
        
        for node, edges in removed_edges_info.items():
            f.write(f"Node {node} - Removed {len(edges)} edges:\n")
            for edge, resistance in edges:
                f.write(f"  Removed Edge: {edge}, Effective Resistance: {resistance:.4f}\n")
            f.write("-" * 40 + "\n")
    return filename

# ---------------------- Main Application ----------------------
def main():
    st.title("CritiCut: Critical Node Moderation with edge removal")
    
    #session state
    if 'G' not in st.session_state:
        st.session_state.G = None
    if 'num_nodes' not in st.session_state:
        st.session_state.num_nodes = 20
    if 'edge_prob' not in st.session_state:
        st.session_state.edge_prob = 0.3
    
    
    tab1, tab2 = st.tabs(["Upload Dataset", "User Graph"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload edge list file", type=["txt", "csv"], key="uploader")
        if uploaded_file is not None:
            try:
                edges = []
                for line in uploaded_file:
                    line = line.decode('utf-8').strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            edges.append((int(parts[0]), int(parts[1])))
                
                G = nx.Graph()
                G.add_edges_from(edges)
                
                if not nx.is_connected(G):
                    largest_cc = max(nx.connected_components(G), key=len)
                    G = G.subgraph(largest_cc).copy()
                    st.warning(f"Using largest connected component with {G.number_of_nodes()} nodes")
                
                st.session_state.G = G
                st.success(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            
            def update_num_nodes_slider():
                st.session_state.num_nodes = st.session_state.num_nodes_slider
            
            def update_num_nodes_input():
                st.session_state.num_nodes = st.session_state.num_nodes_input
            
            num_nodes = st.slider(
                "Number of Nodes", 
                15, 1000, 
                st.session_state.num_nodes, 
                key="num_nodes_slider",
                on_change=update_num_nodes_slider
            )
            
            num_nodes_input = st.number_input(
                "Or enter exact number", 
                min_value=15, 
                max_value=1000, 
                value=st.session_state.num_nodes,
                key="num_nodes_input",
                on_change=update_num_nodes_input
            )
        
        with col2:
            
            def update_edge_prob_slider():
                st.session_state.edge_prob = st.session_state.edge_prob_slider
            
            def update_edge_prob_input():
                st.session_state.edge_prob = st.session_state.edge_prob_input
            
            edge_prob = st.slider(
                "Edge Probability", 
                0.10, 1.00, 
                st.session_state.edge_prob, 
                step=0.05, 
                key="edge_prob_slider",
                on_change=update_edge_prob_slider
            )
            
            edge_prob_input = st.number_input(
                "Or enter exact probability", 
                min_value=0.10, 
                max_value=1.00, 
                value=st.session_state.edge_prob,
                step=0.01,
                key="edge_prob_input",
                on_change=update_edge_prob_input
            )
        
        if st.button("Generate Graph"):
            G = nx.erdos_renyi_graph(st.session_state.num_nodes, st.session_state.edge_prob, seed=42)
            while not nx.is_connected(G):
                G = nx.erdos_renyi_graph(st.session_state.num_nodes, st.session_state.edge_prob, seed=np.random.randint(100))
            st.session_state.G = G
            st.success(f"Generated connected graph with {G.number_of_nodes()} nodes")

    
    if st.session_state.G is not None:
        G = st.session_state.G
        with st.spinner("Calculating graph layout..."):
            if G.number_of_nodes() > 500:
                pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)  
            else:
                pos = nx.spring_layout(G, seed=42)
        
        centrality = calculate_information_centrality(G)
        critical_nodes = find_critical_nodes(G, centrality)
        
        st.write(f"**Graph Statistics:**")
        st.write(f"- Nodes: {G.number_of_nodes()}")
        st.write(f"- Edges: {G.number_of_edges()}")
        st.write(f"- Critical Nodes Identified: {len(critical_nodes)}")
        
        # Visual switch
        if G.number_of_nodes() <= 500:
            st.write("### Initial Graph Visualization")
            plot_dynamic_graph(G, pos, highlighted_nodes=critical_nodes)
        else:
            st.write("### Static Visualization")
            plot_static_graph(G, pos, highlighted_nodes=critical_nodes)
        
        if st.button("Start Edge Removal Optimization", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            initial_edges = G.number_of_edges()
            try:
                L = laplacian(csr_matrix(nx.adjacency_matrix(G)))
                L_pinv = np.linalg.pinv(L.toarray())
            except:
                L_pinv = None
            
            optimized_G = G.copy()
            removed_edges_info = defaultdict(list)
            total_edges_removed = 0

            for iteration, node in enumerate(critical_nodes, 1):
                optimized_G, removed_edges, edges_removed = process_node(optimized_G, node, L_pinv)
                total_edges_removed += edges_removed
                if removed_edges:
                    removed_edges_info[node] = removed_edges
                
                progress = int((iteration / len(critical_nodes)) * 100)
                progress_bar.progress(progress)
                status_text.info(f"Processing node {node} ({iteration}/{len(critical_nodes)})")

            progress_bar.progress(100)
            status_text.success(f"Optimization complete! Removed {total_edges_removed} edges")
            
            st.write("### Final Optimized Graph")
            if optimized_G.number_of_nodes() <= 500:
                plot_dynamic_graph(optimized_G, pos, title="Optimized Graph")
            else:
                plot_static_graph(optimized_G, pos, title="Optimized Graph")
            
            log_filename = write_log_file(optimized_G, critical_nodes, removed_edges_info, initial_edges)
            with open(log_filename, "rb") as f:
                st.download_button(
                    "📥 Download Full Optimization Log",
                    f, 
                    file_name=log_filename,
                    mime="text/plain"
                )
            os.remove(log_filename)

if __name__ == "__main__":
    main()