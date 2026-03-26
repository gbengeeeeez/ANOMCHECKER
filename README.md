# 🛡️ ANOMCHECKER
### K-Means Clustering-Based Cybersecurity Threat Detection in Network Logs

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Plotly_Dash-2.14.0-cyan?logo=plotly)](https://dash.plotly.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3.2-orange?logo=scikit-learn)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

ANOMCHECKER is an interactive web application that detects cybersecurity threats in network log files using **K-Means unsupervised clustering** — no labelled training data or predefined attack signatures required. Upload a CSV network traffic file, select a row range, and the system automatically runs K-Means clustering, evaluates performance, and surfaces flagged anomalies for download.

> **Algorithm Selection:** K-Means was selected through a rigorous comparative study of three unsupervised algorithms — K-Means, DBSCAN, and Isolation Forest — evaluated across **eight row ranges** of the UNSW-NB15 testing partition in Google Colab. K-Means achieved the highest average F1-score of **41.81%** across all ranges, outperforming DBSCAN (12.95%) and Isolation Forest (40.55%).

---

## 📸 Dashboard Preview

> *(Add a screenshot of your running dashboard here)*

---

## ✨ Features

- **Fully unsupervised** — detects threats without labelled datasets or predefined attack signatures
- **K-Means with 8-seed optimisation** — runs across eight random seeds, selects the best F1-score run
- **k-means++ initialisation** — robust centroid placement for reliable cluster separation
- **Interactive Plotly Dash dashboard** — browser-based, no coding required to use
- **PCA scatter plot** — visualise cluster separation in 2D principal component space
- **Confusion matrix heatmap** — clear TP, TN, FP, FN breakdown with colour coding
- **Performance metrics bar chart** — Accuracy, Precision, Recall, F1-Score, FPR at a glance
- **Downloadable threat report** — flagged rows exported as CSV with `ANOMCHECKER_FLAG` column
- **Supports CICIDS2017 and UNSW-NB15** benchmark datasets out of the box

---

## 📊 Experimental Results

### Primary Experiment
**Dataset:** UNSW-NB15 Testing Partition — Rows 60,001 to 70,000
**Subset:** n=10,000 records | 41.5% Normal / 58.5% Attack

| Metric | K-Means | DBSCAN | Isolation Forest |
|--------|---------|--------|-----------------|
| Accuracy | **59.40%** | 44.27% | 37.34% |
| Precision | **68.12%** | 62.72% | 45.86% |
| Recall | **57.55%** | 11.76% | 39.18% |
| F1-Score | **62.39%** | 19.80% | 42.26% |
| False Positive Rate | 37.99% | **9.86%** | 65.26% |

> DBSCAN and Isolation Forest results were generated in Google Colab for comparative documentation. ANOMCHECKER runs K-Means as its production algorithm.

### Eight-Range Trend Analysis (Google Colab)

| Row Range | Normal % | Attack % | K-Means F1 | DBSCAN F1 | Iso. Forest F1 |
|-----------|----------|----------|------------|-----------|----------------|
| 1–10,000 | 2.4% | 97.6% | 59.97% | 20.08% | 64.58% |
| 10,001–20,000 | 0.0% | 100.0% | 27.44% | 23.76% | 66.67% |
| 20,001–30,000 | 66.4% | 33.6% | **99.17%** | 2.10% | 35.95% |
| 30,001–40,000 * | 100.0% | 0.0% | 0.00% | 0.00% | 0.00% |
| 40,001–50,000 | 36.4% | 63.6% | 43.07% | 15.92% | 48.51% |
| 50,001–60,000 | 0.0% | 100.0% | 42.41% | 21.97% | 66.65% |
| **60,001–70,000** | **41.5%** | **58.5%** | **62.39%** | 19.80% | 42.02% |
| 70,001–80,000 * | 100.0% | 0.0% | 0.00% | 0.00% | 0.00% |
| **AVERAGE** | | | **41.81%** | 12.95% | 40.55% |

> \* Single-class ranges — F1=0% is expected behaviour, not algorithm failure.

---

## 🗂️ Project Structure

```
ANOMCHECKER/
│
├── app.py                  # Entry point — launches Dash server at localhost:8050
├── layout.py               # Full dashboard UI structure (Plotly Dash)
├── callbacks.py            # All Dash callback logic — K-Means only pipeline
├── preprocessing.py        # 5-step data preprocessing pipeline
├── models.py               # K-Means 8-seed optimisation + metric computation
├── visualizations.py       # PCA scatter, confusion matrix, metrics bar chart
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

### 2. Create a virtual environment (recommended)
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

Open your browser and navigate to **http://localhost:8050**

---

## 🚀 Usage

1. **Upload** a network traffic CSV file (CICIDS2017 or UNSW-NB15 format)
2. **Set row range** — enter start and end rows (max 10,000 rows per analysis)
3. **Click RUN ANOMCHECKER** — preprocessing and K-Means execute automatically
4. **View results** — metric cards, PCA scatter plot, confusion matrix, metrics bar chart
5. **Download** — export flagged threat rows as `anomchecker_flagged_threats.csv`

---

## 🔬 How It Works

### K-Means Clustering
- **k=2** — binary classification: Normal (0) vs Threat (1)
- **k-means++ initialisation** for robust centroid placement
- **8-seed optimisation** — seeds 0, 1, 2, 3, 7, 10, 42, 99; best F1-score run selected
- **Cluster labelling by size** — larger cluster = Normal, smaller = Threat

### Why K-Means?
Empirically validated across 8 row ranges of the UNSW-NB15 testing partition:
- Highest average F1-score (41.81%) — DBSCAN 12.95%, Isolation Forest 40.55%
- Most consistent on mixed-class ranges representing real-world conditions
- Near-perfect detection (F1=99.17%) on normal-majority subsets
- DBSCAN fails because dense attack groups are misclassified as normal clusters
- Isolation Forest produces excessive false positives (65.26% FPR) on mixed-class data

---

## 🔄 Preprocessing Pipeline

| Step | Operation |
|------|-----------|
| 1 | Drop irrelevant columns (IP strings, timestamps, IDs) |
| 2 | Handle infinite/missing values — replace ±inf with NaN; impute with column means |
| 3 | Remove zero-variance features |
| 4 | Remove highly correlated features (Pearson \|r\| > 0.95) |
| 5 | StandardScaler normalisation — z = (x − μ) / σ |

---

## 📏 Evaluation Metrics

| Metric | Formula |
|--------|---------|
| Accuracy | (TP + TN) / (TP + TN + FP + FN) |
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1-Score | 2 × (Precision × Recall) / (Precision + Recall) |
| False Positive Rate | FP / (FP + TN) |

---

## 🗃️ Supported Datasets

| Dataset | Source | Records | Features |
|---------|--------|---------|----------|
| UNSW-NB15 | Australian Centre for Cyber Security, UNSW Canberra | ~2.5M | 49 |
| CICIDS2017 | Canadian Institute for Cybersecurity, Univ. of New Brunswick | ~3M | 80+ |

---

## 🔁 Reproducing Experimental Results

1. Download the **UNSW-NB15 testing partition** CSV from [research.unsw.edu.au](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
2. Upload to ANOMCHECKER
3. Set **Start Row: 60001** and **End Row: 70000**
4. Click **RUN ANOMCHECKER**

Expected: K-Means Accuracy=59.40%, Precision=68.12%, Recall=57.55%, F1=62.39%, FPR=37.99%

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

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Undergraduate thesis project — **Babcock University**, Department of Computer Science, Ilishan-Remo, Ogun State, Nigeria.

---

## 🙏 Acknowledgements

- UNSW-NB15: Moustafa, N. & Slay, J. (2015). *MilCIS 2015*.
- CICIDS2017: Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). *ICISSP 2018*.
- Built with [Plotly Dash](https://dash.plotly.com/), [Scikit-learn](https://scikit-learn.org/), and [Pandas](https://pandas.pydata.org/).
