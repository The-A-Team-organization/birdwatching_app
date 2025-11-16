ansible-playbook:
	ANSIBLE_HOST_KEY_CHECKING=False \
	ansible-playbook -i $(ANSIBLE_INVENTORY) $(ANSIBLE_PLAYBOOK) --private-key=private_key_DB --extra-vars "db_user=$(DB_USER) db_password=$(DB_PASS) db_name=$(DB_NAME)"