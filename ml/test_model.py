import pandas as pd
import joblib

# Load the complete pipeline
model = joblib.load("phishing_model.pkl")

# Load test data
df = pd.read_csv("output-of-phishing-pcap.csv", nrows=5)

# Save actual labels
actual_labels = df["label"]

# Remove the same columns removed during training
X = df.drop(
    columns=[
        "label",
        "flow_id",
        "timestamp",
        "src_ip",
        "dst_ip",
        "dns_domain_name"
    ]
)

# Make predictions
predictions = model.predict(X)

# Get phishing probability
probabilities = model.predict_proba(X)[:, 1]

# Display results
for i in range(len(X)):
    print("\n-------------------------")
    print("Sample:", i + 1)
    print("Actual:", actual_labels.iloc[i])
    print(
        "Prediction:",
        "Phishing" if predictions[i] == 1 else "Benign"
    )
    print(
        "Phishing probability:",
        round(probabilities[i] * 100, 2),
        "%"
    )