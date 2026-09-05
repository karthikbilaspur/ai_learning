BASELINE={"Recall@5":0.90,"MRR":0.80,"Faithfulness":0.90,"Answer Relevancy":0.85,"Citation correctness":0.95}
def check_gate(current_metrics,baseline=BASELINE,tolerance=.05):
 return [f"{k} regression: {current_metrics[k]:.3f} < {threshold-tolerance:.3f}" for k,threshold in baseline.items() if k in current_metrics and current_metrics[k]<threshold-tolerance]
