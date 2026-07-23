import networkx as nx

def generate_graph_topology(universe: dict) -> dict:
    """
    Constructs Neo4j & NetworkX graph nodes, edges, and properties for entity resolution.
    Part 10 of Digital Banking Universe.
    """
    nodes = []
    edges = []
    seen_nodes = set()

    customers = universe.get("customers", [])
    transactions = universe.get("transactions", [])
    devices = universe.get("devices", [])
    locations = universe.get("locations", [])

    # 1. Customer, Account, Device, City & IP Nodes
    for idx, c in enumerate(customers):
        cust_id = c["customer_id"]
        acc_id = c["primary_account"]
        city = c.get("city", "Mumbai")

        if cust_id not in seen_nodes:
            nodes.append({"id": cust_id, "type": "Customer", "label": c["full_name"], "risk": c["risk_tier"]})
            seen_nodes.add(cust_id)

        if acc_id not in seen_nodes:
            nodes.append({"id": acc_id, "type": "Account", "label": acc_id, "risk": "NORMAL"})
            seen_nodes.add(acc_id)

        # Customer OWNS Account
        edges.append({"source": cust_id, "target": acc_id, "relationship": "OWNS"})

        # Customer LOCATED_IN City
        if city not in seen_nodes:
            nodes.append({"id": city, "type": "City", "label": city, "risk": "LOW"})
            seen_nodes.add(city)
        edges.append({"source": cust_id, "target": city, "relationship": "LOCATED_IN"})

    # Devices & IP connections
    for d in devices:
        dev_id = d["device_id"]
        if dev_id not in seen_nodes:
            nodes.append({"id": dev_id, "type": "Device", "label": dev_id, "trust": d["trust_score"]})
            seen_nodes.add(dev_id)

    # Link Customer USES Device & Device CONNECTED_TO IP
    for idx, loc in enumerate(locations[:len(devices)]):
        if idx < len(customers):
            c_id = customers[idx]["customer_id"]
            d_id = devices[idx]["device_id"]
            ip_id = loc["ip_address"]

            edges.append({"source": c_id, "target": d_id, "relationship": "USES"})

            if ip_id not in seen_nodes:
                nodes.append({"id": ip_id, "type": "IPAddress", "label": ip_id, "vpn": loc["is_vpn_proxy"]})
                seen_nodes.add(ip_id)
            edges.append({"source": d_id, "target": ip_id, "relationship": "CONNECTED_TO"})

    # Transaction Transfers & Mule Rings
    for t in transactions[:100]:
        orig = t["nameOrig"]
        dest = t["nameDest"]
        tx_type = t.get("type", "TRANSFER")

        if orig not in seen_nodes:
            nodes.append({"id": orig, "type": "Account", "label": orig, "risk": "NORMAL"})
            seen_nodes.add(orig)

        if dest not in seen_nodes:
            node_type = "Merchant" if "MERCHANT" in dest else ("Account" if "ACC" in dest else "Beneficiary")
            nodes.append({"id": dest, "type": node_type, "label": dest, "risk": "NORMAL"})
            seen_nodes.add(dest)

        rel = "PAYS" if tx_type in ["PAYMENT", "POS", "ONLINE_SHOPPING"] else "TRANSFERS"
        edges.append({"source": orig, "target": dest, "relationship": rel, "amount": t["amount"]})

        # Fraudster & Mule cluster connections
        if t.get("dest_mule_cluster_id"):
            cluster_id = t["dest_mule_cluster_id"]
            fraudster_id = f"FRAUDSTER_{cluster_id.upper()}"
            
            if cluster_id not in seen_nodes:
                nodes.append({"id": cluster_id, "type": "MuleCluster", "label": f"Mule Ring {cluster_id}", "risk": "CRITICAL"})
                seen_nodes.add(cluster_id)

            if fraudster_id not in seen_nodes:
                nodes.append({"id": fraudster_id, "type": "Fraudster", "label": f"Syndicate Leader {cluster_id}", "risk": "CRITICAL"})
                seen_nodes.add(fraudster_id)

            edges.append({"source": dest, "target": cluster_id, "relationship": "PART_OF_RING"})
            edges.append({"source": fraudster_id, "target": dest, "relationship": "CONNECTED_TO"})

    # Generate Cypher queries for Neo4j injection
    cypher_queries = [
        f"MERGE (c:{n['type']} {{id: '{n['id']}'}}) SET c.label='{n.get('label', '')}', c.risk='{n.get('risk', 'LOW')}'"
        for n in nodes[:10]
    ]

    # Compute real networkx metrics
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"], type=n["type"], label=n.get("label", ""))
    for e in edges:
        G.add_edge(e["source"], e["target"], relationship=e["relationship"])

    seed = universe.get("seed", 42)

    graph_properties = {
        "density": None,
        "connected_components": None,
        "louvain_modularity": None,
        "pagerank_max": None,
        "graph_sage_embedding_dim": None,
        "pagerank_distribution": None,
        "betweenness_centrality": None,
        "louvain_communities": None,
        "degree_distribution": None
    }

    if len(G) > 0:
        graph_properties["density"] = nx.density(G)
        
        # Connected components require undirected graph
        undirected_G = G.to_undirected()
        graph_properties["connected_components"] = nx.number_connected_components(undirected_G)
        
        try:
            communities = nx.community.louvain_communities(undirected_G, seed=seed)
            graph_properties["louvain_communities"] = [list(c) for c in communities]
            graph_properties["louvain_modularity"] = nx.community.modularity(undirected_G, communities)
        except Exception as e:
            graph_properties["louvain_communities"] = None
            graph_properties["louvain_modularity"] = {"value": None, "reason": str(e)}

        try:
            pr = nx.pagerank(G)
            graph_properties["pagerank_max"] = max(pr.values()) if pr else 0.0
            graph_properties["pagerank_distribution"] = pr
        except Exception as e:
            graph_properties["pagerank_max"] = {"value": None, "reason": str(e)}
            graph_properties["pagerank_distribution"] = None

        try:
            graph_properties["betweenness_centrality"] = nx.betweenness_centrality(G)
        except Exception as e:
            graph_properties["betweenness_centrality"] = None

        try:
            degrees = [d for n, d in G.degree()]
            deg_dist = {}
            for d in degrees:
                deg_dist[d] = deg_dist.get(d, 0) + 1
            graph_properties["degree_distribution"] = deg_dist
        except Exception as e:
            graph_properties["degree_distribution"] = None

        graph_properties["graph_sage_embedding_dim"] = {"value": None, "reason": "Requires GraphSAGE neural network pass, not computable via pure NetworkX"}
    else:
        empty_reason = {"value": None, "reason": "Empty graph"}
        for k in graph_properties:
            graph_properties[k] = empty_reason

    return {
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "cypher_sample": cypher_queries,
        "graph_properties": graph_properties
    }

