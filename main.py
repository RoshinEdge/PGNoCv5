# main.py
import separ_func
import os


def parse_separator(node_number, width, topology, ar_fpgas, directory, s_params=None):
    # Generate segment files
    segments = []
    for index, fpga_segment  in enumerate(ar_fpgas):
        try:
            # Generate segment
            code = separ_func.generate_segment(
                segment_num=index,
                nodes=fpga_segment,
                node_number=node_number,
                width=width,
                topology=topology,
                s_params=s_params
            )

            seg_file = os.path.join(directory, f"fpga_segment_{index}.v")
            with open(seg_file, "w") as f:
                f.writelines(code)

            segments.append(fpga_segment)

        except Exception as e:
            print(f"Error generating segment {index}: {str(e)}")

    # Generate global network
    try:
        global_code = separ_func.generate_global_network(
            segments=segments,
            node_number=node_number,
            width=width,
            topology=topology
        )

        global_file = os.path.join(directory, "top_network.v")
        with open(global_file, "w") as f:
            f.writelines(global_code)

    except Exception as e:
        print(f"Error generating global network: {str(e)}")
