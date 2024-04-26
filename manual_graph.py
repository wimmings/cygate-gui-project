import os
import pandas as pd
from matplotlib import pyplot as plt
from PySide6 import QtGui
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
        self.initUI()
    
    def initUI(self):
        #self.data.to_csv(self.csv_name,index=False)
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        final_layout = QHBoxLayout(self)
        gating_layout = QVBoxLayout()
        layout = QVBoxLayout()
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()
        btn_layout = QGridLayout()

        # gating_layout
        gating_label = QLabel("Gating history")
        gating_layout.addWidget(gating_label)
        gating_list = QListWidget()
        gating_list.addItems(self.gating)
        gating_layout.addWidget(gating_list)

        # legend
        plot_legend_label = QLabel("Plot legend")
        gating_layout.addWidget(plot_legend_label)
        self.plot_legend = QListWidget()
        self.plot_legend.setSelectionMode(QListWidget.MultiSelection)
        self.plot_legend.itemClicked.connect(self.change_color)
        gating_layout.addWidget(self.plot_legend)

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

        # Z-axis combo box
        z_axis_label = QLabel("Z-axis:")
        H_layout.addWidget(z_axis_label)
        self.z_axis_combo = QComboBox()
        H_layout.addWidget(self.z_axis_combo)

        # 3D mode btn
        self.d3_mode_btn = QPushButton("3D mode")
        self.d3_mode_btn.setCheckable(True)
        self.d3_mode_btn.setEnabled(False)
        self.d3_mode_btn.toggled.connect(self.d3_plot)
        H_layout.addWidget(self.d3_mode_btn)

        layout.addLayout(H_layout)
        self.mode_btn = QPushButton("Gating mode")
        self.mode_btn.setCheckable(True)
        self.mode_btn.toggled.connect(self.on_btn_toggled)
        self.gating_btn = QPushButton("Gating")
        self.gating_btn.clicked.connect(self.gating_data)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.name_sep_btn = QPushButton("Name dist")
        self.name_sep_btn.toggled.connect(self.name_graph)
        self.name_sep_btn.setCheckable(True)
        toolbar = NavigationToolbar(self.canvas)
        H2_layout.addWidget(toolbar)
        H2_layout.addLayout(btn_layout)
        btn_layout.addWidget(self.mode_btn,0,0)
        btn_layout.addWidget(self.gating_btn,0,1)
        btn_layout.addWidget(self.save_btn,1,0)
        btn_layout.addWidget(self.name_sep_btn,1,1)
        layout.addLayout(H2_layout)

        layout.addWidget(self.canvas)
        self.x_axis_combo.addItems(self.data.columns[:])
        self.y_axis_combo.addItems(self.data.columns[:])
        self.z_axis_combo.addItem('None')
        self.z_axis_combo.addItems(self.data.columns[:])
        
        self.plot_type_check()
        
        self.x_axis_combo.currentIndexChanged.connect(self.plot_type_check)
        self.y_axis_combo.currentIndexChanged.connect(self.plot_type_check)
        self.z_axis_combo.currentIndexChanged.connect(self.plot_type_check)

        final_layout.addLayout(layout,3.5)
        final_layout.addLayout(gating_layout,1)
    
    def plot_type_check(self):
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()

        self.x_data = self.data[x_column]
        self.y_data = self.data[y_column]

        # 데이터 타입 확인
        x_dtype = self.x_data.dtype
        y_dtype = self.y_data.dtype

        # case 둘중 하나라도 문자형
        if x_dtype == 'object' or y_dtype == 'object':
            self.bar_plot()
        else:
            self.plot_manual_change()
        
    def bar_plot(self):
        self.fig.clear()
        self.plot_legend.clear()
        self.d3_mode_btn.setChecked(False)
        self.d3_mode_btn.setEnabled(False)
        self.mode_btn.setEnabled(False)
        self.gating_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.name_sep_btn.setEnabled(False)
        self.ax = self.fig.add_subplot(1, 1, 1)
            
        if self.x_data.dtype == 'object':
            count = self.x_data.value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            legend_color_map = [to_hex(cmap(i)) for i in range(len(values))]  # 색상을 RGB로 변환
            for i in range(len(values)):
                self.ax.bar(names[i], values[i],color = name_color_map(i))
                item_widget = QListWidgetItem()
                item_widget.setText(str(names[i]))  # 항목의 텍스트 설정
                item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                self.plot_legend.addItem(item_widget)
            self.ax.set_xlabel(self.x_axis_combo.currentText())
            self.ax.set_ylabel('Count')
        else:
            count = self.y_data.value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            legend_color_map = [to_hex(cmap(i)) for i in range(len(values))]  # 색상을 RGB로 변환
            for i in range(len(values)):
                self.ax.barh(names[i], values[i],color = name_color_map(i))
                item_widget = QListWidgetItem()
                item_widget.setText(str(names[i]))  # 항목의 텍스트 설정
                item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                self.plot_legend.addItem(item_widget)
            self.ax.set_ylabel(self.y_axis_combo.currentText())
            self.ax.set_xlabel('Count')
        # self.fig.tight_layout()
        self.ax.set_title('Bar plot')
        self.canvas.draw()
        
    def plot_manual_change(self): # manual combo box 값 변화시 실행
        self.fig.clear()
        self.plot_legend.clear()
        self.d3_mode_btn.setChecked(False)
        self.d3_mode_btn.setEnabled(False)
        self.mode_btn.setEnabled(True)
        self.gating_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.name_sep_btn.setEnabled(True)
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        z_column = self.z_axis_combo.currentText()
        if z_column == 'None':
            cmap = copy.copy(cm.get_cmap("jet"))
            cmap.set_under(alpha=0)
            self.ax = self.fig.add_subplot(1, 1, 1, projection='scatter_density')
            density = self.ax.scatter_density(self.x_data, self.y_data, cmap=cmap, 
                                        norm=LogNorm(vmin=0.5, vmax=self.x_data.size),
                                        dpi=36, downres_factor=2)
            self.fig.colorbar(density, label='Number of points per pixel')
        else:
            self.z_data = self.data[z_column]
            self.ax = self.fig.add_subplot(1, 1, 1)
            if self.z_data.dtype == 'object':
                tmp_data = pd.read_csv(self.csv_name)
                self.data['Name'] = tmp_data.loc[self.data.index,'Name']
                self.z_data = self.data[z_column]
                unique_names = self.z_data.unique()
                cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
                name_color_map = ListedColormap(cmap(range(len(unique_names))))
                legend_color_map = [to_hex(cmap(i)) for i in range(len(unique_names))]  # 색상을 RGB로 변환
                
                for i, name in enumerate(unique_names):
                    mask = (self.data[z_column] == name)
                    self.ax.scatter(self.x_data[mask], self.y_data[mask], label=name, color=name_color_map(i),alpha=0.5)
                    item_widget = QListWidgetItem()
                    item_widget.setText(str(name))  # 항목의 텍스트 설정
                    item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                    self.plot_legend.addItem(item_widget)
                
            else:
                scatter = self.ax.scatter(self.x_data, self.y_data,c=self.z_data,cmap='viridis',alpha=0.5)
                self.fig.colorbar(scatter, label= f'value of {z_column}')
                self.d3_mode_btn.setEnabled(True)
        self.ax.set_xlabel(x_column)
        self.ax.set_ylabel(y_column)
        self.ax.set_title(f' {x_column} : {y_column}')
        self.ax.set_xlim(min(self.x_data),max(self.x_data))
        self.ax.set_ylim(min(self.y_data),max(self.y_data))
        self.rs = RectangleSelector(self.ax, self.on_select, useblit=True,
                                    button=[1], minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)
        if self.mode_btn.isChecked():
            self.rs.set_active(True)
        else:
            self.rs.set_active(False)
        if self.name_sep_btn.isChecked():
            self.name_sep_btn.setChecked(False)
        
        self.canvas.draw()

    def d3_plot(self):
        if self.d3_mode_btn.isChecked():
            self.mode_btn.setEnabled(False)
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
            self.mode_btn.setEnabled(True)
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
    
    def on_btn_toggled(self, checked):
        if checked:
            # 버튼이 눌러져 있는 상태
            #self.mode_btn.setStyleSheet("background-color: lightblack;")
            self.rs.set_active(True)
        else:
            # 버튼이 떼어져 있는 상태
            #self.mode_btn.setStyleSheet("")
            self.rs.set_active(False)
            self.rs.extents = (0, 0, 0, 0)
            if self.count:
                self.count.set_visible(False)
                plt.draw()
            self.select_data = None
    
    def save_data(self):
        choice_box = QMessageBox()
        choice_box.setWindowTitle("Choice Range")
        choice_box.setText("Choice Full Range or Gating Range")
        full_range_button = choice_box.addButton("Full Range", QMessageBox.AcceptRole)
        gating_range_button = choice_box.addButton("Gating Range", QMessageBox.RejectRole)

        choice_box.exec()

        if choice_box.clickedButton() == full_range_button:
            self.full_range()
        elif choice_box.clickedButton() == gating_range_button:
            if self.select_data is None:
                print("No select data")
                return
            self.gating_range()
        else:
            print("cancel")
        

    def full_range(self):
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
            self.plot_type_check()
        else:
            print("cancel")

    def gating_range(self):
        choice_csv = QMessageBox()
        choice_csv.setWindowTitle("Choice Save Location")
        choice_csv.setText("New CSV or Update CSV")
        new_button = choice_csv.addButton("New CSV", QMessageBox.AcceptRole)
        update_button = choice_csv.addButton("Update CSV", QMessageBox.RejectRole)
        choice_csv.exec()

        
        if choice_csv.clickedButton() == new_button:
            name = self.open_df()
            if name is not None:
                tmp_data = pd.read_csv(self.csv_name)
                tmp_data.loc[((self.data[self.x_axis_combo.currentText()] >= self.x1) & (self.data[self.x_axis_combo.currentText()] <= self.x2) & 
                                            (self.data[self.y_axis_combo.currentText()] >= self.y1) & (self.data[self.y_axis_combo.currentText()] <= self.y2)),'Name'] = name
                tmp_data.to_csv(self.get_unique_filename(), index=False)
        elif choice_csv.clickedButton() == update_button:
            name = self.open_df()
            if name is not None:
                tmp_data = pd.read_csv(self.csv_name)
                self.data.loc[((self.data[self.x_axis_combo.currentText()] >= self.x1) & (self.data[self.x_axis_combo.currentText()] <= self.x2) & 
                                            (self.data[self.y_axis_combo.currentText()] >= self.y1) & (self.data[self.y_axis_combo.currentText()] <= self.y2)),'Name'] = name
                tmp_data.loc[self.data.index,'Name'] = self.data['Name']
                tmp_data.to_csv(self.csv_name, index=False)
            self.plot_type_check()
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
        if self.name_sep_btn.isChecked():
            self.mode_btn.setEnabled(False)
            self.gating_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

            self.fig.clear()
            #self.data = pd.read_csv(self.csv_name)
            tmp_data = pd.read_csv(self.csv_name)
            unique_names = tmp_data['Name'].unique()
            x_column = self.x_axis_combo.currentText()
            y_column = self.y_axis_combo.currentText()
            x_data = tmp_data[x_column]
            y_data = tmp_data[y_column]
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.set_xlabel(x_column)
            self.ax.set_ylabel(y_column)
            self.ax.set_title(f' {x_column} : {y_column}')
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            legend_color_map = [to_hex(cmap(i)) for i in range(len(unique_names))]  # 색상을 RGB로 변환

            for i, name in enumerate(unique_names):
                mask = (tmp_data['Name'] == name)
                self.ax.scatter(x_data[mask], y_data[mask], label=name, color=name_color_map(i),alpha=0.5)
                item_widget = QListWidgetItem()
                item_widget.setText(str(name))  # 항목의 텍스트 설정
                item_widget.setBackground(QtGui.QColor(legend_color_map[i]))  # 항목의 배경색을 색상으로 설정
                self.plot_legend.addItem(item_widget)
            self.ax.set_xlim(min(x_data),max(x_data))
            self.ax.set_ylim(min(y_data),max(y_data))
    
            self.rs.extents = (0, 0, 0, 0)
            self.canvas.draw()
        else:
            self.mode_btn.setEnabled(True)
            self.gating_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.plot_manual_change()
        
    def change_color(self):
        self.fig.clear()
        selected_items = self.plot_legend.selectedItems()
        selected_list = [item.text() for item in selected_items]
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        self.ax = self.fig.add_subplot(1, 1, 1)

        if self.x_data.dtype == 'object':
            count = self.x_data.value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            for i in range(len(values)):
                if len(selected_list) == 0:
                    self.ax.bar(names[i], values[i],color = name_color_map(i))
                elif names[i] in selected_list:
                    self.ax.bar(names[i], values[i],color = name_color_map(i), label = names[i])
                else:
                    self.ax.bar(names[i], values[i],color = 'lightgray')
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_xlabel(self.x_axis_combo.currentText())
            self.ax.set_ylabel('Count')
            self.ax.set_title('Bar plot')

        elif self.y_data.dtype == 'object':
            count = self.y_data.value_counts()
            values = count.values
            names = count.index
            cmap = plt.cm.get_cmap('tab20', len(values))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(values))))
            for i in range(len(values)):
                if len(selected_list) == 0:
                    self.ax.barh(names[i], values[i],color = name_color_map(i))
                elif names[i] in selected_list:
                    self.ax.barh(names[i], values[i],color = name_color_map(i),label = names[i])
                else:
                    self.ax.barh(names[i], values[i],color = 'lightgray')
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_ylabel(self.y_axis_combo.currentText())
            self.ax.set_xlabel('Count')
            self.ax.set_title('Bar plot')

        elif self.name_sep_btn.isChecked():
            tmp_data = pd.read_csv(self.csv_name)
            unique_names = tmp_data['Name'].unique()
            x_data = tmp_data[x_column]
            y_data = tmp_data[y_column]
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            for i, name in enumerate(unique_names):
                mask = tmp_data['Name'] == name # 'Name 버전'
                if len(selected_list) == 0:
                    self.ax.scatter(x_data[mask], y_data[mask], color=name_color_map(i),alpha=0.5)
                elif name in selected_list:
                    self.ax.scatter(x_data[mask], y_data[mask], label=name, color=name_color_map(i))
                else:
                    self.ax.scatter(x_data[mask], y_data[mask], color='lightgray',alpha=0.1)
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels)
            self.ax.set_xlim(min(x_data),max(x_data))
            self.ax.set_ylim(min(y_data),max(y_data))
            self.ax.set_xlabel(x_column)
            self.ax.set_ylabel(y_column)
            self.ax.set_title(f' {x_column} : {y_column}')

        else:
            z_column = self.z_axis_combo.currentText() #zcolumn 버전
            self.z_data = self.data[z_column] #zcolumn 버전
            unique_names = self.z_data.unique() #zcolumn 버전
            cmap = plt.cm.get_cmap('tab20', len(unique_names))  # tab20 colormap을 사용하거나 다른 colormap을 선택할 수 있음
            name_color_map = ListedColormap(cmap(range(len(unique_names))))
            for i, name in enumerate(unique_names):
                mask = (self.data[z_column] == name) #zcolumn 버전
                if len(selected_list) == 0:
                    self.ax.scatter(self.x_data[mask], self.y_data[mask], color=name_color_map(i),alpha=0.5)
                elif name in selected_list:
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
        
        self.canvas.draw()
