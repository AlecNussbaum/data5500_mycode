return sum(1 for _, degree in graph.degree() if degree > threshold)


if __name__ == "__main__":

    G = nx.Graph()
    G.add_edges_from([
        (1, 2), (1, 3), (1, 4), (1, 5),
        (1, 6), (1, 7), (2, 3), (3, 4),
    ])
    print("Manual Test - Nodes with degree > 5:", count_high_degree_nodes(G))  # Expected: 1 (node 1)

    ba_graph = nx.barabasi_albert_graph(30, 6)
    print("Barabási–Albert Graph - Nodes with degree > 5:",
          count_high_degree_nodes(ba_graph, threshold=5))