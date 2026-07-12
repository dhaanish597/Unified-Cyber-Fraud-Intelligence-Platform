import os
import pandas as pd
import networkx as nx
from community import community_louvain
import json

def build_graph_and_export():
    print("Loading transactions...")
    df = pd.read_csv('data/processed/transactions.csv', nrows=200000) # Read a chunk for speed in demo
    
    G = nx.Graph()
    
    print("Building account/device/IP graph...")
    # Track mule cluster flags
    mule_flags = {}
    
    for _, row in df.iterrows():
        orig = str(row['nameOrig'])
        dest = str(row['nameDest'])
        dev_orig = str(row['device_id'])
        ip_orig = str(row['ip'])
        dev_dest = str(row['dest_device_id'])
        ip_dest = str(row['dest_ip'])
        
        # Add edges
        G.add_edge(orig, dest, type='transfer')
        if dev_orig and dev_orig != 'nan':
            G.add_edge(orig, dev_orig, type='has_device')
        if ip_orig and ip_orig != 'nan':
            G.add_edge(orig, ip_orig, type='has_ip')
            
        if dev_dest and dev_dest != 'nan':
            G.add_edge(dest, dev_dest, type='has_device')
        if ip_dest and ip_dest != 'nan':
            G.add_edge(dest, ip_dest, type='has_ip')
            
        # Collect mule flags
        if pd.notna(row.get('dest_mule_cluster_id')):
            mule_flags[dest] = True
            
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    print("Computing PageRank...")
    pagerank = nx.pagerank(G, alpha=0.85)
    
    print("Computing Betweenness Centrality (approximate)...")
    # Approximate with k=100 for speed
    betweenness = nx.betweenness_centrality(G, k=100, seed=42)
    
    print("Computing Louvain Communities...")
    partition = community_louvain.best_partition(G)
    
    print("Exporting lookup...")
    lookup = {}
    for node in G.nodes():
        lookup[node] = {
            'pagerank': pagerank.get(node, 0.0),
            'betweenness': betweenness.get(node, 0.0),
            'community': partition.get(node, -1),
            'mule_cluster_flag': mule_flags.get(node, False)
        }
        
    os.makedirs('../data/processed', exist_ok=True)
    with open('../data/processed/entity_graph_features.json', 'w') as f:
        json.dump(lookup, f)
        
    print("Lookup exported to data/processed/entity_graph_features.json")

if __name__ == '__main__':
    build_graph_and_export()
