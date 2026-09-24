import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class TimeSeriesRetriever:
    """Retrieves the k most similar historical windows to a query window,
    using simple stats+FFT embeddings + cosine similarity."""

    def __init__(self, history):
        # history: [N, window_len] -- this is the retrieval corpus (should
        # be built from *training* windows only, never from windows that
        # overlap with a validation/test query, or the model can cheat by
        # retrieving its own answer).
        self.history = history
        self.embeddings = self._embed(history)

    def _embed(self, windows):
        embs = []
        for w in windows:
            emb = np.array([w.mean(), w.std(), w.max(), w.min(), np.fft.rfft(w).real.mean()])
            embs.append(emb)
        return np.stack(embs)

    def retrieve(self, query_window, k=5, exclude_idx=None):
        """exclude_idx: index into self.history to drop from the results
        (use this when the query window itself is part of the corpus, to
        avoid trivially retrieving itself)."""
        q_emb = self._embed([query_window])[0]
        sims = cosine_similarity([q_emb], self.embeddings)[0]
        if exclude_idx is not None:
            sims = sims.copy()
            sims[exclude_idx] = -np.inf
        idx = np.argsort(sims)[-k:][::-1]
        return self.history[idx], sims[idx]
