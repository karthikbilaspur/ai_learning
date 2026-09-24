install:
	istioctl install --set profile=demo -y
	kubectl label ns prod istio-injection=enabled --overwrite
	kubectl apply -f istio/
