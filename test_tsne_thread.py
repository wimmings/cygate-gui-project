import os
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from PySide6.QtCore import QThread, Signal
import re


class TestTSNEThread(QThread):
    # update_text = Signal(str)
    update_ui = Signal(pd.DataFrame, str)  # 시그널 추가
    finished = Signal()
    
    def __init__(self, test_data, parent=None):
        super(TestTSNEThread, self).__init__(parent)
        self.test_data = test_data
        
    def run(self):
        print(self.test_data)
        matching_files = find_cygated_files(self.test_data)
        
        file_name = ''
        if len(matching_files) > 1:
            file_name = 'merged_'
     
        merged_df = pd.DataFrame()
        names = []  # 각 파일의 'Name' 정보를 저장하기 위한 리스트
        file_names = [] # 각 파일의 정보를 저장하기 위한 리스트
        sample_size = 10000//len(matching_files)
        
        for path in matching_files:
            file = extract_file_name(path)
            numbers = re.findall(r'\d+', file)
            file_number = numbers[0] if numbers else "00"
            file_name = file_name + numbers[0] + '_'
            
            data = pd.read_csv(path)            

            # 데이터 프레임에서 랜덤으로 샘플 추출
            sampled_data = data.sample(n=min(sample_size, len(data)), random_state=42)

            # 'Name' 정보를 별도로 저장
            # names.extend(sampled_data['Name'])
            if 'Name' not in sampled_data.columns:
                    if 'Label' in sampled_data.columns:
                        names.extend(sampled_data['Label'].astype(str))
                    else:
                        print("Both 'Name' and 'Label' columns are missing in the data.")
            else:
                names.extend(sampled_data['Name'])
            
            # 어느 파일에서 왔는지 저장
            file_names.extend([file_number] * sample_size)

            columns_to_delete = ['Label', 'Name', 'Gated']
            # sampled_data = sampled_data.drop(columns=columns_to_delete, axis=1)

            for column in columns_to_delete:
                if column in sampled_data.columns:
                    sampled_data = sampled_data.drop(column, axis=1)
            merged_df = pd.concat([merged_df, sampled_data])

        
        file_name = file_name[:-1]
        
        # 추가: 특정 CSV 파일이 이미 존재하는 경우 t-SNE를 실행하지 않고 파일을 사용
        csv_folder_path = 'cygate/graphs/test'  
        csv_file_path = os.path.join(csv_folder_path, 'graph_test_' + re.split('_', extract_file_name(matching_files[0]))[0] + '_' + file_name + '.csv')
        
        # 폴더가 없으면 새로 생성
        if not os.path.exists(csv_folder_path):
            os.makedirs(csv_folder_path)
            
        if os.path.exists(csv_file_path):
            tsne_df = pd.read_csv(csv_file_path)
            tsne_df['Name'] = names
            tsne_df['File'] = file_names
        else:
            # pca = PCA(0.95)
            # X_pca = pca.fit_transform(merged_df)

            n_components = 2
            model = TSNE(n_components=n_components, random_state=42)
            
            if len(merged_df) > 10000:
                tsne_result = model.fit_transform(merged_df[:10000])
            else:
                tsne_result = model.fit_transform(merged_df)

            tsne_df = pd.DataFrame(data=tsne_result, columns=['tsne1', 'tsne2'])
            tsne_df['Name'] = names
            tsne_df['File'] = file_names
            
            if 'Label' in data.columns:
                tsne_df.loc[data['Label'] == 0, 'Name'] = 'NA_'
                
            tsne_df.to_csv(csv_file_path, index=False)  # t-SNE 결과를 CSV 파일로 저장

        if 'Label' in data.columns:
            tsne_df.loc[data['Label'] == 0, 'Name'] = 'NA_'
        self.update_ui.emit(tsne_df, file_name)
        self.finished.emit()
        self.quit()
        
        
# 문자열 포함하는 파일 찾기
def find_cygated_files(file_paths):
    cygated_files = []

    for file_path in file_paths:
        # 파일 이름에서 '_wlabel'을 '_wlabel_cygated'로 교체
        cygated_file_path = file_path.replace('_wlabel', '_wlabel_cygated')

        # 파일이 존재하는지 확인
        if os.path.exists(cygated_file_path):
            cygated_files.append(cygated_file_path)

    return cygated_files

def extract_file_name(file_path):
    return os.path.basename(file_path)

