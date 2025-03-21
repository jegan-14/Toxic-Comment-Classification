import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.layers import TextVectorization
from tensorflow.keras.preprocessing.sequence import pad_sequences
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

word_classifier_model = tf.keras.models.load_model("toxic_word_classifier.h5")
custom_stop_words = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "arent",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "cant",
    "cannot",
    "could",
    "couldnt",
    "did",
    "didnt",
    "do",
    "does",
    "doesnt",
    "doing",
    "dont",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "going",
    "had",
    "hadnt",
    "has",
    "hasnt",
    "have",
    "havent",
    "having",
    "he",
    "hed",
    "hell",
    "hes",
    "her",
    "here",
    "heres",
    "hers",
    "herself",
    "hey",
    "him",
    "himself",
    "his",
    "how",
    "hows",
    "i",
    "id",
    "ill",
    "im",
    "ive",
    "if",
    "in",
    "into",
    "is",
    "isnt",
    "it",
    "its",
    "its",
    "itself",
    "lets",
    "me",
    "more",
    "most",
    "mustnt",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shant",
    "she",
    "shed",
    "shell",
    "shes",
    "should",
    "shouldnt",
    "so",
    "some",
    "such",
    "than",
    "that",
    "thats",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "theres",
    "these",
    "they",
    "theyd",
    "theyll",
    "theyre",
    "theyve",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasnt",
    "we",
    "wed",
    "well",
    "were",
    "weve",
    "were",
    "werent",
    "what",
    "whats",
    "when",
    "whens",
    "where",
    "wheres",
    "which",
    "while",
    "who",
    "whos",
    "whom",
    "why",
    "whys",
    "with",
    "wont",
    "would",
    "wouldnt",
    "you",
    "youd",
    "youll",
    "youre",
    "youve",
    "your",
    "yours",
    "yourself",
    "yourselves",
}

# Load the tokenizer
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Initialize the Flask app
app = Flask(__name__)
CORS(app)


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
    # Check if all probabilities are below 0.5

    if all_less_than_05:
        return jsonify({"text": text, "classification": "safe comment"})

    # Get the predicted result for each word in toxic comment
    words = text.split()
    toxic_words = [classify_word(word) for word in words]

    filtered_text = " ".join(
        "***" if toxic_words[i] == 1 else words[i] for i in range(len(toxic_words))
    )

    return jsonify(
        {
            "original_text": text,
            "filtered_text": filtered_text,
            "classification": "toxic",
        }
    )


def classify_word(word):
    if word in custom_stop_words:
        return 0
    result = predict_toxic_word(word)
    return result


def predict_toxic_word(word):
    seq = tokenizer.texts_to_sequences([word])
    seq = pad_sequences(seq, maxlen=1)
    pred = word_classifier_model.predict(seq)[0][0]
    return 1 if pred > 0.7 else 0


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
