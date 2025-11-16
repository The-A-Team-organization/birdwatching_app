ansible-playbook:
	ANSIBLE_HOST_KEY_CHECKING=False \
	ansible-playbook -i $(ANSIBLE_INVENTORY) $(ANSIBLE_PLAYBOOK) --private-key=private_key_web1 --extra-vars "db_user=$(DB_USER) db_password=$(DB_PASS) db_name=$(DB_NAME) db_host=$(DB_HOST) db_port=$(DB_PORT) app_port=$(APP_PORT) secret_key=$(SECRET_KEY) s3_bucket=$(S3_BUCKET) s3_region=$(S3_REGION) app_user=$(APP_USER) app_dir=$(APP_DIR) app_name=$(APP_NAME)" 
