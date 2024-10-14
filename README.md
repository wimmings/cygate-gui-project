# Cygate GUI project
This program is designed for flow cytometry data analysis, providing both automatic and manual gating capabilities. The core feature includes the use of Cygate for automatic gating of single-cell cytometry data. Additionally, it supports manual gating, allowing users to manually adjust and refine gates based on their analysis needs.

The program also includes an evaluation feature, enabling users to assess the quality of the gated data with built-in metrics.

### Key Features:
- Automatic Gating using Cygate for high-throughput cytometry data.
- Manual Gating support for flexible and customized data refinement.
- Evaluation Functionality to assess gated data.

### Resources:
- Cygate Paper: [Na S, Choo Y, Yoon TH, Paek E. CyGate Provides a Robust Solution for Automatic Gating of Single Cell Cytometry Data. Anal Chem. 2023 Nov 21;95(46):16918-16926. doi: 10.1021/acs.analchem.3c03006. Epub 2023 Nov 9. PMID: 37946317; PMCID: PMC10666088.]([link to paper](https://pubmed.ncbi.nlm.nih.gov/37946317/)) 
- Cygate GitHub Repository: ([link to GitHub](https://github.com/HanyangBISLab/cygate))

# Cygate GUI Project Instructions

- src/data folder: Contains the dataset used in this project.
- src folder: Contains the source code for the project.



### 1. Setting Up and Activating the Virtual Environment(Python 3.8+ Required)
- Ensure that you are using Python version 3.8 or higher.

### 2. Clone the Repository
`https://github.com/wimmings/cygate-gui-project.git`  
`cd cygate-gui-project/src`

### 3. Install Required Libraries in the Virtual Environment
`pip install -r requirements.txt`

### 4. Run the Project
`python project.py`

---

## 1. How to Run Cygate TSNE
1. Select the `train` file → Select the `test` file (located in the `data` folder).
2. Click `Run` for Cygate → The output will be saved as `testfilename_cygated.csv` with labeled data.
3. Visualize the `train` file’s cell distribution using a 2D `tsne` graph & bar graph.
4. Visualize the `test` file’s cell distribution using a 2D `tsne` graph & bar graph.
5. The CSV files of the tsne cell distribution for the train and test sets will be saved in `/cygate/train` and `/cygate/test` directories under the directory where the code was executed.

## 2. How to Run Manual Gating
1. `Load` the file and click `Run`.
2. Select the type of plot: Scatter or Bar Plot.
3. For Scatter Plot, select the X, Y, and Z axes (Z-axis options: Density, Feature, Name).
4. Use right-click and drag to select the Gating range, then press the Gating button to perform Manual Gating.
5. Use the `Save` button to assign or modify the cell type of the selected range.
6. Use `3D mode` and adjust the `Compare Instance` to observe the distribution in different settings.

## 3. How to Run Evaluation
