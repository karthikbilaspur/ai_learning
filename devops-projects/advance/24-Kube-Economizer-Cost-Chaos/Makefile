deploy:
	terraform -chdir=terraform init && terraform -chdir=terraform apply
	kubectl apply -f chaos/
