import joblib
import pandas as pd

# Load the complete trained pipeline
pipeline = joblib.load("phishing_model.pkl")

# Get preprocessing and model
preprocessor = pipeline.named_steps["preprocessor"]
model = pipeline.named_steps["model"]

# Get feature names after preprocessing
feature_names = preprocessor.get_feature_names_out()

# Get Random Forest importance
importances = model.feature_importances_

# Create table
importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})

# Sort from most important to least important
importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

# Show top 30
print("\nTop 30 Most Important Features:\n")
print(importance_df.head(30).to_string(index=False))

# Save to CSV
importance_df.to_csv("feature_importance.csv", index=False)

print("\nSaved as feature_importance.csv")