#!/bin/bash
kubectl port-forward -n kubecost svc/kubecost-cost-analyzer 9090:9090 &
echo "Open http://localhost:9090 for cost report"
