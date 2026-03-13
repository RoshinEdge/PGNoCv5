# separ_func.py
import topology_funcs


def generate_segment(segment_num, nodes, node_number, width, topology, s_params):
    code = []
    code.append(f"// Segment {segment_num} - {topology} topology\n")
    code.append("`timescale 1ns / 1ps\n\n")
    code.append(f"module FPGA_Segment_{segment_num}(\n")
    code.append("\tinput clk,\n")
    code.append("\tinput rst_n,\n")

    # Ports declarations
    for node in nodes:
        code.append(f"\tinput [31:0] N_in_{node}, S_in_{node}, W_in_{node}, E_in_{node},\n")
        code.append(f"\toutput [31:0] N_out_{node}, S_out_{node}, W_out_{node}, E_out_{node},\n")

    code.append("\toutput [31:0] data_out\n")
    code.append(");\n\n")

    # Router instances
    for node in nodes:
        neighbors = topology_funcs.gen_router_wires(topology, node_number, width, node, s_params)
        code.append(f"router r{node} (\n")
        code.append(f"\t.clk(clk),\n")
        code.append(f"\t.rst_n(rst_n),\n")
        code.append(f"\t.N(N_in_{node}), .S(S_in_{node}), .W(W_in_{node}), .E(E_in_{node}),\n")
        code.append(f"\t.N_out(N_out_{node}), .S_out(S_out_{node}), .W_out(W_out_{node}), .E_out(E_out_{node})\n")
        code.append(");\n\n")

    code.append("endmodule\n")
    return code


def generate_global_network(segments, node_number, width, topology):
    code = []
    code.append("// Global Network - {topology}\n")
    code.append("`timescale 1ns / 1ps\n\n")
    code.append("module Top_Network(\n")
    code.append("\tinput clk,\n")
    code.append("\tinput rst_n\n")
    code.append(");\n\n")

    # Генерация межчиповых соединений
    for i in range(len(segments)):
        for j in range(len(segments)):
            if i != j:
                code.append(f"wire [31:0] fpga{i}_to_fpga{j};\n")

    # Instantiate all segments
    for i, seg in enumerate(segments):
        code.append(f"FPGA_Segment_{i} seg_{i} (\n")
        code.append("\t.clk(clk),\n")
        code.append("\t.rst_n(rst_n),\n")

        # Connect inter-segment links
        for node in seg:
            neighbors = topology_funcs.gen_router_wires(topology, node_number, width, node)
            for dir in ['N', 'S', 'W', 'E']:
                if neighbors[['N', 'S', 'W', 'E'].index(dir)] not in seg:
                    code.append(f"\t.{dir}_in_{node}({dir}_wire_{node}),\n")
                    code.append(f"\t.{dir}_out_{node}({dir}_wire_{node}),\n")

        code.append("\t.data_out()\n")
        code.append(");\n\n")

    code.append("endmodule\n")
    return code
