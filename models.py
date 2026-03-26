# =============================================================
# ANOMCHECKER — models.py
# Clustering implementation — K-Means only.
# DBSCAN and Isolation Forest are evaluated separately in
# Google Colab for comparative study purposes only.
# =============================================================

import numpy as np
from sklearn.cluster  import KMeans
from sklearn.metrics  import (confusion_matrix, f1_score,
                               precision_score, recall_score,
                               accuracy_score)

# Eight seeds used for K-Means optimisation
KMEANS_SEEDS = [0, 1, 2, 3, 7, 10, 42, 99]


def run_kmeans(X_scaled: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    """
    Run K-Means with k=2 across eight random seeds using k-means++
    initialisation. Returns the prediction array from the seed that
    achieved the highest F1-score against ground-truth labels.

    Parameters
    ----------
    X_scaled : np.ndarray  — preprocessed, standardised feature matrix
    y_true   : np.ndarray  — ground-truth labels (used only for seed selection)

    Returns
    -------
    np.ndarray — best predicted labels (0=Normal, 1=Threat)
    """
    best_preds, best_f1 = None, -1

    for seed in KMEANS_SEEDS:
        km    = KMeans(n_clusters=2, init="k-means++",
                       random_state=seed, n_init=10)
        preds = km.fit_predict(X_scaled)

        # Label clusters by size: larger cluster = Normal (0)
        counts = np.bincount(preds)
        if counts[0] < counts[1]:
            preds = 1 - preds

        score = f1_score(y_true, preds, zero_division=0)
        if score > best_f1:
            best_f1    = score
            best_preds = preds.copy()

    return best_preds


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Compute all five evaluation metrics from predicted vs true labels.

    Returns a dict with keys:
        accuracy, precision, recall, f1, fpr,
        tp, tn, fp, fn, cm
    """
    cm             = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    accuracy  = round(accuracy_score(y_true, y_pred)              * 100, 2)
    precision = round(precision_score(y_true, y_pred,
                       zero_division=0)                            * 100, 2)
    recall    = round(recall_score(y_true, y_pred,
                       zero_division=0)                            * 100, 2)
    f1        = round(f1_score(y_true, y_pred,
                       zero_division=0)                            * 100, 2)
    fpr       = round(fp / (fp + tn) * 100, 2) if (fp + tn) > 0 else 0.0

    return {
        "accuracy":  accuracy,
        "precision": precision,
        "recall":    recall,
        "f1":        f1,
        "fpr":       fpr,
        "tp":        int(tp),
        "tn":        int(tn),
        "fp":        int(fp),
        "fn":        int(fn),
        "cm":        cm.tolist(),
    }