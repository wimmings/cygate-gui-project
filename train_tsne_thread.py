from PySide6.QtCore import QThread, Signal
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os


class TrainTSNEThread(QThread):
    update_text = Signal(str)
    update_ui = Signal(pd.DataFrame, str, int)  # 시그널 추가
    finished = Signal()
    
    def __init__(self, train_data, parent=None):
        super(TrainTSNEThread, self).__init__(parent)
        self.train_data = train_data
        
    def run(self):
        for idx, path in enumerate(self.train_data, start=0):
            file_name = extract_file_name(path)
            # self.update_text.emit(file_name)
            
            data = pd.read_csv(path)
            columns_to_delete = ['Label', 'Name']
            
            for column in columns_to_delete:
                if column in data.columns:
                    data_drop = data.drop(column, axis=1)
            # data.drop(columns=columns_to_delete, axis=1)
            
            # 추가: 특정 CSV 파일이 이미 존재하는 경우 t-SNE를 실행하지 않고 파일을 사용
            csv_folder_path = 'cygate/graphs/train'  
            csv_file_path = os.path.join(csv_folder_path, 'graph_train_' + file_name)
            
            # 폴더가 없으면 새로 생성
            if not os.path.exists(csv_folder_path):
                os.makedirs(csv_folder_path)
            
            if os.path.exists(csv_file_path):
                tsne_df = pd.read_csv(csv_file_path)
                if 'Name' not in data.columns:
                    if 'Label' in data.columns:
                        tsne_df['Name'] = data['Label'].astype(str)
                    else:
                        print("Both 'Name' and 'Label' columns are missing in the data.")
                else:
                    tsne_df['Name'] = data['Name']
            else:
                pca = PCA(0.95)
                X_pca = pca.fit_transform(data_drop)
    
                n_components = 2
                model = TSNE(n_components=n_components, random_state=42)
                tsne_result = model.fit_transform(X_pca[:10000])
    
                tsne_df = pd.DataFrame(data=tsne_result, columns=['tsne1', 'tsne2'])
                # tsne_df['Name'] = data['Name'] 
                if 'Name' not in data.columns:
                    if 'Label' in data.columns:
                        tsne_df['Name'] = data['Label'].astype(str)
                    else:
                        print("Both 'Name' and 'Label' columns are missing in the data.")
                else:
                    tsne_df['Name'] = data['Name']
                   
                tsne_df.to_csv(csv_file_path, index=False)  # t-SNE 결과를 CSV 파일로 저장
            
            
            # update_ui 시그널을 통해 메인 UI에 그래프 업데이트 알림
            self.update_ui.emit(tsne_df, file_name, idx+1)
        
        self.finished.emit()
        self.quit()
        
def extract_file_name(file_path):
    return os.path.basename(file_path)