import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


# ==========================================
# 1. Dataset files
# ==========================================

BENIGN_FILE = "dataset/output-of-benign-pcap-3.csv"
PHISHING_FILE = "dataset/output-of-phishing-pcap.csv"

BENIGN_SAMPLES = 50000
PHISHING_SAMPLES = 43348


# ==========================================
# 2. Features that can be reproduced
#    from TShark + Python
# ==========================================

LIVE_FEATURES = [

    # --------------------------------------
    # Flow statistics
    # --------------------------------------

    "duration",

    "packets_numbers",
    "receiving_packets_numbers",
    "sending_packets_numbers",

    "total_bytes",
    "receiving_bytes",
    "sending_bytes",

    "packets_rate",
    "packets_len_rate",


    # --------------------------------------
    # Packet length statistics
    # --------------------------------------

    "min_packets_len",
    "max_packets_len",
    "mean_packets_len",
    "median_packets_len",
    "mode_packets_len",

    "min_receiving_packets_len",
    "max_receiving_packets_len",
    "mean_receiving_packets_len",
    "median_receiving_packets_len",
    "mode_receiving_packets_len",

    "min_sending_packets_len",
    "max_sending_packets_len",
    "mean_sending_packets_len",
    "median_sending_packets_len",
    "mode_sending_packets_len",


    # --------------------------------------
    # DNS / Domain features
    # --------------------------------------

    "dns_domain_name_length",
    "dns_subdomain_name_length",

    "dns_top_level_domain",
    "dns_second_level_domain",

    "character_entropy",
    "numerical_percentage",

    "max_continuous_alphabet_len",
    "max_continuous_consonants_len",

    "vowels_consonant_ratio",
    "conv_freq_vowels_consonants"
]


# ==========================================
# 3. Load dataset
# ==========================================

print("==========================================")
print("LOADING DATASET")
print("==========================================")

print("\nLoading benign data...")

benign = pd.read_csv(
    BENIGN_FILE,
    nrows=BENIGN_SAMPLES
)

print("Benign data loaded:", benign.shape)


print("\nLoading phishing data...")

phishing = pd.read_csv(
    PHISHING_FILE,
    nrows=PHISHING_SAMPLES
)

print("Phishing data loaded:", phishing.shape)


# ==========================================
# 4. Combine datasets
# ==========================================

df = pd.concat(
    [benign, phishing],
    ignore_index=True
)

print("\n==========================================")
print("DATASET INFORMATION")
print("==========================================")

print("\nDataset shape:")
print(df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


# ==========================================
# 5. Convert labels
# ==========================================

df["label"] = df["label"].map({
    "Benign": 0,
    "Phishing": 1
})

print("\nConverted labels:")
print(df["label"].value_counts())


# ==========================================
# 6. Check required features
# ==========================================

print("\n==========================================")
print("CHECKING FEATURES")
print("==========================================")

missing_features = [
    feature
    for feature in LIVE_FEATURES
    if feature not in df.columns
]

if missing_features:

    print("\nERROR!")
    print("The following required features are missing:")

    for feature in missing_features:
        print(" -", feature)

    raise ValueError(
        "Some required features are missing from the dataset."
    )


print(
    "\nAll required features are present."
)

print(
    "Number of selected features:",
    len(LIVE_FEATURES)
)


# ==========================================
# 7. Create X and y
# ==========================================

X = df[LIVE_FEATURES].copy()

y = df["label"]


print("\nFeature matrix shape:")
print(X.shape)


# ==========================================
# 8. Display feature data types
# ==========================================

print("\n==========================================")
print("FEATURE DATA TYPES")
print("==========================================")

print(
    X.dtypes.to_string()
)


# ==========================================
# 9. Identify numeric/categorical features
# ==========================================

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()


print("\n==========================================")
print("FEATURE TYPES")
print("==========================================")

print(
    "\nNumeric features:",
    len(numeric_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)


print("\nCategorical features:")

for feature in categorical_features:
    print(" -", feature)


# ==========================================
# 10. Numeric preprocessing
# ==========================================

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    )
])


# ==========================================
# 11. Categorical preprocessing
# ==========================================

categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="most_frequent"
        )
    ),

    (
        "encoder",
        OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )
    )
])


# ==========================================
# 12. Column transformer
# ==========================================

preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),

    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# ==========================================
# 13. Train / Test split
# ==========================================

print("\n==========================================")
print("TRAIN / TEST SPLIT")
print("==========================================")

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print(
    "\nTraining samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# ==========================================
# 14. Random Forest model
# ==========================================

model = RandomForestClassifier(

    n_estimators=150,

    random_state=42,

    n_jobs=-1,

    class_weight="balanced"
)


# ==========================================
# 15. Complete ML pipeline
# ==========================================

pipeline = Pipeline([

    (
        "preprocessor",
        preprocessor
    ),

    (
        "model",
        model
    )
])


# ==========================================
# 16. Train model
# ==========================================

print("\n==========================================")
print("TRAINING MODEL")
print("==========================================")

print(
    "\nTraining Random Forest..."
)

print(
    "This may take a few minutes..."
)


pipeline.fit(
    X_train,
    y_train
)


print(
    "\nTraining completed successfully!"
)


# ==========================================
# 17. Make predictions
# ==========================================

print("\n==========================================")
print("PREDICTION")
print("==========================================")

print(
    "\nMaking predictions..."
)


y_pred = pipeline.predict(
    X_test
)


# ==========================================
# 18. Model evaluation
# ==========================================

print("\n==========================================")
print("MODEL RESULTS")
print("==========================================")


accuracy = accuracy_score(
    y_test,
    y_pred
)


print(
    "\nAccuracy:"
)

print(
    accuracy
)


print(
    "\nClassification Report:"
)


print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Benign",
            "Phishing"
        ]
    )
)


print(
    "\nConfusion Matrix:"
)


print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# 19. Save complete pipeline
# ==========================================

MODEL_FILE = "phishing_model.pkl"


joblib.dump(
    pipeline,
    MODEL_FILE
)


print("\n==========================================")
print("MODEL SAVED")
print("==========================================")


print(
    f"\nComplete pipeline saved as: {MODEL_FILE}"
)


# ==========================================
# 20. Show final features
# ==========================================

print("\n==========================================")
print("FEATURES USED BY MODEL")
print("==========================================")


for i, feature in enumerate(
    LIVE_FEATURES,
    start=1
):

    print(
        f"{i:2}. {feature}"
    )


print("\n==========================================")
print("DONE")
print("==========================================")