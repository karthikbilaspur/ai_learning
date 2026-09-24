# Troubleshooting

Common issues you might hit while working through this project, and how to fix them.

## `docker compose up` fails with "port is already allocated"
Something else on your machine is already using port 80, 9090, or 3001.
Either stop that service, or change the left-hand side of the port mapping in
`docker-compose.yml` (e.g. `"8080:80"` instead of `"80:80"`).

## `http://localhost/` shows a 502 Bad Gateway
The `app` container probably isn't up yet, or it crashed. Check with:
```bash
docker compose logs app
```
Nginx starts fast; the Python app can take a few seconds longer.

## Grafana doesn't show the Prometheus data source
Provisioning only runs the *first* time a fresh Grafana volume is created.
If you edited `monitoring/grafana/provisioning/datasources/prometheus.yml`
after already starting Grafana once, reset it with:
```bash
docker compose down -v
docker compose up --build
```
(This deletes any dashboards you've saved — see the `clean` Makefile target.)

## `kubectl apply -f k8s/` says the app image can't be found
On Minikube, images built on your host aren't visible to the cluster by
default. Point your shell at Minikube's Docker daemon first:
```bash
eval $(minikube docker-env)
docker build -t devops-starter:local .
```

## Terraform apply succeeds but you can't SSH into the EC2 instance
Make sure you passed `-var="key_name=your-key-pair-name"` and that the key
pair actually exists in the same AWS region as `var.aws_region`. Also give
the instance a minute or two to finish running the startup script before
connecting.

## Tests fail with `ModuleNotFoundError: No module named 'app'`
Run `pytest` from the project's root folder, not from inside `tests/`.
