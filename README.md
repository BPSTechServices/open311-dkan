# Navigation
- [Installation](#installation)
- [Front-end Development](#front-end-development)

## Installation

### Environment (Not minimum requirement; only my local setup)
- [Installing Composer](https://getcomposer.org/doc/00-intro.md#installation-linux-unix-osx)
- [Installing DDEV](https://ddev.readthedocs.io/en/latest/users/install/ddev-installation/)
- [Installing Docker](https://ddev.readthedocs.io/en/latest/users/install/docker-installation/)
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
ddev drush uli
ddev launch
```

## Front-end Development
```
git pull
ddev dkan-frontend-build
```
