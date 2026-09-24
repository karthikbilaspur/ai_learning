import pandas as pd

def generate_report(eval_results, judge_scores=None, save_path="report.html"):
    judge_scores = judge_scores or []
    summary = dict(eval_results)
    table_html = "<p><em>No judge scores (run with --judge).</em></p>"

    if judge_scores:
        df = pd.DataFrame(judge_scores)
        for col in ["correctness", "helpfulness", "harmlessness", "groundedness"]:
            if col in df.columns:
                summary[f"avg_{col}"] = float(df[col].mean())
        table_html = df.describe().to_html()

    html = f"<h1>LLM Eval Report</h1><pre>{summary}</pre><br>{table_html}"
    with open(save_path, "w") as f:
        f.write(html)
    print(f"Report saved to {save_path}")
    return summary
