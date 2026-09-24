"""Simple Gaussian baseline and a nearest-neighbour disclosure diagnostic."""
import numpy as np, pandas as pd
class GaussianCopulaBaseline:
    def fit(self,df):
        self.columns=df.columns; self.mean=df.mean(numeric_only=True).values; self.cov=df.cov(numeric_only=True).values+1e-6*np.eye(len(self.mean)); return self
    def sample(self,n): return pd.DataFrame(np.random.multivariate_normal(self.mean,self.cov,size=n),columns=self.columns)
