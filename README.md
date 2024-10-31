# Navigation
- [Installation](#installation)
- [Front-end Development](#front-end-development)
- [Datasets Upload](#datasets-upload)
- [Datasets Update](#datasets-update)

## Installation

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
`vi .ddev/config.yaml`
and add:
```
router_http_port: "8080"
router_https_port: "8443"
bind_all_interfaces: true
```

```
// get a local url
ddev drush uli
// get a external url
ddev drush uli | sed "s|https://get-dkan.ddev.site|http://$(curl -s ifconfig.me):8080|g"
ddev launch
```

### Set up the flask proxy

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
