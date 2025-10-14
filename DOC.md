# NiMP Documentation

## Table of Contents

1. [API Reference](#api-reference)
2. [Architecture Overview](#architecture-overview)
3. [Configuration Reference](#configuration-reference)
4. [Docker Services](#docker-services)
5. [Python Package Structure](#python-package-structure)
6. [Command Line Interface](#command-line-interface)
7. [Development Guide](#development-guide)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## API Reference

### Python Package API

#### NiMP.controller.Core.Handler

```python
class Handler:
    """
    Core handler class for NiMP operations.
    Currently minimal implementation - placeholder for future functionality.
    """
    truediv  # Placeholder attribute
```

#### NiMP.config.Constants

```python
class Constants:
    """
    Application constants and version information.
    """
    version: str = "0.9.5"  # Current version of NiMP
```

#### NiMP.utils.commands.run_command

```python
def run_command(command: list[str], env: dict[str, str] | None = None, **kwargs) -> None:
    """
    Execute a system command and handle errors.
    
    Args:
        command: List of command arguments to execute
        env: Environment variables dictionary
        **kwargs: Additional subprocess arguments
    
    Raises:
        SystemExit: On command execution failure or FileNotFoundError
    """
```

### Environment Configuration API

#### Default Environment Variables

```python
default_env = {
    'PHP_VERSION': '7.4',
    'NGINX_VERSION': '1.20', 
    'MYSQL_VERSION': '5.7'
}
```

#### Environment Variable Schema

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LAB_WEB` | string | `nimp_web` | Web container name |
| `LAB_PHP` | string | `nimp_php` | PHP container name |
| `LAB_DB` | string | `nimp_db` | Database container name |
| `LAB_NET` | string | `nimp_network` | Docker network name |
| `WEB_PORT` | string | `8080` | HTTP port |
| `SSL_PORT` | string | `8443` | HTTPS port |
| `DB_PORT` | string | `3306` | MySQL port |
| `DB_NAME` | string | `nimp_db` | Database name |
| `DB_USER` | string | `nimp_user` | Database username |
| `DB_PASS` | string | `nimp_password` | Database password |
| `DB_ROOT_PASSWORD` | string | `root_password` | MySQL root password |
| `PHP_VERSION` | string | `7.4` | PHP version tag |
| `NGINX_VERSION` | string | `1.20` | Nginx version tag |
| `MYSQL_VERSION` | string | `5.7` | MySQL version tag |

---

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   PHP-FPM       │    │   MySQL         │
│   (Port 8080)   │◄──►│   (Port 9000)   │◄──►│   (Port 3306)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Network: nimp_network                │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **HTTP Request** → Nginx (Port 8080)
2. **PHP Processing** → PHP-FPM (Port 9000) via FastCGI
3. **Database Query** → MySQL (Port 3306)
4. **Response** → Nginx → Client

### Volume Mounts

```
Host System                    Container
├── ./var/www              →   /var/www/html (Web files)
├── ./var/mysql            →   /var/lib/mysql (Database)
├── ./etc/nginx            →   /etc/nginx (Nginx config)
├── ./etc/php              →   /usr/local/etc/php (PHP config)
└── ./etc/mysql            →   /etc/mysql (MySQL config)
```

---

## Configuration Reference

### Docker Compose Services

#### Web Service (Nginx)

```yaml
web:
  image: nginx:${NGINX_VERSION}-alpine
  container_name: ${LAB_WEB}
  restart: unless-stopped
  tty: true
  ports:
    - ${WEB_PORT}:80
    - ${SSL_PORT}:443
  volumes:
    - ./var/www:/var/www/html
    - ./etc/nginx:/etc/nginx/
  environment:
    - NGINX_ENTRYPOINT_QUIET_LOGS=1
    - NGINX_PORT=${WEB_PORT}
  depends_on:
    - php
    - db
  networks:
    - internal-net
```

#### PHP Service (PHP-FPM)

```yaml
php:
  build:
    context: .
    dockerfile: ./NiMP/DockerPHP
  image: php:${PHP_VERSION}-fpm-alpine
  container_name: ${LAB_PHP}
  restart: unless-stopped
  tty: true
  working_dir: /var/www/html/
  volumes:
    - ./var/www:/var/www/html
    - ./etc/php/php:/usr/local/etc/php
    - ./etc/php/php-fpm.d:/usr/local/etc/php-fpm.d
    - ./etc/php/php-fpm.conf:/usr/local/etc/php-fpm.conf
  environment:
    DB_NAME: ${DB_NAME}
    DB_USER: ${DB_USER}
    DB_PASS: ${DB_PASS}
    SERVICE_NAME: app
    SERVICE_TAGS: dev
  networks:
    - internal-net
```

#### Database Service (MySQL)

```yaml
db:
  image: mysql:${MYSQL_VERSION}
  container_name: ${LAB_DB}
  restart: unless-stopped
  tty: true
  ports:
    - ${DB_PORT}:3306
  environment:
    MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    DB_NAME: ${DB_NAME}
    DB_USER: ${DB_USER}
    DB_PASS: ${DB_PASS}
    SERVICE_TAGS: dev
    SERVICE_NAME: mysql
  volumes:
    - ./var/mysql:/var/lib/mysql
    - ./etc/mysql/my.cnf:/etc/my.cnf
  networks:
    - internal-net
```

### Nginx Configuration

#### Main Configuration (`etc/nginx/nginx.conf`)

```nginx
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    sendfile on;
    keepalive_timeout 65;
    
    include /etc/nginx/conf.d/*.conf;
}
```

#### Virtual Host (`etc/nginx/conf.d/default.conf`)

```nginx
server {
    listen       80;
    listen  [::]:80;
    index index.php index.html;
    server_name localhost;
    error_log  /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
    root /var/www/html;

    location / {
        try_files $uri $uri/ @rewriteapp;

        # PHP processing, make sure to use your own upstream name if different
        location ~ \.php(/|$) {
            include fastcgi.conf;
            fastcgi_split_path_info ^(.+\.php)(/.*)$;
            fastcgi_param PATH_INFO $fastcgi_path_info;
            fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
            fastcgi_param DOCUMENT_ROOT $realpath_root;
            try_files $uri $uri/ /app.php$is_args$args;
            fastcgi_pass php:9000;
            fastcgi_intercept_errors on;    
        }
    }

    location @rewriteapp {
        rewrite ^(.*)$ /app.php/$1 last;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

### PHP-FPM Configuration

#### Main Configuration (`etc/php/php-fpm.conf`)

Key sections:
- Global options and process management
- Pool definitions for PHP-FPM workers
- Logging and error handling configuration
- Performance tuning parameters

#### Pool Configuration (`etc/php/php-fpm.d/www.conf`)

```ini
[www]
user = www-data
group = www-data
listen = 9000
listen.owner = www-data
listen.group = www-data
listen.mode = 0660

pm = dynamic
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35
```

### MySQL Configuration

#### Configuration File (`etc/mysql/my.cnf`)

```ini
[mysqld]
skip-host-cache
skip-name-resolve
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
secure-file-priv=/var/lib/mysql-files
user=mysql
symbolic-links=0

[client]
socket=/var/run/mysqld/mysqld.sock
```

---

## Docker Services

### Service Dependencies

```
web (Nginx)
├── depends_on: php, db
└── ports: 80, 443

php (PHP-FPM)
├── build: DockerPHP
├── working_dir: /var/www/html
└── ports: 9000 (internal)

db (MySQL)
├── ports: 3306
└── volumes: mysql data
```

### Network Configuration

```yaml
networks:
  internal-net:
    driver: bridge
    name: ${LAB_NET}
```

### Volume Configuration

- **Web Files**: `./var/www:/var/www/html`
- **MySQL Data**: `./var/mysql:/var/lib/mysql`
- **Nginx Config**: `./etc/nginx:/etc/nginx`
- **PHP Config**: `./etc/php:/usr/local/etc/php`
- **MySQL Config**: `./etc/mysql:/etc/mysql`

---

## Python Package Structure

### Package Layout

```
NiMP/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point with error handling
├── controller/              # CLI controller logic
│   ├── Core.py             # Core handler class
│   └── Start.py            # Main CLI entry point
├── config/                  # Configuration management
│   ├── Actions.py          # Command action definitions
│   ├── Constants.py        # Application constants
│   └── DefaultEnv.py       # Default environment variables
├── utils/                   # Utility functions
│   └── commands.py         # Command execution utilities
└── docker/                  # Docker-related files
    ├── DockerNginx         # Nginx Dockerfile (empty)
    └── DockerPHP           # PHP Dockerfile (empty)
```

### Module Dependencies

```
NiMP
├── docker (7.1.0)          # Docker Python SDK
├── python-dotenv (1.1.1)   # Environment variable loading
├── GitPython (3.1.43)      # Git repository operations
└── argcomplete (3.5.0)     # Bash completion support
```

---

## Command Line Interface

### CLI Entry Point

The CLI is accessible through the `nimp` executable script:

```bash
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from NiMP.controller.Start import main

if __name__ == '__main__':
    exit(main())
```

### Command Structure

```python
def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
```

### Available Commands

#### Container Management Commands

| Command | Function | Description |
|---------|----------|-------------|
| `start` | `action_start()` | Start all containers in detached mode |
| `stop` | `action_stop()` | Stop all containers |
| `restart` | `action_restart()` | Restart all containers |
| `build` | `action_build()` | Rebuild images without cache |

#### Development Commands

| Command | Function | Description |
|---------|----------|-------------|
| `shell [service]` | `action_shell()` | Enter container shell |
| `logs [service]` | `action_logs()` | View container logs |
| `composer [...]` | `action_composer()` | Run Composer commands |

#### Maintenance Commands

| Command | Function | Description |
|---------|----------|-------------|
| `clean` | `action_clean()` | Remove containers and volumes |
| `backup` | `action_backup()` | Backup configuration files |
| `restore` | `action_restore()` | Restore from backup |

### Command Implementation Details

#### Start Command

```python
def action_start(command_args: list[str], env: dict[str, str]) -> int:
    """
    Start all containers in detached mode.
    
    Args:
        command_args: Unused command arguments
        env: Environment variables dictionary
        
    Returns:
        int: Exit code (0 for success)
    """
    print("🚀 Démarrage des conteneurs...")
    run_command(["docker-compose", "up", "-d"], env)
    web_port = env.get('WEB_PORT', '8080')
    ssl_port = env.get('SSL_PORT', '8443')
    print(f"✅ Environnement démarré sur:\n\t- http://localhost:{web_port}\n\t- https://localhost:{ssl_port}")
    return 0
```

#### Shell Command

```python
def action_shell(command_args: list[str], env: dict[str, str]) -> int:
    """
    Enter container shell.
    
    Args:
        command_args: Service name (default: 'php')
        env: Environment variables dictionary
        
    Returns:
        int: Exit code (0 for success)
    """
    service = command_args[0] if command_args else "php"
    print(f"💻 Connexion au shell du conteneur '{service}'...")
    os.execvpe("docker-compose", ["docker-compose", "exec", service, "sh"], env)
    return 0
```

#### Composer Command

```python
def action_composer(command_args: list[str], env: dict[str, str]) -> int:
    """
    Execute Composer commands in PHP container.
    
    Args:
        command_args: Composer command arguments
        env: Environment variables dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    if not command_args:
        print("❌ Erreur: Veuillez spécifier une commande Composer.")
        print("Exemple: ./manage.py composer install")
        sys.exit(1)
    print(f"📦 Exécution de 'composer {' '.join(command_args)}' dans le conteneur php...")
    run_command(["docker-compose", "exec", "php", "composer"] + command_args, env)
    return 0
```

### Error Handling

The CLI includes comprehensive error handling:

1. **Missing Dependencies**: Checks for required Python packages
2. **Git Missing**: Validates Git installation for GitPython
3. **Missing .env**: Validates environment configuration file
4. **Command Execution**: Handles subprocess errors and failures
5. **Keyboard Interrupt**: Graceful handling of Ctrl+C

---

## Development Guide

### Setting Up Development Environment

1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd NiMP
   pip install -r requirements.txt
   ```

2. **Create .env File**:
   ```bash
   cp .env.example .env  # If available
   # Or create manually with required variables
   ```

3. **Test Installation**:
   ```bash
   ./nimp  # Should display usage information
   ```

### Adding New Commands

1. **Define Action Function** in `NiMP/config/Actions.py`:
   ```python
   def action_newcommand(command_args: list[str], env: dict[str, str]) -> int:
       """New command implementation."""
       print("🆕 Executing new command...")
       # Implementation here
       return 0
   ```

2. **Register Command** in `run_action()` function:
   ```python
   fptr = {
       # ... existing commands ...
       "newcommand": action_newcommand
   }
   ```

3. **Update Usage Documentation**:
   ```python
   def usage():
       print("  newcommand     🆕 Description of new command")
   ```

### Extending Configuration

1. **Add Environment Variables** to `DefaultEnv.py`:
   ```python
   default_env = {
       # ... existing variables ...
       'NEW_VARIABLE': 'default_value'
   }
   ```

2. **Update Docker Compose** to use new variables
3. **Document in CLI help** and README

### Testing Commands

```bash
# Test individual commands
./nimp start
./nimp logs
./nimp shell php

# Test error conditions
./nimp nonexistent  # Should show usage
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Port Already in Use

**Error**: `Port 8080 is already in use`

**Solution**:
```bash
# Check what's using the port
lsof -i :8080
# Or on Windows
netstat -ano | findstr :8080

# Change port in .env file
echo "WEB_PORT=8081" >> .env
./nimp restart
```

#### 2. Permission Denied on Volumes

**Error**: `Permission denied` when accessing mounted volumes

**Solution** (Linux/macOS):
```bash
# Fix ownership
sudo chown -R $USER:$USER var/
sudo chown -R $USER:$USER etc/

# Or fix permissions
chmod -R 755 var/
chmod -R 644 etc/
```

#### 3. Container Won't Start

**Error**: Containers fail to start or exit immediately

**Solution**:
```bash
# Check logs
./nimp logs

# Check Docker status
docker ps -a
docker-compose ps

# Clean and rebuild
./nimp clean
./nimp build
./nimp start
```

#### 4. MySQL Connection Issues

**Error**: `Can't connect to MySQL server`

**Solution**:
```bash
# Check MySQL container status
./nimp logs db

# Verify environment variables
cat .env | grep DB_

# Test connection
./nimp shell db
mysql -u nimp_user -p nimp_db
```

#### 5. PHP-FPM Connection Issues

**Error**: `502 Bad Gateway` or PHP not processing

**Solution**:
```bash
# Check PHP container
./nimp logs php

# Test PHP-FPM
./nimp shell php
php-fpm -t  # Test configuration

# Check Nginx configuration
./nimp shell web
nginx -t
```

### Debugging Commands

#### Container Debugging

```bash
# Check all container status
docker-compose ps

# View detailed logs
docker-compose logs -f --tail=100

# Check container resources
docker stats

# Inspect container
docker inspect nimp_php
```

#### Network Debugging

```bash
# Check Docker networks
docker network ls
docker network inspect nimp_network

# Test connectivity
./nimp shell web
ping php
ping db
```

#### Volume Debugging

```bash
# Check volume mounts
docker-compose config

# Inspect volumes
docker volume ls
docker volume inspect <volume_name>
```

### Performance Issues

#### Slow Container Startup

**Causes**:
- Large image downloads
- Volume mount issues
- Resource constraints

**Solutions**:
```bash
# Use cached images
docker-compose pull

# Check available resources
docker system df
docker system prune  # Clean up unused resources
```

#### High Memory Usage

**Monitoring**:
```bash
# Check container resource usage
docker stats

# Monitor system resources
htop  # or top
```

**Optimization**:
- Reduce PHP-FPM workers in `www.conf`
- Optimize MySQL configuration in `my.cnf`
- Use Alpine-based images for smaller footprint

### Log Analysis

#### Nginx Logs

```bash
# Access logs
./nimp shell web
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

#### PHP-FPM Logs

```bash
# PHP-FPM logs
./nimp logs php

# PHP error logs
./nimp shell php
tail -f /usr/local/var/log/php-fpm.log
```

#### MySQL Logs

```bash
# MySQL logs
./nimp logs db

# MySQL error log
./nimp shell db
tail -f /var/log/mysql/error.log
```

---

## API Examples

### Environment Configuration Example

```python
# .env file example
LAB_WEB=nimp_web
LAB_PHP=nimp_php
LAB_DB=nimp_db
LAB_NET=nimp_network

WEB_PORT=8080
SSL_PORT=8443
DB_PORT=3306

DB_NAME=nimp_db
DB_USER=nimp_user
DB_PASS=secure_password_123
DB_ROOT_PASSWORD=root_password_456

PHP_VERSION=7.4
NGINX_VERSION=1.20
MYSQL_VERSION=5.7
```

### Command Usage Examples

```bash
# Start environment
./nimp start

# View logs for specific service
./nimp logs php
./nimp logs db

# Access PHP container
./nimp shell php
./nimp shell db
./nimp shell web

# Run Composer commands
./nimp composer install
./nimp composer update
./nimp composer dump-autoload

# Maintenance
./nimp backup
./nimp restore
./nimp clean
```

### Python API Usage

```python
# Load environment variables
from dotenv import dotenv_values
from NiMP.config.DefaultEnv import default_env

env = dotenv_values(".env")
for key in default_env:
    if key not in env:
        env[key] = default_env[key]

# Execute commands
from NiMP.utils.commands import run_command

run_command(["docker-compose", "up", "-d"], env)
```

---

## Security Considerations

### Environment Security

1. **Secure Passwords**: Use strong, unique passwords in `.env`
2. **File Permissions**: Restrict access to configuration files
3. **Network Isolation**: Use internal Docker networks
4. **Regular Updates**: Keep base images updated

### Production Considerations

1. **SSL/TLS**: Configure proper SSL certificates
2. **Firewall**: Restrict port access
3. **Monitoring**: Implement logging and monitoring
4. **Backups**: Regular database and configuration backups

---

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Update documentation
5. Submit pull request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Test commands before submitting

### Documentation Updates

- Update README.md for user-facing changes
- Update DOC.md for API changes
- Add examples for new features
- Keep troubleshooting guide current
