from generation.generator import generate_answer

chunks = [
    "PCA reduces dimensionality by projecting data onto principal components.",
    "PCA maximizes variance while reducing correlated features."
]

query = "What is PCA used for?"

print(generate_answer(query, chunks))
