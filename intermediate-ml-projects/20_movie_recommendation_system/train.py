"""
Level 2 upgrade — Movie Recommendation System
- Real dataset (5,043 movies with genres, plot keywords, director, cast,
  IMDb score — data/movie_metadata.csv) instead of 8 hardcoded titles.
- Combines genres + plot keywords + director + top cast into one "soup"
  for TF-IDF, which captures more signal than genre words alone.
- Hybrid scoring: blends content similarity with a popularity/quality prior
  (IMDb score, vote count) so obscure-but-textually-similar movies don't
  dominate over well-regarded ones — a lightweight stand-in for the
  collaborative-filtering blend a ratings dataset would enable.
- Simple evaluation: for a held-out sample of movies, check how often the
  top recommendation shares a genre with the query movie.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

DATA_PATH = "data/movie_metadata.csv"


def clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).replace("|", " ").replace(",", " ")


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["movie_title"] = df["movie_title"].str.strip()
    df = df.drop_duplicates(subset="movie_title").reset_index(drop=True)

    df["soup"] = (
        clean_text(None)
        + df["genres"].apply(clean_text) + " "
        + df["plot_keywords"].apply(clean_text) + " "
        + df["director_name"].fillna("").astype(str) + " "
        + df["actor_1_name"].fillna("").astype(str) + " "
        + df["actor_2_name"].fillna("").astype(str)
    )
    df["num_voted_users"] = df["num_voted_users"].fillna(0)
    df["imdb_score"] = df["imdb_score"].fillna(df["imdb_score"].median())
    return df


def weighted_popularity(df, m_quantile=0.75):
    """IMDb-style Bayesian weighted rating so niche/low-vote titles don't
    dominate purely because of a high raw score."""
    C = df["imdb_score"].mean()
    m = df["num_voted_users"].quantile(m_quantile)
    v = df["num_voted_users"]
    R = df["imdb_score"]
    return (v / (v + m)) * R + (m / (v + m)) * C


def build_recommender(df):
    vectorizer = TfidfVectorizer(stop_words="english", min_df=2)
    matrix = vectorizer.fit_transform(df["soup"])
    similarity = cosine_similarity(matrix)
    indices = pd.Series(df.index, index=df["movie_title"].str.lower())
    return vectorizer, similarity, indices


def recommend(title, df, similarity, indices, n=8, content_weight=0.7):
    key = title.lower().strip()
    if key not in indices.index:
        raise ValueError(f"Unknown movie: {title}")
    idx = indices[key]
    if isinstance(idx, pd.Series):
        idx = idx.iloc[0]

    content_scores = similarity[idx]
    pop_scores = (df["weighted_score"] - df["weighted_score"].min()) / (
        df["weighted_score"].max() - df["weighted_score"].min() + 1e-9
    )
    blended = content_weight * content_scores + (1 - content_weight) * pop_scores.values

    ranked = np.argsort(-blended)
    ranked = [i for i in ranked if i != idx][:n]
    return df.iloc[ranked][["movie_title", "genres", "imdb_score"]]


def evaluate_genre_overlap(df, similarity, indices, sample_size=200, seed=42):
    """Sanity-check metric: does the #1 recommendation share a genre with the query?"""
    rng = np.random.default_rng(seed)
    sample_idx = rng.choice(df.index, size=min(sample_size, len(df)), replace=False)
    hits = 0
    for idx in sample_idx:
        content_scores = similarity[idx].copy()
        content_scores[idx] = -1
        top = np.argmax(content_scores)
        genres_query = set(df.loc[idx, "genres"].split("|"))
        genres_top = set(df.loc[top, "genres"].split("|"))
        if genres_query & genres_top:
            hits += 1
    return hits / len(sample_idx)


def main():
    df = load_data()
    df["weighted_score"] = weighted_popularity(df)

    vectorizer, similarity, indices = build_recommender(df)

    overlap_rate = evaluate_genre_overlap(df, similarity, indices)
    print(f"Genre-overlap sanity check: {overlap_rate:.1%} of top-1 recommendations share a genre with the query")

    for title in ["Avatar", "The Dark Knight Rises", "Inception"]:
        try:
            recs = recommend(title, df, similarity, indices, n=5)
            print(f"\nRecommendations for '{title}':")
            print(recs.to_string(index=False))
        except ValueError as e:
            print(e)

    # Save the sparse TF-IDF matrix + vectorizer instead of the dense
    # similarity matrix (5043x5043 floats would be ~200MB uncompressed;
    # the sparse matrix is a few MB and similarity is computed per-query).
    joblib.dump({
        "df": df[["movie_title", "genres", "imdb_score", "weighted_score"]],
        "tfidf_matrix": vectorizer.transform(df["soup"]),
        "indices": indices,
    }, "movie_recommender.joblib", compress=3)
    print("\nSaved: movie_recommender.joblib")


if __name__ == "__main__":
    main()
