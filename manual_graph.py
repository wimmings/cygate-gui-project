import sys
import os

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

from sklearn.manifold import TSNE
from matplotlib import pyplot as plt

from PySide6 import QtUiTools, QtGui
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #plot gui 내에 띄우기
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import copy
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QToolBar
from PySide6.QtGui import QAction

from matplotlib.colors import LogNorm
from matplotlib import cm
import mpl_scatter_density # adds projection='scatter_density'


class ManualGraph(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.initUI()
    
    def initUI(self):
        self.fig = plt.figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()
        # X-axis combo box
        x_axis_label = QLabel("X-axis:")
        H_layout.addWidget(x_axis_label)
        self.x_axis_combo = QComboBox()
        H_layout.addWidget(self.x_axis_combo)
        
        # Y-axis combo box
        y_axis_label = QLabel("Y-axis:")
        H_layout.addWidget(y_axis_label)
        self.y_axis_combo = QComboBox()
        H_layout.addWidget(self.y_axis_combo)

        layout.addLayout(H_layout)

        pick_button = QPushButton("Pick")
        pick_button.clicked.connect(self.pick_data)
        toolbar = NavigationToolbar(self.canvas)
        H2_layout.addWidget(toolbar)
        H2_layout.addWidget(pick_button)
        layout.addLayout(H2_layout)

        layout.addWidget(self.canvas)
        self.x_axis_combo.addItems(self.data.columns[:-1])
        self.y_axis_combo.addItems(self.data.columns[:-1])
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        
        self.x_data = self.data[x_column]
        self.y_data = self.data[y_column]

        cmap = copy.copy(cm.get_cmap("jet"))
        cmap.set_under(alpha=0)

        self.ax = self.fig.add_subplot(1, 1, 1, projection='scatter_density')
        self.ax.set_xlabel(x_column)
        self.ax.set_ylabel(y_column)
        self.ax.set_title(f' {x_column} : {y_column}')
        density = self.ax.scatter_density(self.x_data, self.y_data, cmap=cmap,
                                            norm=LogNorm(vmin=0.5, vmax=self.x_data.size),
                                    dpi=36, downres_factor=2)
        self.fig.colorbar(density, label='Number of points per pixel')
        self.ax.set_xlim(min(self.x_data),max(self.x_data))
        self.ax.set_ylim(min(self.y_data),max(self.y_data))
        self.x_axis_combo.currentIndexChanged.connect(self.plot_manual_change)
        self.y_axis_combo.currentIndexChanged.connect(self.plot_manual_change)
        
        self.canvas.draw()
        
    def plot_manual_change(self): # manual combo box 값 변화시 실행
        self.fig.clear()
        
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        self.x_data = self.data[x_column]
        self.y_data = self.data[y_column]
        
        cmap = copy.copy(cm.get_cmap("jet"))
        cmap.set_under(alpha=0)

        self.ax = self.fig.add_subplot(1, 1, 1, projection='scatter_density')
        self.ax.set_xlabel(x_column)
        self.ax.set_ylabel(y_column)
        self.ax.set_title(f' {x_column} : {y_column}')
        density = self.ax.scatter_density(self.x_data, self.y_data, cmap=cmap, 
                                    norm=LogNorm(vmin=0.5, vmax=self.x_data.size),
                                    dpi=36, downres_factor=2)
        self.fig.colorbar(density, label='Number of points per pixel')
        self.ax.set_xlim(min(self.x_data),max(self.x_data))
        self.ax.set_ylim(min(self.y_data),max(self.y_data))
        
        self.canvas.draw()

    def pick_data(self): # pick 버튼 누르면 실행
        print("미완 프로세스")
        """pick_tab = QWidget()
        name = "pick_" + self.name
        self.tab_widget.addTab(pick_tab,name)

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        data = self.data[(self.x_data >= x_min) & (self.x_data <= x_max) & 
                                    (self.y_data >= y_min) & (self.y_data <= y_max)]
        self.plot_manual(pick_tab)
        
        self.plot_manual_change()"""