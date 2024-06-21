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
            if 'Name' in data.columns: # 아예 원본 data에서 0인 label의 name을 'NA_'로 주고 시작?
                data.loc[data['Label'] == 0, 'Name'] = 'NA_'
            
            # label_to_name = {}
            # if 'Label' in data.columns and 'Name' in data.columns:
            #     label_to_name = data.set_index('Label')['Name'].to_dict()

            sample = data.sample(n=10000, random_state=42)
            sampled_data = sample.reset_index(drop=True)

            columns_to_delete = ['Label', 'Name']
            
            for column in columns_to_delete:
                if column in sampled_data.columns:
                    data_drop = sampled_data.drop(column, axis=1) # data_drop : sample에서 label, name 제거한 거
            
            # 추가: 특정 CSV 파일이 이미 존재하는 경우 t-SNE를 실행하지 않고 파일을 사용
            csv_folder_path = 'cygate/graphs/train'  
            csv_file_path = os.path.join(csv_folder_path, 'graph_train_' + file_name)
            
            # 폴더가 없으면 새로 생성
            if not os.path.exists(csv_folder_path):
                os.makedirs(csv_folder_path)
            
            if os.path.exists(csv_file_path):
                tsne_df = pd.read_csv(csv_file_path)
                if 'Name' not in sampled_data.columns:
                    if 'Label' in sampled_data.columns:
                        tsne_df['Name'] = sampled_data['Label'].astype(str)
                    else:
                        print("Both 'Name' and 'Label' columns are missing in the sampled_data.")
                else:
                    tsne_df['Name'] = sampled_data['Name']
            else:
                # pca = PCA(0.95)
                # X_pca = pca.fit_transform(data_drop)
    
                n_components = 2
                model = TSNE(n_components=n_components, random_state=42)
                tsne_result = model.fit_transform(data_drop)
    
                tsne_df = pd.DataFrame(data=tsne_result, columns=['tsne1', 'tsne2'])
                # tsne_df['Name'] = data['Name'] 
                if 'Name' not in sampled_data.columns:
                    if 'Label' in sampled_data.columns:
                        tsne_df['Name'] = sampled_data['Label'].astype(str)
                    else:
                        print("Both 'Name' and 'Label' columns are missing in the sampled_data.")
                else:
                    tsne_df['Name'] = sampled_data['Name']
                
                # if 'Label' in data.columns:
                #     tsne_df.loc[data['Label'] == 0, 'Name'] = 'NA_'
                tsne_df.to_csv(csv_file_path, index=False)  # t-SNE 결과를 CSV 파일로 저장
            
            # if 'Label' in data.columns:
            #     tsne_df.loc[data['Label'] == 0, 'Name'] = 'NA_'
            # update_ui 시그널을 통해 메인 UI에 그래프 업데이트 알림
            self.update_ui.emit(tsne_df, file_name, idx+1)
        
        self.finished.emit()
        self.quit()
        
def extract_file_name(file_path):
    return os.path.basename(file_path)