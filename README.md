# Navigation
- [Installation](#installation)
- [Front-end Development](#front-end-development)
- [Datasets Upload](#datasets-upload)
- [Datasets Update](#datasets-update)

## Installation
We are using a virtual machine instance with Debian 12 (Bookworm) as the operating system. The instance is configured with 8 vCPUs and 32 GB of memory (RAM).

### Environment (Not minimum requirement; only my local setup)
- <a href="https://getcomposer.org/doc/00-intro.md#installation-linux-unix-osx" target="_blank">Installing Composer</a>
- <a href="https://ddev.readthedocs.io/en/latest/users/install/ddev-installation/" target="_blank">Installing DDEV</a>
- <a href="https://ddev.readthedocs.io/en/latest/users/install/docker-installation/" target="_blank">Installing Docker</a>
```
MySQL: 8.4.2
PHP: 8.3.11
Apache: 2.4.59
Node: 22.8.0
```
### Build DKAN BACKEND

```
ddev start
ddev composer install
ddev dkan-site-install
```

### Build DKAN FRONTEND
```
ddev dkan-frontend-install
```
Enter **N** for the following prompt:

**replace docroot/data-catalog-app-1.6.2/.circleci/config.yml? [y]es, [n]o, [A]ll, [N]one, [r]ename:**
```
ddev dkan-frontend-build
```

### Enable Cron Jobs
```
ddev drush cron
```

### Login as the admin user and launch the application

```
sudo usermod -aG docker $USER
newgrp docker
sudo chown -R $USER:$USER /home/get-dkan
```


```
// get a local url
ddev drush uli
// get a external url
ddev drush uli | sed "s|https://get-dkan.ddev.site|http://$(curl -s ifconfig.me):8080|g"
ddev launch
```
### Enable visualization feature
```
composer require 'drupal/dkan_chart:1.0.x-dev@dev' --ignore-platform-req=ext-zip
ddev drush cache-rebuild
ddev drush en  clipboardjs  -y
ddev drush en dkan_chart -y
ddev drush en dkan_tables -y
```

### Flask Proxy
Requirement
```
Python Version 3.7 or later.
```
Environment Setup
```
pip install Flask
pip install flask-restx
```
Proxy Execution
```
docker exec -it ddev-get-dkan-web /bin/bash
setsid /venv/bin/python proxy.py &
```

### Generate certificates locally

```
mkcert 127.0.0.1 localhost
```

## Front-end Development
```
git pull
ddev dkan-frontend-build
```

## Datasets Upload

```
ddev drush queue:list
ddev drush queue:run localize_import
ddev drush queue:run datastore_import
ddev drush queue:run post_import
```

## Datasets Update

```
ddev drush queue:list
ddev drush queue:run resource_purger
ddev drush queue:run orphan_reference_processor
```
