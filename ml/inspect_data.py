import pandas as pd

benign = pd.read_csv("dataset/output-of-benign-pcap-3.csv")
phishing = pd.read_csv("dataset/output-of-phishing-pcap.csv")

print("BENIGN SOURCE PORTS:")
print(benign["src_port"].value_counts().head(20))

print("\nPHISHING SOURCE PORTS:")
print(phishing["src_port"].value_counts().head(20))

print("\nUNNAMED COLUMN:")
print(benign["Unnamed: 0"].head(10))
print(phishing["Unnamed: 0"].head(10))