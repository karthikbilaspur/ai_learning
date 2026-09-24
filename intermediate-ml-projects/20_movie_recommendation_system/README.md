# 20 - Movie Recommendation System (Level 2)

Content-based recommender over the real **movie_metadata** dataset
(5,043 movies with genres, plot keywords, director, cast, IMDb score).

## What changed from Level 1
- Real, large catalog instead of 8 hardcoded movies.
- The TF-IDF "soup" combines genres + plot keywords + director + top two
  billed actors, capturing more signal than genre words alone.
- **Hybrid scoring**: blends content similarity with an IMDb-style
  Bayesian-weighted popularity/quality prior, so obscure-but-textually-similar
  movies don't crowd out well-regarded ones. This is a lightweight stand-in
  for the collaborative-filtering blend a ratings dataset would enable.
- Simple built-in evaluation: for a random sample of movies, checks how
  often the #1 recommendation shares a genre with the query (78.5% here).
- Interactive Gradio demo (`app.py`) with a content-vs-popularity weight slider.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`movie_recommender.joblib`

## Level 3 ideas
Add real collaborative filtering (matrix factorization on MovieLens ratings)
blended with this content score; poster images and a search box in the demo.
