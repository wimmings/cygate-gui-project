import os
import pandas as pd
from matplotlib import pyplot as plt
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import copy
from matplotlib.colors import LogNorm
from matplotlib import cm
from matplotlib.widgets import RectangleSelector
from matplotlib.colors import ListedColormap
from matplotlib.colors import to_hex
import mpl_scatter_density

class ManualGraph(QWidget):
    def __init__(self, data, tab, gating, csv_name):
        super().__init__()
        self.data = data
        self.tab = tab
        self.gating = gating
        self.count = None
        self.csv_name = csv_name
        self.selected_list = []
        self.initUI()
    
    def initUI(self):
        #self.data.to_csv(self.csv_name,index=False)
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        final_layout = QHBoxLayout(self)
        gating_layout = QVBoxLayout()
        gating_sub_layout = QHBoxLayout()
        layout = QVBoxLayout()
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()
        plot_mode_layout = QHBoxLayout()
        btn_layout = QGridLayout()

        # gating_layout
        gating_label = QLabel("Gating history")
        gating_layout.addWidget(gating_label)
        gating_list = QListWidget()
        gating_list.addItems(self.gating)
        gating_layout.addWidget(gating_list)

        # legend
        plot_legend_label = QLabel("Plot legend")
        gating_sub_layout.addWidget(plot_legend_label)

        select_all_button = QPushButton('Select All')
        select_all_button.clicked.connect(self.select_all)

        deselect_all_button = QPushButton('Deselect All')
        deselect_all_button.clicked.connect(self.deselect_all)

        gating_sub_layout.addWidget(select_all_button)
        gating_sub_layout.addWidget(deselect_all_button)
        gating_layout.addLayout(gating_sub_layout)
        self.plot_legend = QListWidget()
        self.plot_legend.setSelectionMode(QListWidget.NoSelection)
        self.plot_legend.itemChanged.connect(self.change_color)
        gating_layout.addWidget(self.plot_legend)

        # A, B 그룹 생성
        group_ab = QButtonGroup(self)
        self.radio_btn_a = QRadioButton('Scatter plot')
        self.radio_btn_b = QRadioButton('Bar plot')
        group_ab.addButton(self.radio_btn_a)
        group_ab.addButton(self.radio_btn_b)
        self.radio_btn_a.setChecked(True)  # 기본 선택을 A로 설정
        
        self.radio_btn_a.toggled.connect(self.on_radio_btn_a_toggled)  # A 버튼이 토글될 때마다 호출
        self.radio_btn_b.toggled.connect(self.on_radio_btn_b_toggled)  # B 버튼이 토글될 때마다 호출

        plot_mode_layout.addWidget(self.radio_btn_a)
        plot_mode_layout.addWidget(self.radio_btn_b)

        spacer_label = QLabel("")
        plot_mode_layout.addWidget(spacer_label)

        # 3D mode btn
        self.d3_mode_btn = QPushButton("3D mode")
        self.d3_mode_btn.setCheckable(True)
        self.d3_mode_btn.setEnabled(False)
        self.d3_mode_btn.toggled.connect(self.d3_plot)

        self.name_sep_btn = QPushButton("Background")
        self.name_sep_btn.toggled.connect(self.name_graph)
        self.name_sep_btn.setCheckable(True)

        plot_mode_layout.addWidget(self.d3_mode_btn)
        plot_mode_layout.addWidget(self.name_sep_btn)

        layout.addLayout(plot_mode_layout)

        # X-axis combo box
        x_axis_label = QLabel("X-axis:")
        H_layout.addWidget(x_axis_label)
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.setFixedWidth(100)
        H_layout.addWidget(self.x_axis_combo)

        spacer_label = QLabel("")
        H_layout.addWidget(spacer_label)
        
        # Y-axis combo box
        y_axis_label = QLabel("Y-axis:")
        H_layout.addWidget(y_axis_label)
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.setFixedWidth(100)
        H_layout.addWidget(self.y_axis_combo)

        spacer_label = QLabel("")
        H_layout.addWidget(spacer_label)

        # Z-axis combo box
        z_axis_label = QLabel("Z-axis:")
        H_layout.addWidget(z_axis_label)
        self.z_axis_combo = QComboBox()
        self.z_axis_combo.setFixedWidth(100)

        
        group_z = QButtonGroup(self)
        self.radio_btn_density = QRadioButton('Density')
        self.radio_btn_feature = QRadioButton('Feature')
        self.radio_btn_label = QRadioButton('Name')
        group_z.addButton(self.radio_btn_density)
        group_z.addButton(self.radio_btn_feature)
        group_z.addButton(self.radio_btn_label)
        self.radio_btn_density.setChecked(True)  # 기본 선택을 A로 설정
        self.z_axis_combo.setEnabled(False)
        self.radio_btn_density.toggled.connect(self.on_radio_btn_density_toggled)  # A 버튼이 토글될 때마다 호출
        self.radio_btn_feature.toggled.connect(self.on_radio_btn_feature_toggled)  # B 버튼이 토글될 때마다 호출
        self.radio_btn_label.toggled.connect(self.on_radio_btn_label_toggled)  # C 버튼이 토글될 때마다 호출
        H_layout.addWidget(self.radio_btn_density)
        H_layout.addWidget(self.radio_btn_feature)
        H_layout.addWidget(self.z_axis_combo)
        H_layout.addWidget(self.radio_btn_label)
        
        layout.addLayout(H_layout)
        self.gating_btn = QPushButton("Gating")
        self.gating_btn.clicked.connect(self.gating_data)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        
        toolbar = NavigationToolbar(self.canvas)
        H2_layout.addWidget(toolbar)
        H2_layout.addLayout(btn_layout)
        
        btn_layout.addWidget(self.gating_btn,0,1)
        btn_layout.addWidget(self.save_btn,0,2)
        
        layout.addLayout(H2_layout)

        layout.addWidget(self.canvas)
        for i in self.data.columns:
            if not(self.data[i].dtype == 'object' or self.data[i].dtype == 'int'):
                self.x_axis_combo.addItem(i)
                self.y_axis_combo.addItem(i)
                self.z_axis_combo.addItem(i)
        
        self.plot_manual_change()
        
        self.x_axis_combo.currentIndexChanged.connect(self.plot_manual_change)
        self.y_axis_combo.currentIndexChanged.connect(self.plot_manual_change)
        self.z_axis_combo.currentIndexChanged.connect(self.plot_manual_change)

        final_layout.addLayout(layout,3.5)
        final_layout.addLayout(gating_layout,1)
    
    def on_radio_btn_a_toggled(self, checked):
        if checked:
            if self.radio_btn_density.isChecked():
                self.on_radio_btn_density_toggled(True)
            elif self.radio_btn_feature.isChecked():
                self.on_radio_btn_feature_toggled(True)
            else:
                self.on_radio_btn_label_toggled(True)
            self.radio_btn_density.setEnabled(True)
            self.radio_btn_feature.setEnabled(True)
            self.radio_btn_label.setEnabled(True)
            self.x_axis_combo.setEnabled(True)
            self.y_axis_combo.setEnabled(True)
            

    def on_radio_btn_b_toggled(self, checked):
        if checked:
            self.fig.clear()
            self.plot_legend.clear()   
            self.ax = self.fig.add_subplot(1, 1, 1)

            count = self.data['Name'].value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            legend_color_map = [to_hex(cmap(i)) for i in range(len(values))]  # 색상을 RGB로 변환
            self.selected_list = []
            for i in range(len(values)):
                self.ax.bar(names[i], values[i],color = name_color_map(i))
                item_widget = QListWidgetItem()
                item_widget.setText(str(names[i]))  # 항목의 텍스트 설정
                item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                item_widget.setCheckState(Qt.Unchecked)
                item_widget.setFlags(item_widget.flags() | Qt.ItemIsUserCheckable)  # Ensure item is checkable
                self.plot_legend.addItem(item_widget)
                
            self.ax.set_xlabel(self.x_axis_combo.currentText())
            self.ax.set_ylabel('Count')
            self.ax.set_xticks(range(len(names)))
            self.ax.set_xticklabels(names, rotation=45, ha='right')

            self.ax.set_title('Bar plot')
            self.canvas.draw()
            self.rs.extents = (0, 0, 0, 0)
            self.x_axis_combo.setEnabled(False)
            self.y_axis_combo.setEnabled(False)
            self.z_axis_combo.setEnabled(False)
            self.radio_btn_density.setEnabled(False)
            self.radio_btn_feature.setEnabled(False)
            self.radio_btn_label.setEnabled(False)
            self.d3_mode_btn.setChecked(False)
            self.d3_mode_btn.setEnabled(False)
            self.gating_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.name_sep_btn.setEnabled(False)
    
    def on_radio_btn_density_toggled(self, checked):
        if checked:
            self.z_axis_combo.setEnabled(False)
            self.plot_manual_change()
    def on_radio_btn_feature_toggled(self, checked):
        if checked:
            self.z_axis_combo.setEnabled(True)
            self.plot_manual_change()
    def on_radio_btn_label_toggled(self, checked):
        if checked:
            self.z_axis_combo.setEnabled(False)
            self.plot_manual_change()

    def plot_manual_change(self): # manual combo box 값 변화시 실행
        self.fig.clear()
        self.plot_legend.clear()
        self.d3_mode_btn.setChecked(False)
        self.d3_mode_btn.setEnabled(False)
        self.gating_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.name_sep_btn.setEnabled(True)
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()

        self.x_data = self.data[x_column]
        self.y_data = self.data[y_column]
        if self.radio_btn_density.isChecked():
            cmap = copy.copy(cm.get_cmap("jet"))
            cmap.set_under(alpha=0)
            self.ax = self.fig.add_subplot(1, 1, 1, projection='scatter_density')
            density = self.ax.scatter_density(self.x_data, self.y_data, cmap=cmap, 
                                        norm=LogNorm(vmin=0.5, vmax=self.x_data.size),
                                        dpi=36, downres_factor=2)
            self.fig.colorbar(density, label='Number of points per pixel')
        elif self.radio_btn_feature.isChecked():
            z_column = self.z_axis_combo.currentText()
            self.z_data = self.data[z_column]
            self.ax = self.fig.add_subplot(1, 1, 1)
            
            scatter = self.ax.scatter(self.x_data, self.y_data,c=self.z_data,cmap='viridis',alpha=0.5)
            self.fig.colorbar(scatter, label= f'value of {z_column}')
            self.d3_mode_btn.setEnabled(True)
        else:
            self.ax = self.fig.add_subplot(1, 1, 1)
            tmp_data = pd.read_csv(self.csv_name)
            self.data['Name'] = tmp_data.loc[self.data.index,'Name']
            self.z_data = self.data['Name']
            unique_names = self.z_data.unique()
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            legend_color_map = [to_hex(cmap(i)) for i in range(len(unique_names))]  # 색상을 RGB로 변환
            self.selected_list = []
            for i, name in enumerate(unique_names):
                mask = (self.z_data == name)
                self.ax.scatter(self.x_data[mask], self.y_data[mask], label=name, color=name_color_map(i),alpha=0.5)
                item_widget = QListWidgetItem()
                item_widget.setText(str(name))  # 항목의 텍스트 설정
                item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                item_widget.setCheckState(Qt.Unchecked)
                item_widget.setFlags(item_widget.flags() | Qt.ItemIsUserCheckable)
                self.plot_legend.addItem(item_widget)
        self.ax.set_xlabel(x_column)
        self.ax.set_ylabel(y_column)
        self.ax.set_title(f' {x_column} : {y_column}')
        self.ax.set_xlim(min(self.x_data),max(self.x_data))
        self.ax.set_ylim(min(self.y_data),max(self.y_data))
        self.rs = RectangleSelector(self.ax, self.on_select, useblit=True,
                                    button=[3], minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)
        if self.d3_mode_btn.isChecked() or self.radio_btn_b.isChecked() or self.name_sep_btn.isChecked():
            self.rs.set_active(False)
        else:
            self.rs.set_active(True)
        
        if self.name_sep_btn.isChecked():
            self.name_sep_btn.setChecked(False)
        
        self.canvas.draw()

    def d3_plot(self):
        if self.d3_mode_btn.isChecked():
            self.rs.set_active(False)
            self.gating_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.name_sep_btn.setEnabled(False)

            self.fig.clear()
            x_column = self.x_axis_combo.currentText()
            y_column = self.y_axis_combo.currentText()
            z_column = self.z_axis_combo.currentText()
            self.ax = self.fig.add_subplot(1 ,1 ,1, projection='3d')
            scatter = self.ax.scatter(self.x_data, self.y_data, self.z_data, c=self.z_data, cmap='viridis',alpha=0.5)
            self.fig.colorbar(scatter, label= f'value of {z_column}')
            self.d3_mode_btn.setEnabled(True)
            self.ax.set_xlabel(x_column)
            self.ax.set_ylabel(y_column)
            self.ax.set_zlabel(z_column)
            self.ax.set_title('3D Scatter Plot')
            self.ax.set_xlim(min(self.x_data),max(self.x_data))
            self.ax.set_ylim(min(self.y_data),max(self.y_data))
            self.ax.set_zlim(min(self.z_data),max(self.z_data))
            self.canvas.draw()
        else:
            self.gating_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.name_sep_btn.setEnabled(True)
            self.plot_manual_change()

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
            a = ManualGraph(self.select_data,self.tab,new_gating, self.csv_name)
            
            index = self.tab.addTab(a,tab_name)
            self.tab.setTabToolTip(index,tab_name)
    
    def on_select(self,eclick, erelease):
        if self.count:
            self.count.remove()

        self.x1, self.x2 = min(eclick.xdata, erelease.xdata), max(eclick.xdata, erelease.xdata)
        self.y1, self.y2 = min(eclick.ydata, erelease.ydata), max(eclick.ydata, erelease.ydata)
        
        # width = self.x2 - self.x1
        # height = self.y2 - self.y1
        # center_x = min(self.x1, self.x2) + width / 2
        # center_y = max(self.y1, self.y2) + height / 10
        self.select_data = self.data[(self.x_data >= self.x1) & (self.x_data <= self.x2) & 
                                    (self.y_data >= self.y1) & (self.y_data <= self.y2)]
        
        percentage = str(round((self.select_data.shape[0]/self.data.shape[0])*100,2))+"%"
        #self.count = self.ax.text(center_x, center_y, percentage, ha='center', va='center', color='red')
        self.count = self.fig.text(0.7,0.95, "Gating percent: " + percentage, ha='left', va='top', color='red')
        plt.draw()
    
        
    def save_data(self):
        choice_csv = QMessageBox()
        choice_csv.setWindowTitle("Choice Save Location")
        choice_csv.setText("New CSV or Update CSV")
        new_button = choice_csv.addButton("New CSV", QMessageBox.AcceptRole)
        update_button = choice_csv.addButton("Update CSV", QMessageBox.RejectRole)
        choice_csv.exec()

        if choice_csv.clickedButton() == new_button:
            name = self.open_df()
            if name is not None:
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                tmp_data = pd.read_csv(self.csv_name)
                tmp_data.loc[((self.data[self.x_axis_combo.currentText()] >= x_min) & (self.data[self.x_axis_combo.currentText()] <= x_max) & 
                                            (self.data[self.y_axis_combo.currentText()] >= y_min) & (self.data[self.y_axis_combo.currentText()] <= y_max)),'Name'] = name
                tmp_data.to_csv(self.get_unique_filename(), index=False)
        elif choice_csv.clickedButton() == update_button:
            name = self.open_df()
            if name is not None:
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                tmp_data = pd.read_csv(self.csv_name)
                self.data.loc[((self.data[self.x_axis_combo.currentText()] >= x_min) & (self.data[self.x_axis_combo.currentText()] <= x_max) & 
                                            (self.data[self.y_axis_combo.currentText()] >= y_min) & (self.data[self.y_axis_combo.currentText()] <= y_max)),'Name'] = name
                tmp_data.loc[self.data.index,'Name'] = self.data['Name']
                tmp_data.to_csv(self.csv_name, index=False)
                self.plot_manual_change()
        else:
            print("cancel")

    def get_unique_filename(self):
        filename, file_extension = os.path.splitext(self.csv_name)
        index = 1
        while True:
            new_filename = f"{filename}_{index}{file_extension}"
            if not os.path.exists(new_filename):
                return new_filename
            index += 1
            
    def open_df(self):
        current_tab_index = self.tab.currentIndex()
        current_tab_name = self.tab.tabText(current_tab_index)
        name, ok_pressed = QInputDialog.getText(self, 'Input Name', 'Enter Name:', text=current_tab_name)
        if ok_pressed and name:
            return name
        
    def name_graph(self):
        self.plot_legend.clear()
        
        if not self.name_sep_btn.isChecked():
            self.gating_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.plot_manual_change()
            return
        
        self.gating_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.fig.clear()

        # Read data
        tmp_data = pd.read_csv(self.csv_name)
        unique_names_tmp = tmp_data['Name'].unique()
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        x_data = tmp_data[x_column]
        y_data = tmp_data[y_column]
        
        # Set up plot
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel(x_column)
        self.ax.set_ylabel(y_column)
        self.ax.set_title(f'Back Ground of {x_column} : {y_column}')

        # Create color map
        cmap = plt.cm.get_cmap('tab20', len(unique_names_tmp))
        colors = [to_hex(cmap(i)) for i in range(len(unique_names_tmp))]

        # Create scatter plot and legend items
        self.selected_list = []
        
        for i, name in enumerate(unique_names_tmp):
            mask = tmp_data['Name'] == name
            item_widget = QListWidgetItem(name)
            item_widget.setBackground(QtGui.QColor(colors[i]))
            item_widget.setCheckState(Qt.Unchecked)
            item_widget.setFlags(item_widget.flags() | Qt.ItemIsUserCheckable)
            self.plot_legend.addItem(item_widget)
            
            # Check if data points are within the range
            x_in_range = (x_data[mask] >= self.x_data.min()) & (x_data[mask] <= self.x_data.max())
            y_in_range = (y_data[mask] >= self.y_data.min()) & (y_data[mask] <= self.y_data.max())
            in_range = x_in_range & y_in_range
            
            if in_range.any():
                self.ax.scatter(x_data[mask][in_range], y_data[mask][in_range], label=name, color=colors[i])
            else:
                self.ax.scatter(x_data[mask], y_data[mask], color='lightgray', alpha=0.1)


            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)

        # Set plot limits
        self.ax.set_xlim(x_data.min(), x_data.max())
        self.ax.set_ylim(y_data.min(), y_data.max())

        # Reset rectangle selector extents
        self.rs.extents = (0, 0, 0, 0)
        self.canvas.draw()
        
    def change_color(self, item=None):
        self.fig.clear()

        if item is not None:
            if item.checkState() == Qt.Checked:
                if item.text() not in self.selected_list:
                    self.selected_list.append(item.text())
            else:
                if item.text() in self.selected_list:
                    self.selected_list.remove(item.text())

        self.ax = self.fig.add_subplot(1, 1, 1)
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()

        if self.radio_btn_b.isChecked():
            count = self.data['Name'].value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            for i in range(len(values)):
                if len(self.selected_list) == 0:
                    self.ax.bar(names[i], values[i],color = name_color_map(i))
                elif names[i] in self.selected_list:
                    self.ax.bar(names[i], values[i],color = name_color_map(i), label = names[i])
                else:
                    self.ax.bar(names[i], values[i],color = 'lightgray')
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_xlabel(self.x_axis_combo.currentText())
            self.ax.set_ylabel('Count')
            self.ax.set_title('Bar plot')
            self.ax.set_xticks(range(len(names)))
            self.ax.set_xticklabels(names, rotation=45, ha='right')

        elif self.name_sep_btn.isChecked():
            tmp_data = pd.read_csv(self.csv_name)
            unique_names = tmp_data['Name'].unique()
            x_data = tmp_data[x_column]
            y_data = tmp_data[y_column]
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            for i, name in enumerate(unique_names):
                mask = tmp_data['Name'] == name # 'Name 버전'

                # Check if data points are within the range
                x_in_range = (x_data[mask] >= self.x_data.min()) & (x_data[mask] <= self.x_data.max())
                y_in_range = (y_data[mask] >= self.y_data.min()) & (y_data[mask] <= self.y_data.max())
                in_range = x_in_range & y_in_range

                if name in self.selected_list:
                    self.ax.scatter(x_data[mask], y_data[mask], label=name, color=name_color_map(i))
                elif in_range.any():
                    self.ax.scatter(x_data[mask][in_range], y_data[mask][in_range], label=name, color=name_color_map(i))
                else:
                    self.ax.scatter(x_data[mask], y_data[mask], color='lightgray',alpha=0.1)

            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_xlim(min(x_data),max(x_data))
            self.ax.set_ylim(min(y_data),max(y_data))
            self.ax.set_xlabel(x_column)
            self.ax.set_ylabel(y_column)
            self.ax.set_title(f'Back Ground of {x_column} : {y_column}')

        else:
            self.z_data = self.data['Name'] #zcolumn 버전
            unique_names = self.z_data.unique() #zcolumn 버전
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            for i, name in enumerate(unique_names):
                mask = (self.z_data == name) #zcolumn 버전
                if len(self.selected_list) == 0:
                    self.ax.scatter(self.x_data[mask], self.y_data[mask], color=name_color_map(i),alpha=0.5)
                elif name in self.selected_list:
                    self.ax.scatter(self.x_data[mask], self.y_data[mask], label=name, color=name_color_map(i))
                else:
                    self.ax.scatter(self.x_data[mask], self.y_data[mask], color='lightgray',alpha=0.1)
            
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_xlim(min(self.x_data),max(self.x_data))
            self.ax.set_ylim(min(self.y_data),max(self.y_data))
            self.ax.set_xlabel(x_column)
            self.ax.set_ylabel(y_column)
            self.ax.set_title(f' {x_column} : {y_column}')

            self.rs = RectangleSelector(self.ax, self.on_select, useblit=True,
                                    button=[3], minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)
            if self.d3_mode_btn.isChecked() or self.radio_btn_b.isChecked() or self.name_sep_btn.isChecked():
                self.rs.set_active(False)
            else:
                self.rs.set_active(True)
            
        
        self.canvas.draw()

    
    def select_all(self):
        self.plot_legend.blockSignals(True)
        for index in range(self.plot_legend.count()):
            item = self.plot_legend.item(index)
            item.setCheckState(Qt.Checked)
            if item.text() not in self.selected_list:
                self.selected_list.append(item.text())
        self.plot_legend.blockSignals(False)
        self.change_color()

    def deselect_all(self):
        self.plot_legend.blockSignals(True)
        self.selected_list = []
        for index in range(self.plot_legend.count()):
            item = self.plot_legend.item(index)
            item.setCheckState(Qt.Unchecked)
        self.plot_legend.blockSignals(False)
        self.change_color()