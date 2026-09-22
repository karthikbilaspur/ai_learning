zip:
	cd lambda && zip ../lambda.zip handler.py
deploy:
	terraform -chdir=terraform init && terraform -chdir=terraform apply
