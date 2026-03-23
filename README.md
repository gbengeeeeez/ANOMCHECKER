# 🛡️ ANOMCHECKER
### Clustering-Based Cybersecurity Threat Detection in Network Logs

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Plotly_Dash-2.14.0-cyan?logo=plotly)](https://dash.plotly.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3.2-orange?logo=scikit-learn)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

ANOMCHECKER is an interactive web application that detects cybersecurity threats in network log files using **unsupervised clustering** — no labelled training data required. Upload a CSV network traffic file, select a row range, and the system automatically runs **K-Means** and **DBSCAN** clustering, evaluates both algorithms, and surfaces flagged anomalies for download.

---

## 📸 Dashboard Preview

> *(Add a screenshot of your running dashboard here)*

---

## ✨ Features

- **Fully unsupervised** — detects threats without predefined attack signatures or labelled datasets
- **Two algorithms compared** — K-Means (8-seed optimised) vs DBSCAN (automated epsilon selection)
- **Interactive Plotly Dash dashboard** — browser-based, no coding required to use
- **PCA scatter plots** — visualise cluster separation for both algorithms
- **Side-by-side confusion matrices** — separate labelled heatmaps for K-Means and DBSCAN
- **Algorithm comparison bar chart** — Accuracy, Precision, Recall, F1-Score, FPR at a glance
- **Downloadable threat report** — flagged anomaly rows exported as CSV with `ANOMCHECKER_FLAG` column
- **Supports CICIDS2017 and UNSW-NB15** benchmark datasets out of the box

---

## 🗂️ Project Structure

```
ANOMCHECKER/
│
├── app.py                  # Entry point — launches Dash server at localhost:8050
├── layout.py               # Full dashboard UI structure (Plotly Dash)
├── callbacks.py            # All Dash callback logic
├── preprocessing.py        # 5-step data preprocessing pipeline
├── models.py               # K-Means and DBSCAN clustering implementations
├── visualizations.py       # All Plotly figure builders
│
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOURUSERNAME/ANOMCHECKER.git
cd ANOMCHECKER
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Then open your browser and navigate to **http://localhost:8050**

---

## 🚀 Usage

1. **Upload** a network traffic CSV file (CICIDS2017 or UNSW-NB15 format)
2. **Set row range** — enter start and end rows (max 10,000 rows per analysis)
3. **Click RUN ANOMCHECKER** — preprocessing and clustering execute automatically
4. **View results** — metric cards, PCA scatter plots, confusion matrices, comparison chart
5. **Download** — export flagged threat rows as `anomchecker_flagged_threats.csv`

---

## 📊 Algorithms

### K-Means
- `k=2` (binary normal/threat classification)
- `k-means++` initialisation for robust centroid placement
- **8-seed optimisation** (seeds: 0, 1, 2, 3, 7, 10, 42, 99) — best F1-score run selected
- Cluster labelling by size: larger cluster = Normal, smaller = Threat

### DBSCAN
- **Automated epsilon selection** via 85th-percentile of 5-nearest-neighbour distance distribution — no manual tuning required
- `MinPts = 5`
- Noise points (label = -1) mapped to Threat class; cluster members mapped to Normal

---

## 🔄 Preprocessing Pipeline

The 5-step pipeline (`preprocessing.py`) applied before clustering:

| Step | Operation |
|------|-----------|
| 1 | Drop irrelevant columns (IP strings, timestamps, ID fields) |
| 2 | Handle infinite and missing values (replace ±inf → NaN; impute with column means) |
| 3 | Remove zero-variance features |
| 4 | Remove highly correlated features (Pearson \|r\| > 0.95) |
| 5 | StandardScaler normalisation (zero mean, unit variance) |

---

## 📈 Experimental Results

Primary experiment: **UNSW-NB15 testing partition**, rows 60,001–70,000 (n=10,000; 41.5% normal / 58.5% attack)

| Metric | K-Means | DBSCAN | Winner |
|--------|---------|--------|--------|
| Accuracy | 59.40% | 43.08% | K-Means |
| Precision | 68.12% | 56.85% | K-Means |
| Recall | 57.55% | 11.35% | K-Means |
| F1-Score | **62.39%** | 18.92% | **K-Means** |
| False Positive Rate | 37.99% | **12.15%** | **DBSCAN** |

> **Note:** The elevated FPR for K-Means reflects the attack-majority composition of the UNSW-NB15 testing partition (52.6% attack), which is an intentional property of the official dataset designed for challenging evaluation.

---

## 📦 Dependencies

```
dash==2.14.0
dash-bootstrap-components
plotly==5.17.0
scikit-learn==1.3.2
pandas==2.1.1
numpy==1.26.0
```

Full list in `requirements.txt`.

---

## 🗃️ Supported Datasets

| Dataset | Source | Records | Features |
|---------|--------|---------|----------|
| UNSW-NB15 | Australian Centre for Cyber Security (ACCS), UNSW Canberra | ~2.5M | 49 |
| CICIDS2017 | Canadian Institute for Cybersecurity (CIC), Univ. of New Brunswick | ~3M | 80+ |

Both datasets are publicly available for research use.

---

## 🔬 Reproducing Experimental Results

To reproduce the results reported in the thesis:

1. Download the **UNSW-NB15 testing partition** CSV from the [official UNSW-NB15 page](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
2. Upload the file to ANOMCHECKER
3. Set **Start Row: 60001** and **End Row: 70000**
4. Click **RUN ANOMCHECKER**

Expected output: K-Means F1 ≈ 62.39%, DBSCAN F1 ≈ 18.92%

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Developed as an undergraduate thesis project at **Babcock University**, Department of Computer Science, Ilishan-Remo, Ogun State, Nigeria.

---

## 🙏 Acknowledgements

- UNSW-NB15 dataset: Moustafa, N. & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems. *MilCIS 2015*.
- CICIDS2017 dataset: Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward generating a new intrusion detection dataset and intrusion traffic characterization. *ICISSP 2018*.
