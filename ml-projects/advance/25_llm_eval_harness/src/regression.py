import argparse,json
from benchmark import compare_metrics

def main(before,after):
    b=json.load(open(before));a=json.load(open(after));print(json.dumps(compare_metrics(b,a),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--before',required=True);p.add_argument('--after',required=True);args=p.parse_args();main(args.before,args.after)
