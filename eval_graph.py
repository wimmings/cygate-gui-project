import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from PySide6.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.gridspec as gridspec

class EvalGraph(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.groundtruth = None  # Ground Truth
        self.predict = None  # Predicted values
        
        self.initUI()
        
    def initUI(self):
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        final_layout = QVBoxLayout(self)
        H_layout = QHBoxLayout()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # X-axis combo box
        groundtruth_label = QLabel("Ground Truth:")
        H_layout.addWidget(groundtruth_label)
        self.groundtruth_combo = QComboBox()
        self.groundtruth_combo.setFixedWidth(100)
        H_layout.addWidget(self.groundtruth_combo)

        spacer_label = QLabel("")
        H_layout.addWidget(spacer_label)
        
        # Y-axis combo box
        predict_label = QLabel("Prediction:")
        H_layout.addWidget(predict_label)
        self.predict_combo = QComboBox()
        self.predict_combo.setFixedWidth(100)
        H_layout.addWidget(self.predict_combo)

        spacer_label = QLabel("")
        H_layout.addWidget(spacer_label)

        valid_columns = self.data.select_dtypes(include=['object', 'int']).columns

        for col in valid_columns:
            self.groundtruth_combo.addItem(col)
            self.predict_combo.addItem(col)
        self.groundtruth_combo.currentIndexChanged.connect(self.plot_change)
        self.predict_combo.currentIndexChanged.connect(self.plot_change)

        self.plot_change()

        # layout.addLayout() 필요한 평가지표를 추가할 때 사용
        
        final_layout.addLayout(H_layout)
        final_layout.addLayout(layout,3.5)
        
    
    def plot_change(self):
        self.fig.clear()

        # 현재 선택된 Ground Truth 및 Prediction 컬럼 가져오기
        groundtruth_col = self.groundtruth_combo.currentText()
        predict_col = self.predict_combo.currentText()
        
        # Ground Truth와 Prediction 값 추출
        self.groundtruth = self.data[groundtruth_col].values
        self.predict = self.data[predict_col].values
        
        # 평가지표 계산 (weighted 포함)
        accuracy = accuracy_score(self.groundtruth, self.predict)
        precision = precision_score(self.groundtruth, self.predict, average='macro')
        recall = recall_score(self.groundtruth, self.predict, average='macro')
        f1 = f1_score(self.groundtruth, self.predict, average='macro')

        # GridSpec 사용하여 레이아웃 설정
        gs = gridspec.GridSpec(5, 2, height_ratios=[1, 1, 0.2, 1, 2])  # 빈 행 추가, 마지막 행 더 크게

        # 첫 번째 subplot: Accuracy 출력 (weight 미적용)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax1.text(0.5, 0.5, f'Accuracy: {accuracy:.3%}\n'
                            f'Precision: {precision:.3%}\n'
                            f'Recall: {recall:.3%}\n'
                            f'F1 Score: {f1:.3%}', ha='center', va='center', fontsize=12)
        ax1.axis('off')  # 축 숨기기

        # 두 번째 subplot: Evaluation Metrics (weight 미적용)
        ax2 = self.fig.add_subplot(gs[0, 1])
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
        values = [accuracy, precision, recall, f1]
        ax2.bar(metrics, values, color=['blue', 'orange', 'green', 'red'])
        ax2.set_ylim(0, 1)  # Y축 범위 설정
        ax2.set_ylabel('Score')
        ax2.set_title('Evaluation Metrics', fontsize=12)

        # 두 번째 행 - Weight 고려한 평가지표
        accuracy_weighted = accuracy  # Accuracy는 같음
        precision_weighted = precision_score(self.groundtruth, self.predict, average='weighted')
        recall_weighted = recall_score(self.groundtruth, self.predict, average='weighted')
        f1_weighted = f1_score(self.groundtruth, self.predict, average='weighted')

        # 세 번째 subplot: Accuracy 출력 (weight 적용)
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax3.text(0.5, 0.5, f'Accuracy: {accuracy_weighted:.3%}\n'
                            f'Precision: {precision_weighted:.3%}\n'
                            f'Recall: {recall_weighted:.3%}\n'
                            f'F1 Score: {f1_weighted:.3%}', ha='center', va='center', fontsize=12)
        ax3.axis('off')  # 축 숨기기

        # 네 번째 subplot: Evaluation Metrics (weight 적용)
        ax4 = self.fig.add_subplot(gs[1, 1])
        metrics_weighted = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
        values_weighted = [accuracy_weighted, precision_weighted, recall_weighted, f1_weighted]
        ax4.bar(metrics_weighted, values_weighted, color=['blue', 'orange', 'green', 'red'])
        ax4.set_ylim(0, 1)  # Y축 범위 설정
        ax4.set_ylabel('Score')
        ax4.set_title('Evaluation Metrics (Weighted)', fontsize=12)

        # 빈 행 추가 (세 번째 행은 공백으로 남김)
        ax_blank = self.fig.add_subplot(gs[2, :])
        ax_blank.axis('off')

        # 네 번째 행: 혼동 행렬 그리기
        cm = confusion_matrix(self.groundtruth, self.predict)
        ax5 = self.fig.add_subplot(gs[3:, :])  # 마지막 2행을 혼동 행렬에 할당
        cax = ax5.matshow(cm, cmap='Blues')
        
        # 혼동 행렬 레이블 설정
        for (i, j), value in np.ndenumerate(cm):
            ax5.text(j, i, int(value), ha='center', va='center', color='white' if cm[i, j] > cm.max() / 2 else 'black')

        ax5.set_xlabel('Predicted')
        ax5.set_ylabel('True')
        ax5.set_title('Confusion Matrix', fontsize=12)

        # 그래프 크기 조정
        plt.tight_layout()  # 레이아웃 자동 조정
        self.canvas.draw()