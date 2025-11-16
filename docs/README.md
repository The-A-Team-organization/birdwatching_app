# Vagrant Setup

This repository contains a Vagrantfile for setting up a virtual machine using VirtualBox. The environment includes PostgreSQL, Flask web servers, and a load balancer. It is designed for development and testing, with private networks, port forwarding, host management using the vagrant-hostmanager plugin, and the vagrant-ansible_inventory plugin connected to create an inventory.ini file for further use.

## Overview

Base Box: Bento Ubuntu 24.04 (bento/ubuntu-24.04)
Synced Folder: ./storage on host is synced to /vagrant/storage on guests (owned by vagrant:vagrant).
Host Management: Enabled via vagrant-hostmanager for automatic /etc/hosts updates on host and guests.
VMs Provisioned:
-1 Database VM (dbpostgresql)
-2 Web Servers (flaskserver1, flaskserver2)
-1 Load Balancer (loadbalancing)
Ansible Groups:
-db: [dbpostgresql]
-web: [flaskserver1, flaskserver2]
-lb: [loadbalancing]

## Requirements

Vagrant (version 2.4.7)
VirtualBox (version 7.1.4)
Vagrant plugin: vagrant-hostmanager, vagrant-ansible_inventory

## Installation and Setup

1. Clone the Repository:

```bash
git clone <repository-url>
cd BirdWatchingFlask/Vagrant/Vagrantfile
```

2. Open Vagrantfile and configure the number of web servers: edit the web_server_amount variable in the Vagrantfile (default: 2) and run vagrant up to configure the number of Flask servers.

3. Install Required Vagrant Plugin:

```bash
vagrant plugin install vagrant-hostmanager
vagrant plugin install vagrant-ansible_inventory
```

4. Start the VMs: Run the following command:

```bash
vagrant up
```

This will download the base box if not already present.

5. Access the VMs:
   SSH access to the created virtual machine: vagrant ssh <vm_name> (e.g., vagrant ssh dbpostgresql).

# Usage plugin vagrant-ansible_inventory

Once all virtual machines have booted up, run:

```bash
vagrant ansible inventory > <path_to_folder>
```

In the shared folder with the Jenkins virtual machine on your host .\storage, you need to put the generated inventory.ini.

From the folder created in the root of Vagrantfile .\\.vagrant, move the private keys to .\storage\keys\<vm_name>\ using the path .\.vagrant\machines\<vm_name>\virtualbox\private_key

In inventory.ini, change the paths according to the paths of the shared folder on the Jenkins VM.

```bash
ansible_ssh_private_key_file=/mnt/shared/keys/<vm_name>/private_key
```

## Inventory Example

inventory.ini should look like this:

```bash
[lb]
loadbalancing ansible_host=loadbalancing ansible_port=22 ansible_user=vagrant ansible_ssh_private_key_file=/mnt/shared/keys/loadbalancing/private_key

[db]
dbpostgresql ansible_host=dbpostgresql ansible_port=22 ansible_user=vagrant ansible_ssh_private_key_file=/mnt/shared/keys/dbpostgresql/private_key

[web]
flaskserver1 ansible_host=flaskserver1 ansible_port=22 ansible_user=vagrant ansible_ssh_private_key_file=/mnt/shared/keys/flaskserver1/private_key
flaskserver2 ansible_host=flaskserver2 ansible_port=22 ansible_user=vagrant ansible_ssh_private_key_file=/mnt/shared/keys/flaskserver2/private_key
```

ansible_host can be either a domain or an IP address.

# Jenkins & Ansible Setup for BirdWatchingFlask

This guide explains how to run all Ansible playbooks using Jenkins locally.

## Requirements

- A virtual machine with:
  - Jenkins installed
  - Make
  - Ansible
- A shared folder /mnt/shared/ containing:
  - inventory.ini file
  - keys folder with 4 subfolders: dbpostgresql, flaskserver1, flaskserver2, loadbalancing
  - Each subfolder contains the private key for the corresponding VM

## Tested Versions

The setup was tested with the following tool versions:

- Ansible: 2.18.9
- Make: 4.3
- Jenkins: 2.516.3

## Jenkins Plugins Required

Ansible plugin
GitHub plugin
Pipeline
SSH Agent Plugin

## Jenkins Credentials

Create the following credentials in Jenkins (all under System -> Global credentials):

Type ID / Name Description
SSH Username with private key Git_user_ssh Git access
Secret text DB_PASS Database password
Secret text DB_NAME Database name
Secret text DB_USER Database user
Secret text DB_HOST Database host
Secret text DB_PORT Database port
Secret text SECRET_KEY Flask secret key
Secret text APP_PORT Flask app port
Secret text NGINX_LB_PORT Nginx load balancer port
Secret text UPLOAD_FOLDER Flask upload folder

## Creating Jenkins Pipelines

1. Go to New Item in Jenkins.

2. Name the pipeline exactly as the corresponding file:

```bash
JenkinsFile.DataBase
JenkinsFile.nginxLB
JenkinsFile.webservers
```

3. Select Pipeline as the item type and click OK.

4. In Pipeline Definition, select Pipeline script from SCM:

SCM: Git

Repository URL: git@github.com:Maars-Team/BirdWatching.git

Credentials: select your Git SSH credentials

Branch Specifier: \*/main

Script Path: select the corresponding file:

BirdWatchingFlask/JenkinsAndAnsible/Jenkins/JenkinsFile.DataBase

BirdWatchingFlask/JenkinsAndAnsible/Jenkins/JenkinsFile.nginxLB

BirdWatchingFlask/JenkinsAndAnsible/Jenkins/JenkinsFile.webservers

5. Click Build Now.

## Verify Deployment

Once the pipeline builds successfully, you can access the site via the load balancer to verify that everything works correctly.

# Flask Web Application

This is a simple web application that allows users to upload images of birds and view them in a gallery.<br>
Everyone can edit their own images. For better security users can report ip addresses of malicious users, <br>
especially hunters and users with a bad reputation.<br>
App also allows admins to delete images and edit them in the admins' dashboard.

## Requirements

- flask>=2.3.0
- psycopg2-binary>=2.9.0
- flask-bcrypt>=1.0.1
- werkzeug>=2.3.0
- gunicorn==22.0.0
- flask-sqlalchemy>=3.1.1
- flask_login>=0.6.3
- boto3>=1.40.45

## Environment Configuration

Required environment variables:

- SECRET_KEY: Flask secret key for sessions
- DB_NAME: Database name
- DB_USER: Database username
- DB_PASSWORD: Database password
- DB_HOST: Database host
- DB_PORT: Database port
- S3_BUCKET: name of the S3 bucket
- S3_REGION: region of the S3 bucket

## Overview Bird Watching Flask

This Flask application provides a comprehensive platform for bird enthusiasts to:

- Share bird photographs with location data
- Browse community gallery
- Manage personal photo collections
- Report malicious users (hunters)
- Admin dashboard for content management

## Features

### User Features

- User registration and authentication
- Upload bird photos with location information
- View community gallery
- Personal dashboard with user's photos
- Edit photo locations
- Delete own photos
- Report hunter IP addresses

### Admin Features

- Admin dashboard with all photos
- Delete any photo
- Edit any photo location
- View photo authors
- Full content management

### Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- Hunter IP blocking with hashed storage
- CSRF protection through Flask sessions

## Architecture

The application follows a modular Blueprint structure:

```bash
/
├── main.py                 # Application entry point
├── models/                 # Database models
│   └── models.py
├── login/                  # Authentication module
│   ├── login_register.py
│   └── templates/
├── images/                 # Photo management module
│   ├── photo_uploader.py
│   └── templates/
├── dashboard/              # User/Admin dashboards
│   ├── dashboard.py
│   └── templates/
├── utils/                  # Utilities and decorators
│   └── decorators.py
└── static/                 # CSS and static assets
```

## Authentication & Authorization

### Session Management

- Users authenticate via username/password
- Sessions store: loggedin, id, username, role
- Two roles: user (default) and admin

### Decorators

- @login_required: Ensures user is authenticated
- @admin_required: Restricts access to admin users only

## Database Models

### User Model

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255))  # Hashed
    role = db.Column(db.String(20), default='user')
```

### BirdPictures Model

```python
class BirdPictures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

### HunterIP Model

```python
class HunterIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipaddr = db.Column(db.String(255), unique=True, nullable=False)  # Hashed
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
```

## Security Features

### IP Blocking System

- Users can report hunter IP addresses
- IPs are stored as hashes for privacy
- Blocked IPs are redirected to Ukrainian hunting law information
- Uses X-Forwarded-For header support for proxy environments

### Password Security

- All passwords are hashed using Werkzeug's generate_password_hash()
- Secure password verification with check_password_hash()

### File Upload Security

- Filename sanitization with secure_filename()
- File type validation (only image formats)
- Files stored outside web root
