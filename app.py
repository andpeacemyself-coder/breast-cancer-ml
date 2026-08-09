import os

from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# Resolve the model path relative to this file so the app works no matter
# which directory the server is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'cancer_model.pkl')

# The 30 cell-measurement features, in the exact order the model was trained on.
FEATURE_NAMES = [
    'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean',
    'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean',
    'radius_se', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se',
    'compactness_se', 'concavity_se', 'concave points_se', 'symmetry_se', 'fractal_dimension_se',
    'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst',
    'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst',
]

# Load the trained model once at startup, failing loudly with a clear message
# rather than crashing with an opaque traceback if the file is missing/corrupt.
try:
    model = joblib.load(MODEL_PATH)
    print(f"[startup] Loaded model from {MODEL_PATH}")
except Exception as exc:  # noqa: BLE001 - surface any load failure clearly
    model = None
    print(f"[startup] WARNING: could not load model at {MODEL_PATH}: {exc}")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template(
            'index.html',
            prediction_text="Error: model not loaded. Ensure cancer_model.pkl is in the app root.",
        )

    try:
        # Read every feature, convert to float, and build a (1, 30) array.
        input_data = [float(request.form[feat]) for feat in FEATURE_NAMES]
        features_array = np.array([input_data], dtype=float)  # shape (1, 30)

        prediction = model.predict(features_array)[0]

        # Model outputs 'M'/'B'; also tolerate a numeric convention (1 == malignant).
        if prediction == 'M' or prediction == 1:
            result_text = "Malignant (M)"
        else:
            result_text = "Benign (B)"

        return render_template('index.html', prediction_text=result_text)

    except KeyError as exc:
        return render_template(
            'index.html',
            prediction_text=f"Error: missing feature value for {exc}.",
        )
    except ValueError:
        return render_template(
            'index.html',
            prediction_text="Error: all 30 features must be valid numbers.",
        )
    except Exception as exc:  # noqa: BLE001 - last-resort guard for the request
        return render_template('index.html', prediction_text=f"Error in prediction: {exc}")


if __name__ == '__main__':
    # Port 5000 is reserved/occupied on many Windows 11 setups (Hyper-V/WSL2
    # dynamic reservations -> WinError 10013), so default to 5001 and allow an
    # override via the PORT environment variable.
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
