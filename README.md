# Cygate GUI project 실행 방법

- src/data 폴더 : 본 프로젝트에서 쓰인 데이터 셋입니다.
- src 폴더 : 본 프로젝트의 소스코드입니다.



### 1. 실행시킬 가상환경 설치 및 접속

### 2. git clone 받기
`https://github.com/wimmings/cygate-gui-project.git`  
`cd cygate-gui-project/src`

### 3. 가상환경 터미널에서 라이브러리 설치  
`pip install -r requirements.txt`

### 4. 프로젝트 실행
`python project.py`

---

## 1. Cygate tsne 실행법
1. `train` 파일 선택 → `test` 파일 선택 (`data 폴더` 내)
2. cygate `Run` → 결과물은 `test파일이름_cygated.csv` : 라벨링이 됩니다.
3. train 파일 `tsne` 2차원 그래프 & 막대그래프로 cell분포 표현하기
4. test 파일 `tsne` 2차원 그래프 & 막대 그래프로 cell분표 표현하기
5. train, test의 tsne cell 분포의 `csv 파일`은 각각 `코드를 실행시킨 디렉토리/cygate/train` 과 `/cygate/test`에 생성됩니다.

## 2. Manual Gating 실행법
1. 파일 `Load` → `Run`
2. Scatter or Bar Plot type select, Plot 의 종류를 선택
3. Scatter Plot X 축 Y축 Z축 select, 데이터 분포의 각 축을 선택 (Z축의 경우 Density, Feature, Name)
4. 우클릭 드래그로 Gating range select, 이후 Gating 버튼으로 Manual Gating
5. `Save` 버튼을 통해 현재 범위 데이터의 셀타입을 지정 혹은 수정
6. 3D mode, Background를 통해 다양한 상황에 맞춰 분포 확인
