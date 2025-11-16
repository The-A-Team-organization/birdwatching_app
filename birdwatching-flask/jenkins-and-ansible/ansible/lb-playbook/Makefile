ansible-playbook:
	ANSIBLE_HOST_KEY_CHECKING=False \
	ansible-playbook -i $(ANSIBLE_INVENTORY) $(ANSIBLE_PLAYBOOK) --private-key=private_key_LB --extra-vars "nginxlb_port=$(NGINX_LB_PORT)"