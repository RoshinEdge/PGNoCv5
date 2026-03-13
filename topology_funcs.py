# topology_funcs.py
import networkx as nx
import math


def generate_topology(topology, node_number, width=None, s_params=None):
    try:
        if topology == "Mesh":
            return mesh_2D(node_number, width)
        elif topology == "Thorus":
            return thorus(node_number, width)
        elif topology == "Hypercube":
            return hypercube(node_number)
        elif topology == "WK_recursive":
            return WK_recursive(node_number, width, s_params)
        elif topology == "Circulant_2_3":
            return circulant(node_number, [2, 3])
        elif topology == "Circulant":
            return circulant(node_number, s_params)
        else:
            return nx.Graph()
    except:
        return nx.Graph()


def mesh_2D(node_number, width):
    G = nx.Graph()
    size = node_number // width
    G.add_nodes_from(range(node_number))

    for row in range(size):
        for col in range(width - 1):
            node = row * width + col
            G.add_edge(node, node + 1)

    for col in range(width):
        for row in range(size - 1):
            node = row * width + col
            G.add_edge(node, node + width)
    return G


def thorus(node_number, width):
    G = mesh_2D(node_number, width)
    size = node_number // width

    for row in range(size):
        G.add_edge(row * width, row * width + width - 1)

    for col in range(width):
        G.add_edge(col, (size - 1) * width + col)
    return G


def hypercube(node_number):
    dim = int(math.log2(node_number))
    return nx.hypercube_graph(dim)


def WK_recursive(node_number, width, s_params):
    try:
        L = int(math.log(node_number, width))
        if width ** L != node_number:
            return nx.Graph()

        G = nx.Graph()
        cluster_size = width
        clusters = []

        for _ in range(width ** (L - 1)):
            cluster = nx.complete_graph(cluster_size)
            clusters.append(cluster)
            G = nx.disjoint_union(G, cluster)

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                for node in range(cluster_size):
                    G.add_edge(
                        i * cluster_size + node,
                        j * cluster_size + node
                    )
        return G
    except:
        return nx.Graph()


def circulant(node_number, s):
    G = nx.Graph()
    G.add_nodes_from(range(node_number))
    for i in range(node_number):
        for k in s:
            G.add_edge(i, (i + k) % node_number)
            G.add_edge(i, (i - k) % node_number)
    return G


def gen_router_wires(topology, node_number, width, k, s_params=None):
    connections = []

    if topology == "Thorus":
        cons = _thorus_wires(node_number, width, k)
    elif topology == "Mesh":
        cons = _mesh_wires(node_number, width, k)
    elif topology == "Circulant":
        cons = _circulant_wires(node_number, s_params, k)
    else:
        cons = [-1] * 4

    # Помечаем внешние соединения
    marked_cons = []
    for c in cons:
        if c == -1:
            marked_cons.append(('ext', -1))  # Внешнее соединение
        else:
            marked_cons.append(('local', c))

    return marked_cons


def _thorus_wires(node_number, width, k):
    row = k // width
    col = k % width
    N = ((row - 1) % (node_number // width)) * width + col
    S = ((row + 1) % (node_number // width)) * width + col
    W = row * width + (col - 1) % width
    E = row * width + (col + 1) % width
    return [N, S, W, E]


def _mesh_wires(node_number, width, k):
    row = k // width
    col = k % width
    N = (row - 1) * width + col if row > 0 else -1
    S = (row + 1) * width + col if row < (node_number // width - 1) else -1
    W = row * width + (col - 1) if col > 0 else -1
    E = row * width + (col + 1) if col < width - 1 else -1
    return [N, S, W, E]


def _circulant_wires(node_number, s, k):
    return [(k + offset) % node_number for offset in s] + \
        [(k - offset) % node_number for offset in s]
