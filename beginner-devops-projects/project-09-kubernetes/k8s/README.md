# Kubernetes

## Minikube

Build the image inside Minikube:

```bash
minikube start
eval $(minikube docker-env)
docker build -t devops-starter:local .
kubectl apply -f k8s/
kubectl get pods -n devops-starter
kubectl get services -n devops-starter
minikube service devops-app -n devops-starter
```

`kubectl apply -f k8s/` applies every manifest in the folder — including
`namespace.yaml`, which creates the `devops-starter` namespace everything
else lives in, and `configmap.yaml`, which sets `APP_ENV` inside the pod the
same way `docker-compose.yml` does.

To clean up:

```bash
kubectl delete -f k8s/
```
