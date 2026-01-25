from explainability.shap_attribution import shap_attribution

chunks = [
    "PCA reduces dimensionality by projecting data.",
    "PCA maximizes variance of projected data.",
    "K-means is a clustering algorithm."
]

query = "What is PCA used for?"

answer, shap_scores = shap_attribution(query, chunks)

print("Answer:", answer)
print("\nSHAP Contributions:")
for c, s in shap_scores:
    print(round(s, 3), "→", c[:60])
