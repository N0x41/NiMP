# NiMP - Version agnostic web development environment

[![Version](https://img.shields.io/badge/version-0.8.5-blue.svg)](https://github.com/your-username/NiMP)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)

**NiMP** is a comprehensive Python wrapper for managing a containerized web development environment using Nginx, MySQL, and PHP (with phpMyAdmin). It provides an easy-to-use CLI interface for managing Docker containers and simplifies the setup of a complete LEMP stack.

## 🚀 Features

- **Complete LEMP Stack**: Nginx, MySQL, PHP-FPM, and phpMyAdmin
- **Python CLI Interface**: Easy-to-use command-line management
- **Docker Compose Integration**: Container orchestration with hot-reload
- **Configurable Environment**: Customizable versions and settings
- **Backup & Restore**: Built-in configuration backup functionality
- **Development Ready**: Optimized for local development workflows
- **Volume Persistence**: Data persistence across container restarts

## 📋 Requirements

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Python** (3.9+)
- **Git** (for version control features)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/NiMP.git
cd NiMP
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env  # If you have an example file
# Or create manually:
```

```env
# Container Names
LAB_WEB=nimp_web
LAB_PHP=nimp_php
LAB_DB=nimp_db
LAB_NET=nimp_network

# Ports
WEB_PORT=8080
SSL_PORT=8443
DB_PORT=3306

# Database Configuration
DB_NAME=nimp_db
DB_USER=nimp_user
DB_PASS=nimp_password
DB_ROOT_PASSWORD=root_password

# Software Versions
PHP_VERSION=7.4
NGINX_VERSION=1.20
MYSQL_VERSION=5.7
```

### 4. Make the CLI Executable

```bash
chmod +x nimp
```

## 🎯 Quick Start

### Start the Environment

```bash
./nimp start
```

This will:
- Build and start all containers (Nginx, PHP-FPM, MySQL)
- Set up the network and volume mounts
- Display access URLs

### Access Your Environment

- **Web Server**: http://localhost:8080
- **HTTPS**: https://localhost:8443
- **phpMyAdmin**: http://localhost:8080/phpmyadmin
- **MySQL**: localhost:3306

### Stop the Environment

```bash
./nimp stop
```

## 📚 CLI Commands

### Container Management

```bash
./nimp start           # 🚀 Start all containers
./nimp stop            # 🛑 Stop all containers
./nimp restart         # 🔄 Restart all containers
./nimp build           # 🛠️  Rebuild images (no cache)
```

### Development Tools

```bash
./nimp shell [service] # 💻 Enter container shell (default: php)
./nimp logs [service]  # 📜 View container logs
./nimp composer [...]  # 📦 Run Composer commands
```

### Maintenance

```bash
./nimp clean           # 🧹 Remove containers and volumes
./nimp backup          # 📥 Backup configuration files
./nimp restore         # 📤 Restore from backup
```

## 🏗️ Project Structure

```
NiMP/
├── nimp                    # CLI executable
├── docker-compose.yml      # Docker services configuration
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Python project configuration
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── etc/                   # Configuration files
│   ├── nginx/             # Nginx configuration
│   ├── php/               # PHP-FPM configuration
│   └── mysql/             # MySQL configuration
├── var/                   # Runtime data
│   ├── mysql/             # MySQL data directory
│   └── www/               # Web root with phpMyAdmin
└── NiMP/                  # Python package
    ├── controller/        # CLI controller logic
    ├── config/            # Configuration management
    ├── utils/             # Utility functions
    └── docker/            # Docker-related files
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LAB_WEB` | Web container name | `nimp_web` |
| `LAB_PHP` | PHP container name | `nimp_php` |
| `LAB_DB` | Database container name | `nimp_db` |
| `LAB_NET` | Network name | `nimp_network` |
| `WEB_PORT` | HTTP port | `8080` |
| `SSL_PORT` | HTTPS port | `8443` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_NAME` | Database name | `nimp_db` |
| `DB_USER` | Database user | `nimp_user` |
| `DB_PASS` | Database password | `nimp_password` |
| `PHP_VERSION` | PHP version | `7.4` |
| `NGINX_VERSION` | Nginx version | `1.20` |
| `MYSQL_VERSION` | MySQL version | `5.7` |

### Customizing Configurations

- **Nginx**: Edit files in `etc/nginx/`
- **PHP**: Edit files in `etc/php/`
- **MySQL**: Edit `etc/mysql/my.cnf`

### Volume Mounts

- `./var/www` → `/var/www/html` (Web files)
- `./var/mysql` → `/var/lib/mysql` (Database data)
- `./etc/nginx` → `/etc/nginx` (Nginx config)
- `./etc/php` → `/usr/local/etc/php` (PHP config)
- `./etc/mysql` → `/etc/mysql` (MySQL config)

## 🔧 Development

### Adding PHP Extensions

1. Edit `NiMP/docker/DockerPHP` to add extension installation
2. Rebuild the PHP container:
   ```bash
   ./nimp build
   ```

### Custom Nginx Configuration

1. Modify `etc/nginx/conf.d/default.conf`
2. Restart the web service:
   ```bash
   ./nimp restart
   ```

### Database Management

Access the MySQL shell:
```bash
./nimp shell db
mysql -u nimp_user -p nimp_db
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8080
# Change WEB_PORT in .env file
```

**Permission denied on volumes:**
```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER var/
```

**Container won't start:**
```bash
# Check logs
./nimp logs
# Clean and rebuild
./nimp clean
./nimp build
./nimp start
```

**MySQL connection issues:**
- Ensure `DB_*` variables in `.env` match across services
- Check if MySQL container is fully started: `./nimp logs db`

### Getting Help

1. Check container logs: `./nimp logs [service]`
2. Verify environment variables in `.env`
3. Ensure Docker is running: `docker --version`
4. Check disk space: `df -h`

## 📝 TODO

- [ ] Fix MySQL socket deletion issue
- [ ] Add PHP extension installation automation
- [ ] Create configuration bootstrapper
- [ ] Add SSL certificate management
- [ ] Implement health checks
- [ ] Add database migration tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- Docker team for containerization platform
- Nginx, PHP, and MySQL communities
- Contributors and users of this project

---

**Made with ❤️ for developers who love containerized environments**