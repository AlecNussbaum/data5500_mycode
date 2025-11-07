
import networkx as nx
G = nx.Graph()



def count_nodes(graph: nx.Graph) -> int:

    return graph.number_of_nodes()


if __name__ == "__main__":

    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4])
    print("Manual Test - Number of nodes:", count_nodes(G))

    K_5 = nx.complete_graph(5)
    print("Complete Graph (K5) - Number of nodes:", count_nodes(K_5))