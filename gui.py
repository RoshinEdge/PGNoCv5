# gui.py
import sys
import ast
import math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QLineEdit,
                             QLabel, QGraphicsView, QFrame, QSpinBox,
                             QVBoxLayout, QComboBox, QPushButton, QMainWindow,
                             QFileDialog, QGraphicsScene)
from PyQt5 import QtGui, QtCore
import topology_funcs
import networkx as nx
import main


class UiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_graph = None

    def initUI(self):
        self.setWindowTitle('NoC Configurator')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)

        self.fpga_count_spin = QSpinBox()
        self.fpga_count_spin.setRange(2, 8)
        params_layout.addWidget(QLabel("FPGA count:"))
        params_layout.addWidget(self.fpga_count_spin)

        self.node_spin = QSpinBox()
        self.node_spin.setRange(4, 256)
        params_layout.addWidget(QLabel("Node Number:"))
        params_layout.addWidget(self.node_spin)

        self.topology_combo = QComboBox()
        self.topology_combo.addItems([
            "Mesh", "Thorus", "Hypercube",
            "WK_recursive", "Circulant_2_3", "Circulant"
        ])
        params_layout.addWidget(QLabel("Topology:"))
        params_layout.addWidget(self.topology_combo)

        self.width_edit = QLineEdit("4")
        params_layout.addWidget(QLabel("Width (for Mesh/Thorus):"))
        params_layout.addWidget(self.width_edit)

        self.params_edit = QLineEdit("[2,3]")
        params_layout.addWidget(QLabel("Topology Parameters:"))
        params_layout.addWidget(self.params_edit)

        self.canvas = QGraphicsView()
        self.scene = QGraphicsScene()
        self.canvas.setScene(self.scene)

        self.visualize_btn = QPushButton("Visualize")
        self.generate_btn = QPushButton("Generate Verilog")

        layout.addWidget(params_frame)
        layout.addWidget(self.canvas)
        layout.addWidget(self.visualize_btn)
        layout.addWidget(self.generate_btn)

        # Исправленные подключения сигналов
        self.visualize_btn.clicked.connect(self.draw_graph)
        self.generate_btn.clicked.connect(self.generate_code)

    def parse_params(self):
        try:
            params = {
                'fpga_count': self.fpga_count_spin.value(),
                'node_number': self.node_spin.value(),
                'topology': self.topology_combo.currentText(),
                'width': int(self.width_edit.text()),
                's_params': ast.literal_eval(self.params_edit.text())
            }

            if params['topology'] in ["Mesh", "Thorus"]:
                if params['node_number'] % params['width'] != 0:
                    raise ValueError("Node number must be divisible by width")
            if params['node_number'] < params['fpga_count']:
                raise ValueError("The number of nodes cannot be less than the number of FPGAs")
            return params
        except Exception as e:
            self.show_error(str(e))
            return None

    def draw_graph(self):
        params = self.parse_params()
        if not params:
            return

        try:
            self.scene.clear()
            G = topology_funcs.generate_topology(
                params['topology'],
                params['node_number'],
                params.get('width'),
                params.get('s_params')
            )

            pos = nx.spring_layout(G)

            # Исправленные константы цвета
            node_pen = QtGui.QPen(Qt.blue)
            node_brush = QtGui.QBrush(Qt.cyan)
            edge_pen = QtGui.QPen(Qt.darkGray, 2)

            for node, (x, y) in pos.items():
                self.scene.addEllipse(
                    x * 300 - 10, y * 300 - 10, 20, 20,
                    node_pen,
                    node_brush
                )
                text = self.scene.addText(str(node))
                text.setPos(x * 300 - 10, y * 300 - 10)

            for edge in G.edges():
                x1, y1 = pos[edge[0]]
                x2, y2 = pos[edge[1]]
                self.scene.addLine(x1 * 300, y1 * 300, x2 * 300, y2 * 300, edge_pen)

            # Исправленная константа аспекта
            self.canvas.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        except Exception as e:
            self.show_error(str(e))

    def generate_code(self):
        params = self.parse_params()
        if not params:
            return

        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if not directory:
                return

            ar_fpgas = self.create_partitions(params['node_number'])

            main.parse_separator(
                node_number=params['node_number'],
                width=params['width'],
                topology=params['topology'],
                ar_fpgas=ar_fpgas,
                directory=directory,
                s_params=params.get('s_params')
            )

            QMessageBox.information(self, "Success", "Files generated successfully!")

        except Exception as e:
            self.show_error(str(e))

    def create_partitions(self, node_number):
        fpga_count = self.fpga_count_spin.value()
        base = node_number // fpga_count
        remainder = node_number % fpga_count

        partitions = []
        start = 0
        for i in range(fpga_count):
            end = start + base + (1 if i < remainder else 0)
            partitions.append(list(range(start, end)))
            start = end
        return partitions

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UiMainWindow()
    window.show()
    sys.exit(app.exec_())
