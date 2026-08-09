"""Train the breast cancer classifier and save it as cancer_model.pkl.

Uses scikit-learn's built-in Wisconsin Diagnostic Breast Cancer dataset, whose
30 features are an exact match (and in the same column order) for the fields the
Flask form submits.

Label convention note: in the sklearn dataset, target 0 = malignant and
1 = benign. We remap those to the strings 'M' and 'B' so the saved model
predicts human-readable labels that line up with app.py's result logic.

This is a demonstration model trained on a public research dataset. It is not
a clinical device and must not be used for real diagnosis.
"""

import os

import joblib
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "cancer_model.pkl")


def main():
    data = load_breast_cancer()
    X = data.data  # shape (569, 30), same column order as the app's form

    # target_names == ['malignant', 'benign'] -> 0 is malignant, 1 is benign.
    y = np.where(data.target == 0, "M", "B")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Trained RandomForestClassifier on {X.shape[0]} samples, {X.shape[1]} features.")
    print(f"Hold-out test accuracy: {acc:.4f}")
    print(f"Classes: {list(model.classes_)}  (M = Malignant, B = Benign)")

    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
