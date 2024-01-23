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
import copy
from matplotlib.widgets import RectangleSelector


class ManualGraph(QWidget):
    def __init__(self, data, tab, gating):
        super().__init__()
        self.data = data
        self.tab = tab
        self.gating = gating
        self.count = None
        self.initUI()
    
    def initUI(self):
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        final_layout = QHBoxLayout(self)
        gating_layout = QVBoxLayout()
        layout = QVBoxLayout()
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        # gating_layout
        gating_label = QLabel("Gating history")
        gating_layout.addWidget(gating_label)
        gating_list = QListWidget()
        gating_list.addItems(self.gating)
        gating_layout.addWidget(gating_list)

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
        self.mode_btn = QPushButton("Gating_mode")
        self.mode_btn.setCheckable(True)
        self.mode_btn.toggled.connect(self.on_btn_toggled)
        gating_btn = QPushButton("Gating")
        gating_btn.clicked.connect(self.gating_data)
        toolbar = NavigationToolbar(self.canvas)
        H2_layout.addWidget(toolbar)
        H2_layout.addWidget(self.mode_btn)
        H2_layout.addWidget(gating_btn)
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

        self.rs = RectangleSelector(self.ax, self.on_select, useblit=True,
                                    button=[1], minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)
        self.rs.set_active(False)

        self.canvas.draw()

        final_layout.addLayout(layout,3.5)
        final_layout.addLayout(gating_layout,1)
        
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
        self.rs = RectangleSelector(self.ax, self.on_select, useblit=True,
                                    button=[1], minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)
        if self.mode_btn.isChecked():
            self.rs.set_active(True)
        else:
            self.rs.set_active(False)
        
        self.canvas.draw()

    def gating_data(self): # gating 버튼 누르면 실행
        if self.select_data is None:
            print("no select data")
            return
        tab_name = (f"{round(self.x1, 3)} <= {self.x_axis_combo.currentText()} <= {round(self.x2, 3)}\n"
                        f"{round(self.y1, 3)} <= {self.y_axis_combo.currentText()} <= {round(self.y2, 3)}")
        
        name, ok_pressed = QInputDialog.getText(self, 'Gating Name', 'Enter Name:', text=tab_name)
        if ok_pressed and name:
            tab_name = name

            new_gating = copy.deepcopy(self.gating)
            new_gating.append('↓')
            new_gating.append(tab_name)
            a = ManualGraph(self.select_data,self.tab,new_gating)
            
            index = self.tab.addTab(a,tab_name)
            self.tab.setTabToolTip(index,tab_name)
    
    def on_select(self,eclick, erelease):
        if self.count:
            self.count.remove()

        self.x1, self.x2 = min(eclick.xdata, erelease.xdata), max(eclick.xdata, erelease.xdata)
        self.y1, self.y2 = min(eclick.ydata, erelease.ydata), max(eclick.ydata, erelease.ydata)
        
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        center_x = min(self.x1, self.x2) + width / 2
        center_y = max(self.y1, self.y2) + height / 10

        self.select_data = self.data[(self.x_data >= self.x1) & (self.x_data <= self.x2) & 
                                    (self.y_data >= self.y1) & (self.y_data <= self.y2)]
        
        percentage = str(round((self.select_data.shape[0]/self.data.shape[0])*100,2))+"%"
        self.count = self.ax.text(center_x, center_y, percentage, ha='center', va='center', color='red')
        plt.draw()
    
    def on_btn_toggled(self, checked):
        if checked:
            # 버튼이 눌러져 있는 상태
            self.mode_btn.setStyleSheet("background-color: lightblack;")
            self.rs.set_active(True)
        else:
            # 버튼이 떼어져 있는 상태
            self.mode_btn.setStyleSheet("")
            self.rs.set_active(False)
            self.rs.extents = (0, 0, 0, 0)
            if self.count:
                self.count.set_visible(False)
                plt.draw()
            self.select_data = None