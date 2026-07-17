# 🧬 AI Biomarker Discovery Platform

An end-to-end **AI-powered biomarker discovery platform** that integrates bioinformatics, machine learning, and explainable AI to identify potential disease-associated biomarkers from gene expression data.

The platform allows researchers to upload or automatically retrieve public gene expression datasets, perform preprocessing, train machine learning models, interpret predictions using SHAP explainability, and generate biological insights.

---

# 🚀 Project Overview

Finding reliable biomarkers from high-dimensional genomic data is challenging because gene expression datasets contain thousands of features (genes) but limited samples.

This project aims to build an automated workflow:

```
Gene Expression Data
          |
          ↓
Data Preprocessing
          |
          ↓
Exploratory Analysis
          |
          ↓
Feature Selection
          |
          ↓
Machine Learning Models
          |
          ↓
Explainable AI (SHAP)
          |
          ↓
Biomarker Ranking
          |
          ↓
Biological Interpretation
```

---

# ✨ Features

## 📂 Dataset Management

Supports:

- User-uploaded gene expression matrices
- Sample metadata upload
- Example datasets
- GEO accession-based dataset retrieval

Currently supports:

- GEO datasets (GSE accession)
- CSV expression matrices
- CSV metadata files

---

## 🧬 Gene Expression Processing

Pipeline includes:

- Expression matrix loading
- Sample validation
- Metadata matching
- Data preprocessing
- Gene feature handling
- Dataset quality checks

---

## 🔍 Exploratory Analysis

Includes:

- Gene expression visualization
- PCA analysis
- Sample clustering
- Distribution analysis

---

## 🤖 Machine Learning

Implemented models:

- Random Forest Classifier
- Logistic Regression

The models learn patterns between:

```
Gene Expression → Disease State
```

---

## 🔬 Explainable AI

Uses SHAP (SHapley Additive exPlanations) to understand model decisions.

Provides:

- Global feature importance
- Top biomarker candidates
- SHAP summary plots
- SHAP ranking of important genes

---

## 🧪 GEO Dataset Integration

The platform can automatically:

- Download GEO datasets
- Extract expression matrices
- Extract sample metadata
- Detect experimental groups
- Prepare data for downstream analysis

Example:

```
GSE2034
        |
        ↓
Expression Matrix
        |
        ↓
Metadata
        |
        ↓
Machine Learning Pipeline
```

---

# 🏗️ Project Architecture

```
AI_Biomarker_Discovery/

│
├── app.py
│
├── pages/
│   ├── 1_Dataset.py
│   ├── 2_Preprocessing.py
│   ├── 3_Exploration.py
│   ├── 4_Feature_Selection.py
│   ├── 5_Machine_Learning.py
│   ├── 6_SHAP_Explainability.py
│   └── 7_Report.py
│
├── utils/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_selection.py
│   ├── models.py
│   ├── shap_analysis.py
│   ├── geo_downloader.py
│   └── report.py
│
├── data/
│
├── requirements.txt
│
└── README.md
```

---

# 🛠️ Tech Stack

## Programming

- Python 3.12+

## Bioinformatics

- GEOparse
- Gene expression analysis
- Genomic datasets

## Machine Learning

- Scikit-learn
- Random Forest
- Logistic Regression

## Explainable AI

- SHAP

## Data Processing

- Pandas
- NumPy

## Visualization

- Matplotlib
- Streamlit

## Report Generation

- ReportLab

---

# 📊 Input Data Format

## Expression Matrix

Example:

| Gene | Sample_1 | Sample_2 | Sample_3 |
|---|---|---|---|
| TP53 | 10.2 | 12.5 | 8.4 |
| EGFR | 5.6 | 7.2 | 2.3 |

Format:

```
Gene → First column
Samples → Remaining columns
```

---

## Metadata File

Example:

| Sample | Group |
|---|---|
| Sample_1 | Control |
| Sample_2 | Control |
| Sample_3 | Disease |

Sample names must match expression matrix columns.

---

# ⚙️ Installation

Clone repository:

```bash
git clone https://github.com/Bano733-code/AI-Biomarker-Discovery.git
```

Navigate:

```bash
cd AI-Biomarker-Discovery
```

Create environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 📈 Future Improvements

Planned improvements:

- Differential expression analysis
- GO and KEGG pathway enrichment
- Gene ontology annotation
- Biological network visualization
- RNA-seq normalization workflows
- Deep learning models
- Automated research report generation
- Integration with additional biological databases

---

# 🎯 Motivation

This project explores the application of:

- Machine Learning
- Explainable AI
- Computational Biology
- Genomics

for discovering interpretable biomarkers from high-dimensional biological datasets.

---

# 👩‍💻 Author

**Bano Rani**

BS Bioinformatics Student  
Research Interests:

- Machine Learning in Bioinformatics
- Computational Biology
- Genomics
- Precision Medicine
- AI-driven Drug Discovery

---

# ⭐ Acknowledgements

Data sources:

- NCBI Gene Expression Omnibus (GEO)
- Public genomic datasets

Libraries:

- Scikit-learn
- SHAP
- Streamlit
- GEOparse
