import separ_func
import topology_funcs



node_number = 16                     #Количество роутеров в сети
ar_edges_fpga_1 = [0,1,2,3]       #Номера роутеров, релизованные в ПЛИС1
ar_edges_fpga_2 = [4,5,6,7,8,9,10,11,12,13,14,15]         #Номера роутеров, релизованные в ПЛИС2



path_sm_cpu     = " \"C:\\Project\\send_wait_recieve.mem\" "
path_fpga_1_top = "C:\\Project\\top_fpga1.v"
path_fpga_2_top = "C:\\Project\\top_fpga2.v"

topology = "Thorus"
routing  = "router_xy"
#*******************************************************************************************#



'''
separ_func.separate_NoC(1,node_number,ar_edges_fpga_1,ar_edges_fpga_2,path_fpga_1_top,"top_fpga1")
separ_func.separate_NoC(2,node_number,ar_edges_fpga_2,ar_edges_fpga_1,path_fpga_2_top,"top_fpga2")
'''

#'''
print("i"," ","[N,S,W,E]")
for i in range(0,16):
    print(i," ",topology_funcs.gen_router_wires_Mesh(16,4,i))
# '''

### test
#for i in range(0,len(orig_sour)):
#    print(str(i)+ " " + orig_sour[i])
###

print("\n ############################# \n")

ar_fpgas = [[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]
#ar_fpgas = [[0,1,2,3,4],[5,6,7,8,9],[10,11,12,13,14],[15,16,17,18,19],[20,21,22,23,24]]
#ar_fpgas = [[0,1],[2,3],[4,5],[6,7],[8,9],[10,11],[12,13],[14,15]]
#ar_fpgas = [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12],[13],[14],[15]]

graph_code = []
separ_wire = []

graph_code.append(" strict graph G { \n")

fpga_numb = 0

for i in ar_fpgas:
    if i:

        graph_code.append("subgraph cluster_{} {{ ".format(fpga_numb))
        graph_code.append("node [style=filled shape=circle];")
        graph_code.append("label = \"FPGA {}\";".format(fpga_numb))

        nodes_was = []
        for k in i:

            neighbours = topology_funcs.gen_router_wires_Mesh(node_number,4,k)
            #print(k,neighbours)
            for j in neighbours:
                #print("ok {} {}",k,j)
                if (j != -1) and (j not in nodes_was):
                    if (j in i) :  graph_code.append("{} -- {};".format(k,j))
                    else:       separ_wire.append("{} -- {};".format(k,j))
                nodes_was.append(k)
        graph_code.append("}\n")
    fpga_numb += 1

graph_code.extend(separ_wire)

graph_code.append(" }")

##@@@@@@@@@@@@@@@@@@##



node_number = 16

#ar_fpgas = [[0,1,2],[3,4,5,6,7],[8,9,10],[11,12,13,14,15]]

ar_index = 0 #only for test !!!

nodes_was = []
wires_ar = []
separ_wire = [] #to_another_fpga
from_wire  = [] #from_another_fpga


print("i"," ","[N, S, W, E]")

for i in ar_fpgas[ar_index]:
    print(i,"",topology_funcs.gen_router_wires_Mesh(node_number,4,i))
    neighbours = topology_funcs.gen_router_wires_Mesh(node_number, 4, i)
    print(i,neighbours)
    ind = 0
    for j in neighbours:
        # print("ok {} {}",k,j)
        if (j != -1) and (j not in nodes_was):
            if (j in ar_fpgas[ar_index]):
                wires_ar.append("{} -- {};".format(i, j))
            else:
                if(ind == 0):
                    separ_wire.append("N_wire_{}".format(i))
                    from_wire.append("S_wire_{}".format(j))
                elif(ind == 1):
                    separ_wire.append("S_wire_{}".format(i))
                    from_wire.append("N_wire_{}".format(j))
                elif (ind == 2):
                    separ_wire.append("W_wire_{}".format(i))
                    from_wire.append("E_wire_{}".format(j))
                else:
                    separ_wire.append("E_wire_{}".format(i))
                    from_wire.append("W_wire_{}".format(j))
        nodes_was.append(i)
        ind += 1

print(wires_ar)
print(len(separ_wire))
print(separ_wire)

wire_con_tx = "tx_ar <= {"
for i in range(0,len(separ_wire)-1):
    wire_con_tx += separ_wire[i] + ","
wire_con_tx += separ_wire[len(separ_wire)-1] + "};"

print(wire_con_tx)


wire_con_rx = "rx_ar <= {"
for i in range(0,len(from_wire)-1):
    wire_con_rx += from_wire[i] + ","
wire_con_rx += from_wire[len(from_wire)-1] + "};"

print(wire_con_rx)
##__TEST_NEW_SEPAR_FUNC_FOR_NOC__##
#'''
for index, fpga in enumerate(ar_fpgas):
    ar_code_fpga = separ_func.separ_NoC(which_fpga_number = index,node_number = 16,ar_edges_fpga = fpga, path = " ",name_module = "Top_FPGA_{}".format(1))
    my_file = open(f"BabyFile{index}.v", "w+")
    for i in ar_code_fpga:
        my_file.write(i)
    my_file.close()


#############################################################


#'''
for i in graph_code:
    print(i)
#'''