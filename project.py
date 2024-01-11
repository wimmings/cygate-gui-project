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

from manual_graph import ManualGraph
import subprocess

class MainView(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        global UI_set
        # 생성한 UI 파일 모두 담고 있는 객체
        UI_set = QtUiTools.QUiLoader().load(resource_path("/Users/hyunjoon/Desktop/vscode/Project/new_start/cygate.ui"))
        
        # Training Samples 선택
        UI_set.pushButton_TSopen.clicked.connect(self.select_train)
        
        # Training Parameter 지정

        # Test Samples 선택
        UI_set.pushButton_DSopen.clicked.connect(self.select_test)
        
        self.graph_widget = UI_set.findChild(QTabWidget, "graph")
        # cygate 실행
        UI_set.pushButton_Run.clicked.connect(self.run)

        # manual gate
        UI_set.manual_load_btn.clicked.connect(self.load_data)
        UI_set.manual_remove_btn.clicked.connect(self.remove_list)
        UI_set.manual_clear_btn.clicked.connect(self.clear_list)
        UI_set.manual_run_btn.clicked.connect(self.manual_run)
        UI_set.manual_graph_tab.tabCloseRequested.connect(self.close_tab)

        self.paths = []
        
        self.setCentralWidget(UI_set)
        self.setWindowTitle("UI TEST")
        self.resize(1000,800)
        self.show()
    def select_train(self):
        global configFile
        # config file 만들기
        configFile = open("fooo2.txt", "w+")
        
        # 파일 가져오기
        training_files = QFileDialog.getOpenFileNames(self, self.tr("Open Data files"), "./", self.tr("Data Files (*.csv *.xls *.xlsx)"))
        
        # fooo.txt에 path 쓰기
        for file in training_files[0]:
            configFile.write("Training.Sample= "+file+'\n')
            exist = UI_set.textEdit_TS.toPlainText()
            UI_set.textEdit_TS.setText(exist+file+'\n')
        
    
    def training_param(self):
        param = UI_set.textEdit_TUC.toPlainText()
        
        # foo.txt에 적기
        configFile.write("Training.UngatedCellLabel= "+param+'\n')
                
        
    def select_test(self):
        # 파일 가져오기
        test_files = QFileDialog.getOpenFileNames(self, self.tr("Open Data files"), "./", self.tr("Data Files (*.csv *.xls *.xlsx)"))
        
        # foo.txt에 파일 이름 적기
        for file in test_files[0]:
            configFile.write("Data.Sample= "+file+'\n')
            exist = UI_set.textEdit_DS.toPlainText()
            UI_set.textEdit_DS.setText(exist+file+'\n')
            

    def tsne(self):        
        matching_files = find_files('_cygated')
        print(matching_files)
        
        for path in matching_files:
            data = pd.read_csv(path)

            # 열 삭제
            columns_to_delete = ['Label', 'Name']
            data = data.drop(columns=columns_to_delete, axis=1)

            pca = PCA(0.95)
            X_pca = pca.fit_transform(data)

            # # 2차원 t-SNE 임베딩

            # # 축소한 차원의 수
            n_components = 2

            # # 모델 만들기
            model = TSNE(n_components = n_components, random_state=42)

            # # TSNE 훈련
            tsne_result = model.fit_transform(X_pca[:10000])

            # # # DataFrame으로 변환
            tsne_df = pd.DataFrame(data=tsne_result, columns = ['tsne1', 'tsne2'])

            # # # 그래프를 시각화
            color_map = {0: 'pink', 1: 'purple', 2: 'yellow', 3:'green', 4:'red', 5:'orange', 6:'blue', 7:'pink', 8:'cyan', 9:'khaki', 10:'gold', 11:'olive', 12:'teal', 13:'deepskyblue', 14:'skyblue', 15:'coral'}  # Add more colors if you have additional classes
            tsne_df['Gated'] = data['Gated']

            # 그래프를 FigureCanvas에 통합
            self.fig, ax = plt.subplots()
            canvas = FigureCanvas(self.fig)
            canvas.setParent(self.graph_widget)

            # Scatter plot with colors
            for target_value, color in color_map.items():
                subset_df = tsne_df[tsne_df['Gated'] == target_value]
                plt.scatter(subset_df['tsne1'], subset_df['tsne2'], marker='o', alpha=0.5, label=f'Class {target_value}', color=color)


            ax.set_title('t-SNE')
            ax.set_xlabel('t-SNE 1')
            ax.set_ylabel('t-SNE 2')
            ax.legend()
            ax.grid(True)
            print("finish!")
            
            # tab 지정
            file_name = os.path.basename(path).split('.')[0]            
            tab_idx = self.graph_widget.addTab(QWidget(), file_name)
            
            layout = QVBoxLayout(self.graph_widget.widget(tab_idx))
            layout.addWidget(canvas)
        

    def run(self):
        # param 가져오기
        self.training_param()
        
        configFile.close()
        
        # 실행
        jar_name = "CyGate_v1.02.jar"
        
        # 최종 실행 명령어
        # os.system("java -jar " + jar_name + " --c " + "fooo2.txt")
        result = subprocess.run(["java", "-jar", jar_name, "--c", "fooo2.txt"])
        
        if result.returncode == 0:
            self.tsne()
        else:
            print("외부 프로세스 완료 이전")


    def remove_list(self): # manual list 항목 제거
        selected_item = UI_set.manual_list.currentItem()
        if selected_item:
            row = UI_set.manual_list.row(selected_item)
            UI_set.manual_list.takeItem(row)
            del self.paths[row]

    def clear_list(self):  # manual list 클리어
        UI_set.manual_list.clear()

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
            tab_instance = self.sender()
            tab_instance.removeTab(index)
    
    def manual_run(self):
        data_path = self.paths[UI_set.manual_list.currentRow()] + "/" + UI_set.manual_list.currentItem().text()
        data_name = UI_set.manual_list.currentItem().text()
        data = pd.read_csv(data_path)
        
        tab_instance = QTabWidget()
        tab_instance.setDocumentMode(True)
        tab_instance.setTabsClosable(True)
        tab_instance.tabCloseRequested.connect(self.close_tab)

        manual_graph_instance = ManualGraph(data)

        tab_instance.addTab(manual_graph_instance, "Original")
        UI_set.manual_graph_tab.addTab(tab_instance, data_name)

        

# 파일 경로 찾기
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 문자열 포함하는 파일 찾기
def find_files(target_string):
    matching_files = []
    for root, dirs, files in os.walk('/Users/ohsuyoung/hyu/gui/Samusik/'):
        for file in files:
            if target_string in file:
                matching_files.append(os.path.join(root, file))
    return matching_files

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainView()
    sys.exit(app.exec())
 