import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from flask import Flask, request, jsonify
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.layers import TextVectorization
import pandas as pd


df = pd.read_csv("balanced_data.csv")

X = df["comment_text"]
y = df[df.columns[2:]].values

# Load the model and vectorizer
model = tf.keras.models.load_model("toxic_classification.h5")

MAX_FEATURES = 200000
vectorizer = TextVectorization(
    max_tokens=MAX_FEATURES, output_sequence_length=1800, output_mode="int"
)
vectorizer.adapt(X.values)

# Initialize the Flask app
app = Flask(__name__)


# Define a route for classification
@app.route("/classify", methods=["POST"])
def classify():
    # Get the input data from the request
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Vectorize the input text
    vectorized_text = vectorizer(text)

    # Make prediction
    prediction = model.predict(np.expand_dims(vectorized_text, 0))
    all_less_than_05 = np.all(prediction < 0.3)
    print(prediction)
    # Check if all probabilities are below 0.5
    
    if all_less_than_05:
        return jsonify({"text": text, "classification": "safe comment"})

    # Otherwise, return the class with the highest probability
    predicted_class = np.argmax(prediction, axis=1)[0]

    return jsonify({"text": text, "predicted_class": int(predicted_class)})


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
