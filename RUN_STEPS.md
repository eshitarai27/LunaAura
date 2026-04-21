# Run Instructions

## 1. Environment Setup
Assuming you have a python environment activated (we use `venv` by default):

```bash
pip install -r requirements.txt
```

## 2. Re-building the Master Dataset
If you modify the source data in `data/raw/`, you must rebuild the matched master dataset:

```bash
python src/data_pipeline/build_master_dataset.py
```
*Note: This matches temporal and lifestyle logs to depression metrics using strict demographic proximities.*

## 3. Retraining the ML Ensembles 
If you simply want to use the pre-trained artifacts in `/src/models/`, skip this. Otherwise:

```bash
# Trains calibrated probabilities and SHAP reference
python src/models/train_classifier.py

# Trains exact scoring and conformal bounds
python src/models/train_regressor.py
```

## 4. Launching the Backend API
```bash
python api/app.py
```
The Flask server will fire on `http://127.0.0.1:5000`. Leave this terminal tab open.

## 5. View the Frontend
Open `web/index.html` directly in your browser. It points straight to localhost:5000 and parses real-time SHAP features and Risk models. 
