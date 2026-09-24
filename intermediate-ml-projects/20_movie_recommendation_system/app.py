"""Interactive demo for the movie recommender.
Run: python train.py   (once, to produce movie_recommender.joblib)
     python app.py
"""
import numpy as np
import joblib
import gradio as gr
from sklearn.metrics.pairwise import cosine_similarity

bundle = joblib.load("movie_recommender.joblib")
df, tfidf_matrix, indices = bundle["df"], bundle["tfidf_matrix"], bundle["indices"]


def recommend(title, content_weight):
    key = title.lower().strip()
    if key not in indices.index:
        return "Movie not found. Try an exact title, e.g. 'Avatar', 'Inception', 'The Dark Knight Rises'."
    idx = indices[key]
    if hasattr(idx, "iloc"):
        idx = idx.iloc[0]

    content_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).ravel()
    pop = (df["weighted_score"] - df["weighted_score"].min()) / (
        df["weighted_score"].max() - df["weighted_score"].min() + 1e-9
    )
    blended = content_weight * content_scores + (1 - content_weight) * pop.values
    ranked = np.argsort(-blended)
    ranked = [i for i in ranked if i != idx][:8]

    lines = [f"Because you liked **{title}**:"]
    for i in ranked:
        row = df.iloc[i]
        lines.append(f"- {row.movie_title} ({row.genres}) — IMDb {row.imdb_score}")
    return "\n".join(lines)


demo = gr.Interface(
    fn=recommend,
    inputs=[
        gr.Textbox(value="Avatar", label="Movie title"),
        gr.Slider(0, 1, value=0.7, label="Content-similarity weight (vs. popularity)"),
    ],
    outputs=gr.Markdown(label="Recommendations"),
    title="Movie Recommendation System — Level 2",
)

if __name__ == "__main__":
    demo.launch()
