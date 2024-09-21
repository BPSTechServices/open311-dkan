### Environment (Not minimum requirement; only my local setup)
- [Installing Composer](https://getcomposer.org/doc/00-intro.md#installation-linux-unix-osx)
- [Installing DDEV](https://ddev.readthedocs.io/en/latest/users/install/ddev-installation/)
- [Installing Docker](https://ddev.readthedocs.io/en/latest/users/install/docker-installation/)
```
DDEV: Required
Composer: Required
Docker: Required
MySQL: 8.4.2
PHP: 8.3.11
Apache: 2.4.59
Node: 22.8.0
```

### Build DKAN BACKEND

```
ddev start
composer install
ddev dkan-site-install
```

### Build DKAN FRONTEND
```
ddev dkan-frontend-install
```
Enter **N** for the following question:

**replace docroot/data-catalog-app-1.6.2/.circleci/config.yml? [y]es, [n]o, [A]ll, [N]one, [r]ename:**
```
ddev dkan-frontend-build
```

### Enable Cron Jobs
```
ddev drush cron
```