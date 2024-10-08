import sys
import os
import re
import csv
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from PySide6 import QtUiTools
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QTabWidget, QProgressDialog, QMessageBox, QCheckBox, QHBoxLayout, QGridLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #plot gui 내에 띄우기
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import QApplication, QMainWindow

from matplotlib import colormaps as cmaps

from manual_graph import ManualGraph
from cygate_thread import CygateThread
from train_tsne_thread import TrainTSNEThread
from test_tsne_thread import TestTSNEThread
from eval_graph import EvalGraph

class MainView(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        global UI_set
        # 생성한 UI 파일 모두 담고 있는 객체
        UI_set = QtUiTools.QUiLoader().load(resource_path("cygate.ui"))
        
        # Training Samples 선택
        UI_set.cygate_train_load.clicked.connect(self.select_train_candidate)
        UI_set.cygate_train_all.clicked.connect(self.select_train_all)
        UI_set.cygate_train_rm.clicked.connect(self.remove_train)
        UI_set.cygate_train_clear.clicked.connect(self.clear_train)
        UI_set.train_graph.tabCloseRequested.connect(self.close_tab)

        # Test Samples 선택
        UI_set.cygate_test_load.clicked.connect(self.select_test_candidate)
        UI_set.cygate_test_all.clicked.connect(self.select_test_all)
        UI_set.cygate_test_rm.clicked.connect(self.remove_test)
        UI_set.cygate_test_clear.clicked.connect(self.remove_test)
        UI_set.graph.tabCloseRequested.connect(self.close_tab)
        
        self.test_tsne_graph = UI_set.findChild(QTabWidget, "graph")
        self.train_tsne_graph = UI_set.findChild(QTabWidget, "train_graph")
        self.test_candidate = []
        self.train_candidate = []
        # cygate 실행
        UI_set.cygate_run.clicked.connect(self.run_cygate)        
        MainView.tab_data = {
            'bars' : [],
            'cell_mappings': [],
            'checkboxes' : [],
            'cids' : [],
            'colors': [],
            'color_maps': [],
            'figs': [],
            'name_counts': []
        }
        MainView.train_tab_data = {
            'bars': [],
            'cell_mappings': [],
            'cids' : [],
            'colors': [],
            'color_maps': [],
            'figs': [],
            'name_counts': [],
            'tsne_dfs': []
        }
        # manual gate
        UI_set.manual_load_btn.clicked.connect(self.load_data)
        UI_set.manual_remove_btn.clicked.connect(self.remove_list)
        UI_set.manual_clear_btn.clicked.connect(self.clear_list)
        UI_set.manual_run_btn.clicked.connect(self.manual_run)
        UI_set.manual_graph_tab.tabCloseRequested.connect(self.close_tab)

        # Evaluation
        UI_set.eval_load_btn.clicked.connect(self.eval_load_data)
        UI_set.eval_remove_btn.clicked.connect(self.eval_remove_list)
        UI_set.eval_clear_btn.clicked.connect(self.eval_clear_list)
        UI_set.eval_run_btn.clicked.connect(self.eval_run)
        UI_set.eval_graph_tab.tabCloseRequested.connect(self.close_tab)

        self.paths = []
        
        self.setCentralWidget(UI_set)
        self.setWindowTitle("UI TEST")
        self.show()
    
    def train_tsne(self, train):
        progress = QProgressDialog("Running TRAIN Data t-SNE.. \n", None, 0, 0, self)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 최소 시간 지정 (0으로 설정하면 즉시 표시)

        # 기존 스레드가 존재하면 기다린 후 종료set value 0 finish
        if not hasattr(self, 'train_tsne_thread') or not self.train_tsne_thread.isRunning():
            self.train_tsne_thread = TrainTSNEThread(train)
            
            self.train_tsne_thread.update_text.connect(lambda text: progress.setLabelText("Running TRAIN Data t-SNE.. \n[" + text + "]"))
            
            # update_ui signal 발생시 draw 함수 호출
            self.train_tsne_thread.update_ui.connect(self.train_draw)
            self.train_tsne_thread.update_ui.connect(lambda df, file, i: progress.setValue(i))
            
            
            self.train_tsne_thread.finished.connect(progress.close)
            self.train_tsne_thread.finished.connect(self.train_tsne_thread.quit)
            
            # 쓰레드 시작
            self.train_tsne_thread.start()
            
        # else:
        #     print("train tsne thread already running")
        
        
    def save_image(self, figure, file_path, dpi=300):
        figure.savefig(file_path, dpi=dpi)
        
    @Slot(pd.DataFrame, str)
    def train_draw(self, tsne_df, file_name) :
        # 'Name' 열에 따라 색상을 자동으로 생성
        unique_names = sorted(tsne_df['Name'].astype(str).unique())
        color_map = {name: cmaps.get_cmap('gist_rainbow')(i / len(unique_names)) for i, name in enumerate(unique_names)}
        
        fig, (ax_tsne, ax_hist) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [2.5, 1]})
        
        
        
        cell_mapping = {}
        for name, color in color_map.items():
            subset_df = tsne_df.loc[tsne_df['Name'] == name]
            scatter = ax_tsne.scatter(subset_df['tsne1'], subset_df['tsne2'], marker='o', alpha=0.5, label=name, color=color, s=3)
            cell_mapping[name] = scatter
        
        ax_tsne.set_title('t-SNE', fontsize=8)
        ax_tsne.grid(True)    
        
        # 범례 조정
        # legend_elements = [Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=color, markersize=8) for name, color in color_map.items()]
        # ax_tsne.legend(handles=legend_elements, loc='upper right', prop={'size': 6}, bbox_to_anchor=(1.28, 1))
        
        # Create histogram
        name_counts = tsne_df['Name'].value_counts().sort_index()
        log_counts = np.log10(name_counts+1)  # 자연 로그 변환 
        colors = [color_map[name] for name in name_counts.index]
        bars = ax_hist.bar(np.arange(len(name_counts)), log_counts, color=colors, alpha=0.7)


        ax_hist.set_title('Cell Counts', fontsize=8)
        ax_hist.set_xticks(np.arange(len(name_counts)))  # x 축 눈금 위치 설정
        ax_hist.set_xticklabels(name_counts.index, rotation=90)  # x 축 눈금 레이블 설정

        ax_hist.xaxis.set_tick_params(which='both', labelbottom=True, labeltop=True)
        ax_hist.xaxis.set_tick_params(labelbottom=True, labeltop=False)
        ax_hist.tick_params(axis='x', rotation=90)

        for i, count in enumerate(name_counts):
            log_count = log_counts[i]
            ax_hist.text(i, log_count + 0.05, f'{count}', ha='center', va='bottom', fontsize=6)


        # Set x-axis tick labels font size
        ax_hist.tick_params(axis='x', labelsize=6)
        ax_hist.set_ylim(0, 1.2 * log_counts.max())

        canvas = FigureCanvas(fig)
        canvas.setParent(self.train_tsne_graph)
        toolbar = NavigationToolbar(canvas)
        toolbar.setFixedHeight(30)
        
        tab_widget = QTabWidget()
        tab_widget.tabCloseRequested.connect(self.close_tab)

        tab_idx = self.train_tsne_graph.addTab(tab_widget, file_name)
        
        layout = QVBoxLayout(self.train_tsne_graph.widget(tab_idx))
        
        legend_select_layout = QHBoxLayout()
        legend_select = QCheckBox('Select All')
        legend_select.setChecked(True)
        legend_select.stateChanged.connect(self.update_legend_all_train)
        legend_select_layout.addWidget(legend_select)
        layout.addLayout(legend_select_layout)
        
        layout.addWidget(canvas)
        layout.addWidget(toolbar)

        cid = ax_hist.figure.canvas.mpl_connect('button_press_event', self.on_bar_click_train)          
        self.train_tab_data[tab_idx] = {
            'bars': bars,
            'cell_mappings': cell_mapping,
            'cids' : cid,
            'colors': colors,
            'color_maps': color_map,
            'figs' : fig,
            'name_counts': name_counts,
            'tsne_dfs': tsne_df,
        }

        plt.subplots_adjust(hspace=0.7, bottom=0.2)

        # self.save_image(ax_tsne.get_figure(), tsne_image_path)
    
    def test_tsne(self, test):
        progress = QProgressDialog("Running TEST Data t-SNE.. \n", None, 0, 0, self)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 최소 시간 지정 (0으로 설정하면 즉시 표시)

        # 기존 스레드가 존재하면 기다린 후 종료
        if not hasattr(self, 'test_tsne_thread') or not self.test_tsne_thread.isRunning():
            self.test_tsne_thread = TestTSNEThread(test)
            self.test_tsne_thread.update_ui.connect(self.test_draw)
            self.test_tsne_thread.finished.connect(progress.close)
            self.test_tsne_thread.start()
            
        # else:
        #     print("ttttttttttttttest tsne thread already running")
        
        
    @Slot(pd.DataFrame, str)
    def test_draw(self, tsne_df, file_name) :
        # 'Name' 열에 따라 색상을 자동으로 생성
        unique_names = sorted(tsne_df['Name'].astype(str).unique())
        # print(unique_names)
        color_map = {name: cmaps.get_cmap('gist_rainbow')(i / len(unique_names)) for i, name in enumerate(unique_names)}
        # print(color_map)
        fig, (ax_tsne, ax_hist) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [2.5, 1]})

        
        cell_mapping = {}
        grouped_df = tsne_df.groupby(['Name', 'File'])
        for (cell_name, file_number), group in grouped_df:
            # 해당 그룹의 모든 점을 하나의 scatter로 만들어줍니다.
            scatter = ax_tsne.scatter(group['tsne1'], group['tsne2'], marker='o', alpha=0.5, label=cell_name, color=color_map[cell_name], s=3)
            # cell_mapping에 추가합니다.
            cell_mapping[(cell_name, file_number)] = scatter
        # print(cell_mapping)
        ax_tsne.set_title('t-SNE', fontsize=8)
        ax_tsne.grid(True)
       
        # cell count 막대 그래프
        name_counts = tsne_df['Name'].value_counts().sort_index()
        log_counts = np.log10(name_counts+1)  # 자연 로그 변환 
        colors = [color_map[name] for name in name_counts.index]
        # 막대 바
        bars = ax_hist.bar(np.arange(len(name_counts)), log_counts, color=colors, alpha=0.7)

        ax_hist.set_title('Cell Counts', fontsize=8)
        ax_hist.set_xticks(np.arange(len(name_counts)))  # x 축 눈금 위치 설정
        ax_hist.set_xticklabels(name_counts.index, rotation=90)  # x 축 눈금 레이블 설정
        
        ax_hist.xaxis.set_tick_params(which='both', labelbottom=True, labeltop=True)
        ax_hist.xaxis.set_tick_params(labelbottom=True, labeltop=False)
        ax_hist.tick_params(axis='x', rotation=90)

        for i, count in enumerate(name_counts):
            log_count = log_counts[i]
            ax_hist.text(i, log_count + 0.05, f'{count}', ha='center', va='bottom', fontsize=6)


        # Set x-axis tick labels font size
        ax_hist.tick_params(axis='x', labelsize=6)
        ax_hist.set_ylim(0, 1.2 * log_counts.max())
        
        canvas = FigureCanvas(fig)
        canvas.setParent(self.test_tsne_graph)
        toolbar = NavigationToolbar(canvas)
        toolbar.setFixedHeight(30)
        
        tab_widget = QTabWidget()
        tab_widget.tabCloseRequested.connect(self.close_tab)

        tab_idx = self.test_tsne_graph.addTab(tab_widget, file_name)
        
        layout = QVBoxLayout(self.test_tsne_graph.widget(tab_idx))
        # 체크박스 생성 및 레이아웃 추가
        # 파일별로 cell 나누기        
        unique_files = tsne_df['File'].unique()
        checkbox_layout = QHBoxLayout()
        checkboxes = {}
        for file_number in unique_files:
            checkbox = QCheckBox(f"File {file_number}")
            checkbox.setChecked(True)  # 초기에 모든 체크박스를 선택 상태로 설정
            checkbox.stateChanged.connect(lambda state, file_number=file_number: self.update_file_color(state, file_number))
            checkbox_layout.addWidget(checkbox)
            checkboxes[file_number] = checkbox
            
        layout.addLayout(checkbox_layout)
        
        
        # 전체 파일, legend를 체크하고 해제하는 거
        legend_select_layout = QHBoxLayout()
        legend_select = QCheckBox('Select All')
        legend_select.setChecked(True)
        legend_select.stateChanged.connect(self.update_legend_all_test)
        legend_select_layout.addWidget(legend_select)
        layout.addLayout(legend_select_layout)
        
        layout.addWidget(canvas) # 체크박스 -> 그래프 순서?
        layout.addWidget(toolbar)
        
        # 현재 탭 데이터 저장
        cid = ax_hist.figure.canvas.mpl_connect('button_press_event', self.on_bar_click_test)          
        self.tab_data[tab_idx] = {
            'bars' : bars,
            'cell_mappings': cell_mapping,
            'checkboxes' : checkboxes,
            'cids' : cid,
            'colors' : colors,
            'color_maps': color_map,
            'figs' : fig,
            'name_counts': name_counts
        }


        # 서브플롯 간의 간격 및 밑에 여백 조정
        plt.subplots_adjust(hspace=0.6)
    
    def update_legend_all_train(self, state):
        current_tab_index = self.train_tsne_graph.currentIndex()
        current_tab_data = self.train_tab_data.get(current_tab_index)
        
        if current_tab_data:            
            bars = current_tab_data['bars']
            cell_mapping = current_tab_data['cell_mappings']
            colors = current_tab_data['colors']
            color_map = current_tab_data['color_maps']
            fig = current_tab_data['figs']
            name_counts = current_tab_data['name_counts']
            
            for name, scatter in cell_mapping.items():
                # scatter 색상 설정
                new_color = (0.8, 0.8, 0.8, 0.02) if state == 0 else color_map[name]
                scatter.set_facecolor(new_color)
                scatter.set_edgecolor(new_color)
                

                # 해당 이름의 bar 색상 설정
                for i, bar in enumerate(bars):
                    if name_counts.index[i] == name:
                        bar.set_facecolor(new_color)
                        colors[i] = new_color
                        
            fig.canvas.draw_idle()  # 그래프 업데이트
    
    def update_legend_all_test(self, state):
        current_tab_index = self.test_tsne_graph.currentIndex()
        current_tab_data = self.tab_data.get(current_tab_index)
        checked = self.get_checked_file_numbers(current_tab_index)
        
        if current_tab_data:            
            bars = current_tab_data['bars']
            cell_mapping = current_tab_data['cell_mappings']
            colors = current_tab_data['colors']
            color_map = current_tab_data['color_maps']
            fig = current_tab_data['figs']
            name_counts = current_tab_data['name_counts']
            for (cell_name, f_number), scatter in cell_mapping.items():
                if f_number in checked:
                    new_color = (0.8, 0.8, 0.8, 0.02) if state == 0 else color_map[cell_name]
                    scatter.set_facecolor(new_color)
                    scatter.set_edgecolor(new_color)

                    # 해당 이름의 bar 색상 설정
                    for i, bar in enumerate(bars):
                        if name_counts.index[i] == cell_name:
                            bar.set_facecolor(new_color)
                            colors[i] = new_color
    
                    fig.canvas.draw_idle()  # 그래프 업데이트



    def update_file_color(self, state, file_number):
        current_tab_index = self.test_tsne_graph.currentIndex()
        current_tab_data = self.tab_data.get(current_tab_index)
        
        if current_tab_data:
            bars = current_tab_data['bars']
            cell_mapping = current_tab_data['cell_mappings']
            colors = current_tab_data['colors']
            color_map = current_tab_data['color_maps']
            fig = current_tab_data['figs']
            name_counts = current_tab_data['name_counts']

            # 파일 번호에 해당하는 셀들만 처리
            for (cell_name, f_number), scatter in cell_mapping.items():
                if f_number == file_number:
                    if state == 0:
                        scatter.set_facecolor((0.8,0.8,0.8,0.02))
                        scatter.set_edgecolor((0.8,0.8,0.8,0.02))
                    else:
                        scatter.set_facecolor(color_map[cell_name])
                        scatter.set_edgecolor(color_map[cell_name])
                        # 각 cell_name에 해당하는 bar 색상도 업데이트
                        for i, bar in enumerate(bars):
                            if colors[i] == (0.8,0.8,0.8,0.02) and name_counts.index[i] == cell_name:
                                bar.set_facecolor(color_map[cell_name])
                                colors[i] = color_map[cell_name]

                    fig.canvas.draw_idle()


    def on_bar_click_train(self, event):
        current_tab_index = self.train_tsne_graph.currentIndex()
        current_tab_data = self.train_tab_data.get(current_tab_index)
        if current_tab_data:
            bars = current_tab_data['bars']
            cell_mapping = current_tab_data['cell_mappings']
            colors = current_tab_data['colors']
            color_map = current_tab_data['color_maps']
            fig = current_tab_data['figs']
            name_counts = current_tab_data['name_counts']
            if event.inaxes:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        cell_name = name_counts.index[i]
                        if colors[i] == color_map[cell_name]:
                            colors[i] = (0.8,0.8,0.8,0.02)
                        else:
                            colors[i] = color_map[cell_name]
                        bar.set_facecolor(colors[i])

                        cell_mapping[cell_name].set_facecolor(colors[i])
                        cell_mapping[cell_name].set_edgecolor(colors[i])
                        fig.canvas.draw_idle()
                        break

    def on_bar_click_test(self, event):
        current_tab_index = self.test_tsne_graph.currentIndex()
        current_tab_data = self.tab_data.get(current_tab_index)
        checked = self.get_checked_file_numbers(current_tab_index)

        if current_tab_data:
            bars = current_tab_data['bars']
            cell_mapping = current_tab_data['cell_mappings']
            colors = current_tab_data['colors']
            color_map = current_tab_data['color_maps']
            fig = current_tab_data['figs']
            name_counts = current_tab_data['name_counts']
            if event.inaxes:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        cell_name = name_counts.index[i]
                        
                        if colors[i] == color_map[cell_name]: # 클릭한 막대 찾음 - 색이 있으면
                            new_color = (0.8,0.8,0.8,0.02)
                        else:                                # 회색이면
                            new_color = color_map[cell_name] # 색상 변경. 원래<->회색
                     
                        colors[i] = new_color
                        bar.set_facecolor(new_color)
                        
                        for (c_name, f_number), scatter in cell_mapping.items():
                            if f_number in checked and c_name == cell_name:  
                                scatter.set_facecolor(new_color)
                                scatter.set_edgecolor(new_color)                  
    
                        fig.canvas.draw_idle()
                        break
                                                   
    
    def get_checked_file_numbers(self, index):
        current_tab_index = self.test_tsne_graph.currentIndex()
        current_tab_data = self.tab_data.get(current_tab_index)        
        if current_tab_data:
            checkboxes = current_tab_data['checkboxes']
        # 체크된 파일 번호 가져오기
        checked_file_numbers = []
        for file_number, checkbox in checkboxes.items():
            if checkbox.isChecked():
                checked_file_numbers.append(file_number)
        return checked_file_numbers

    def run_cygate(self):
        # 체크된 train files 가져오기
        train = self.get_checked_train_files(self.train_candidate)
        test = self.get_checked_test_files(self.test_candidate)
        
        config_file = open("cygate.txt", "w+")
        for file_path in train:
            config_file.write("Training.Sample= "+file_path+'\n')
        
        # param 가져오기
        param = UI_set.cygate_uncell.toPlainText()
        config_file.write("Training.UngatedCellLabel= "+param+'\n')

        # 체크된 test files 가져오기
        for file_path in test:
            config_file.write("Data.Sample= "+file_path+'\n')    
        
        config_file.close()
        
        # 쓰레드 인스턴스 생성
        self.cygate_thread = CygateThread()
        
        # 로딩창 생성
        progress = QProgressDialog("Running Cygate..", None, 0, 0, self)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 최소 시간 지정 (0으로 설정하면 즉시 표시)
            
        # 쓰레드가 완료되면 tsne 수행
        self.cygate_thread.finished.connect(progress.close)  # 로딩창 닫기
        # self.cygate_thread.finished.connect(self.cygate_thread.quit)  # 쓰레드 종료
        
        self.cygate_thread.finished.connect(lambda: self.run_tsne(train, test))  # train 및 test 전달

        # 쓰레드 시작
        self.cygate_thread.start()
    
    def run_tsne(self, train, test):
        # 기존 train_tsne_thread가 존재하면 기다린 후 종료
        if not hasattr(self, 'train_tsne_thread') or not self.train_tsne_thread.isRunning():
            self.train_tsne(train)
            print("train _ tsne start")
        # else:
        #     print("train tsne thread already running")
            
        # 기존 test_tsne_thread가 존재하면 기다린 후 종료
        if not hasattr(self, 'test_tsne_thread') or not self.test_tsne_thread.isRunning():
            self.test_tsne(test)
            print("test _ tsne start")
        # else:
        #     print("ttttttttttttttest tsne thread already running")
        

    def extract_columns(self, file):
        column_names = []
        with open(file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            column_names = next(reader)
        return column_names
            
    
    def select_train_candidate(self):
        # 파일 가져오기
        selected_files, _ = QFileDialog.getOpenFileNames(self, self.tr("Open Data files"), "./", self.tr("Data Files (*.csv *.xls *.xlsx)"))
        
        # columns 만 추춣하기
        if selected_files:
            column_names = self.extract_columns(selected_files[0])
            UI_set.cygate_train_columns.clear()
            UI_set.cygate_train_columns.addItems(column_names)
        
        train_list = UI_set.cygate_train_list
        existing_files = [train_list.item(i).text() for i in range(train_list.count())]
        
        files = []
        for file in selected_files:
            file_name = extract_file_name(file)
            if file_name not in existing_files:
                self.train_candidate.append(file)   
                files.append(file_name)
        UI_set.cygate_train_list.addItems(files)
        self.set_selected_train_true(files)
        
    def select_test_candidate(self):
        # 파일 가져오기
        selected_files, _ = QFileDialog.getOpenFileNames(self, self.tr("Open Data files"), "./", self.tr("Data Files (*.csv *.xls *.xlsx)"))
        

        test_list = UI_set.cygate_test_list # 원래 리스트 객체
        existing_files = [test_list.item(i).text() for i in range(test_list.count())] # 원래 리스트 텍스트형태
        
        files = []
        for full_path in selected_files: # file은 풀패스, file name이 리스트에 보여질 
            file_name = extract_file_name(full_path)
            if file_name not in existing_files:
                self.test_candidate.append(full_path)   
                files.append(file_name)
        UI_set.cygate_test_list.addItems(files)
        self.set_selected_test_true(files)
        # 리스트를 돌면서 방금 추가한 파일이름과 같으면 select true하기
    
    def set_selected_train_true(self, files):
        train_list = UI_set.cygate_train_list
        for i in range(train_list.count()):
            if train_list.item(i).text() in files:
                UI_set.cygate_train_list.item(i).setSelected(True)
    
    def set_selected_test_true(self, files):
        test_list = UI_set.cygate_test_list
        for i in range(test_list.count()):
            if test_list.item(i).text() in files:
                UI_set.cygate_test_list.item(i).setSelected(True)
        
    def select_train_all(self):
        selected_items = UI_set.cygate_train_list.selectedItems()

        if selected_items and len(selected_items) == UI_set.cygate_train_list.count():
            # 모두 선택되어 있는 경우에만 모두 해제
            UI_set.cygate_train_list.clearSelection()
        else:
            # 그렇지 않은 경우 모두 선택
            UI_set.cygate_train_list.selectAll()
        
            
    def select_test_all(self):
        selected_items = UI_set.cygate_test_list.selectedItems()

        if selected_items and len(selected_items) == UI_set.cygate_test_list.count():
            # 모두 선택되어 있는 경우에만 모두 해제
            UI_set.cygate_test_list.clearSelection()
        else:
            # 그렇지 않은 경우 모두 선택
            UI_set.cygate_test_list.selectAll()
    
    def remove_train(self):
        selected_items = UI_set.cygate_train_list.selectedItems()

        if not selected_items:
            return

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to REMOVE the selected items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            for item in selected_items:
                row = UI_set.cygate_train_list.row(item)
                UI_set.cygate_train_list.takeItem(row)
                
            if UI_set.cygate_train_list.count() == 0:
                UI_set.cygate_train_columns.clear()
        
    def clear_train(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to CLEAR the selected items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            UI_set.cygate_train_list.clear()
            UI_set.cygate_train_columns.clear()
    
    def remove_test(self):
        selected_items = UI_set.cygate_test_list.selectedItems()
        
        if not selected_items:
            return

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to REMOVE the selected items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            for item in selected_items:
                row = UI_set.cygate_test_list.row(item)
                UI_set.cygate_test_list.takeItem(row)
            
    def clear_test(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to CLEAR the selected items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            UI_set.cygate_test_list.clear()
    
    def get_checked_train_files(self, candidate):
        # 선택된 항목만 배열에 추가
        selected_items = UI_set.cygate_train_list.selectedItems()

        checked_files = []
        for selected_item in selected_items:
            # candidate에서 해당 파일의 전체 경로를 찾아서 checked_files에 추가
            for file_path in candidate:
                if selected_item.text() in file_path:
                    checked_files.append(file_path)

        return checked_files     
        
    def get_checked_test_files(self, candidate):
        # 선택된 항목만 배열에 추가
        selected_items = UI_set.cygate_test_list.selectedItems()

        checked_files = []
        for selected_item in selected_items:
            # candidate에서 해당 파일의 전체 경로를 찾아서 checked_files에 추가
            for file_path in candidate:
                if selected_item.text() in file_path:
                    checked_files.append(file_path)

        return checked_files    
    
    def remove_list(self): # manual list 항목 제거
        selected_item = UI_set.manual_list.currentItem()
        name = selected_item.text()
        if selected_item:
            reply = QMessageBox.question(self, 'Item Remove', 'Do you really want to Remove Item?\n' + name,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                row = UI_set.manual_list.row(selected_item)
                UI_set.manual_list.takeItem(row)
                del self.paths[row]

    def clear_list(self):  # manual list 클리어
        reply = QMessageBox.question(self, 'List Clear', 'Do you really want to clear list?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            UI_set.manual_list.clear()
            self.paths = []

    def load_data(self): # manual list 항목 추가
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("CSV files (*.csv)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
        if selected_files:
            selected_files_name = []
            for i in selected_files:
                self.paths.append(os.path.dirname(i))
                selected_files_name.append(os.path.basename(i))
            UI_set.manual_list.addItems(selected_files_name)

    def close_tab(self, index):
        tab = self.sender()
        name = tab.tabText(index)
        reply = QMessageBox.question(self, 'Close Tab', 'Do you really want to close?\n' + name,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            tab.removeTab(index)
    
    def merge_data(self, items):
        items_list = [item.text() for item in items]
        cleaned_strings = [re.sub(r'\d', '', item) for item in items_list]
        if len(set(cleaned_strings)) == 1:
            combined_data = pd.DataFrame()
            data_path = self.paths[UI_set.manual_list.currentRow()] + "/"
            tooltip_list = []
            for i in items_list:
                df = pd.read_csv(data_path+i)
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                tooltip_list.append(i.split('_')[1]) # 수정 필요
            # 숫자 sort 필요
            self.tooltip = ','.join(tooltip_list)
            return combined_data
        
        self.show_error_message()
        return
    
    def manual_run(self):
        selected_items  = UI_set.manual_list.selectedItems()
        if len(selected_items) == 1:
            data_name = UI_set.manual_list.currentItem().text()
            data_path = self.paths[UI_set.manual_list.currentRow()] + "/" + data_name
            data_name = data_name.split('.')[0]
            data = pd.read_csv(data_path)
            data = self.conversion_data(data)
        else:
            data = self.merge_data(selected_items)
            data_name = UI_set.manual_list.currentItem().text().split('_')[0] + "_merge_" + self.tooltip
            data = self.conversion_data(data)
        
        tab_instance = QTabWidget()
        tab_instance.setDocumentMode(True)
        tab_instance.setTabsClosable(True)
        tab_instance.tabCloseRequested.connect(self.close_tab)
        
        csv_name = self.get_unique_filename(data_name)
        data.to_csv(csv_name,index=False)
        manual_graph_instance = ManualGraph(data, tab_instance, ["Original"], csv_name)

        instance_index = tab_instance.addTab(manual_graph_instance, "Original")
        tab_instance.setTabToolTip(instance_index,"Original")
        index = UI_set.manual_graph_tab.addTab(tab_instance, data_name)
        UI_set.manual_graph_tab.setTabToolTip(index,data_name)
        
    def show_error_message(self):
        # 오류 메시지 박스 생성
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)  # 아이콘 설정
        error_box.setWindowTitle("Error")  # 제목 설정
        error_box.setText("Error : different file name")  # 메시지 설정
        error_box.exec_()  # 메시지 박스 표시
    
    def conversion_data(self, df):
        if 'Name' not in df.columns:
            if 'Label' in df.columns:
                df['Name'] = df['Label'].apply(lambda x: f'Label_{x}')
            else:
                df['Name'] = 'NA_'
        df.loc[df['Label'] == 0, 'Name'] = 'NA_'
        
        for column in df.columns:
            # 'name' 또는 'label'이 열 이름에 포함되어 있지 않은 경우에만 값을 변경합니다.
            if 'Name' not in column and 'Label' not in column:
                df[column] = np.where(df[column] < 0, 0, df[column])
                df[column] = np.arcsinh(df[column] / 5)
        return df
    
    def get_unique_filename(self, base_filename):
        check_name = "new_" + base_filename + ".csv"
        if not os.path.exists(check_name):
            return check_name

        filename, file_extension = os.path.splitext(check_name)
        index = 1
        while True:
            new_filename = f"{filename}_{index}{file_extension}"
            if not os.path.exists(new_filename):
                return new_filename
            index += 1
    
    def eval_remove_list(self): # Eval list 항목 제거
        selected_item = UI_set.eval_list.currentItem()
        name = selected_item.text()
        if selected_item:
            reply = QMessageBox.question(self, 'Item Remove', 'Do you really want to Remove Item?\n' + name,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                row = UI_set.eval_list.row(selected_item)
                UI_set.eval_list.takeItem(row)
                del self.paths[row]

    def eval_clear_list(self):  # eval list 클리어
        reply = QMessageBox.question(self, 'List Clear', 'Do you really want to clear list?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            UI_set.eval_list.clear()
            self.paths = []

    def eval_load_data(self): # eval list 항목 추가
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("CSV files (*.csv)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
        if selected_files:
            selected_files_name = []
            for i in selected_files:
                self.paths.append(os.path.dirname(i))
                selected_files_name.append(os.path.basename(i))
            UI_set.eval_list.addItems(selected_files_name)

    def eval_run(self):
        data_name = UI_set.eval_list.currentItem().text()
        data_path = self.paths[UI_set.eval_list.currentRow()] + "/" + data_name
        data_name = data_name.split('.')[0]
        data = pd.read_csv(data_path)
        
        eval_graph_instance = EvalGraph(data)

        index = UI_set.eval_graph_tab.addTab(eval_graph_instance, data_name)
        UI_set.eval_graph_tab.setTabToolTip(index,data_name)
        
# 파일 경로 찾기
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def extract_file_name(file_path):
    return os.path.basename(file_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainView()
    sys.exit(app.exec())
 