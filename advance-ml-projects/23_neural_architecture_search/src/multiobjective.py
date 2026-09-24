"""Multi-objective NAS: maximize accuracy while minimizing parameters and estimated CPU latency."""
import argparse, time, optuna, torch
from search_space import SEARCH_SPACE, build_model, parameter_count
from evaluator import evaluate

def objective(trial):
    hidden=trial.suggest_categorical('hidden',SEARCH_SPACE['hidden']); layers=trial.suggest_int('layers',*SEARCH_SPACE['layers'])
    dropout=trial.suggest_float('dropout',*SEARCH_SPACE['dropout']); lr=trial.suggest_float('lr',*SEARCH_SPACE['lr'],log=True)
    model=build_model(hidden,layers,dropout); params=parameter_count(model)
    x=torch.randn(1,784); start=time.perf_counter()
    for _ in range(20): model(x)
    latency=(time.perf_counter()-start)/20*1000
    acc=evaluate(model,lr=lr,epochs=2)
    trial.set_user_attr('params',params); trial.set_user_attr('latency_ms',latency)
    return acc, float(params), latency

def run(n_trials=20):
    study=optuna.create_study(directions=['maximize','minimize','minimize'])
    study.optimize(objective,n_trials=n_trials)
    print('Pareto trials:',len(study.best_trials))
    for t in study.best_trials: print(t.number,t.values,t.params)
    return study
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--n_trials',type=int,default=20);run(p.parse_args().n_trials)
