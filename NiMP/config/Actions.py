import os
import sys
import subprocess

from NiMP.config.DefaultEnv import default_env
from NiMP.utils.commands import run_command
from dotenv import dotenv_values

def usage():
    """Affiche le message d'aide."""
    script_name = os.path.basename(__file__)
    print("----------------------------------------------------")
    print(" Wrapper de gestion pour l'environnement Docker (Python)")
    print("----------------------------------------------------")
    print(f"Usage: ./{script_name} <commande> [options]")
    print("")
    print("Commandes principales :")
    print("  start           🚀 Démarrer les conteneurs en arrière-plan.")
    print("  stop            🛑 Arrêter les conteneurs.")
    print("  restart         🔄 Redémarrer les conteneurs.")
    print("  build           🛠️  Reconstruire les images Docker (sans cache).")
    print("  logs [service]  📜 Afficher les logs (ex: ./manage.py logs php).")
    print("")
    print("Utilitaires :")
    print("  shell [service] 💻 Entrer dans un conteneur (php par défaut).")
    print("  composer [...]  📦 Exécuter une commande Composer (ex: ./manage.py composer install).")
    print("  clean           🧹 Supprimer les conteneurs ET les volumes de données.")
    print("  backup          📥 Crée une archive 'backup.tar.gz' des fichiers de config.")
    print("  restore         📤 Restaure les fichiers de config depuis 'backup.tar.gz'.")
    print("----------------------------------------------------")

def action_start(command_args: list[str], env = dict[str, str]):  # pyright: ignore[reportUnusedParameter]
    print("🚀 Démarrage des conteneurs...")
    run_command(["docker-compose", "up", "-d"], env)
    web_port = env.get('WEB_PORT', '8080') # Utilise 8080 si WEB_PORT n'est pas défini
    ssl_port = env.get('SSL_PORT', '8443') # Utilise 8443 si SSL_PORT n'est pas défini
    print(f"✅ Environnement démarré sur:\n\t- http://localhost:{web_port}\n\t- https://localhost:{ssl_port}")
    return 0;

def action_stop(command_args: list[str], env = dict[str, str] | None):
    print("🛑 Arrêt des conteneurs...")
    run_command(["docker-compose", "down"], env=env)
    return 0;

def action_restart(command_args: list[str], env = dict[str, str] | None):
    print("🔄 Redémarrage des conteneurs...")
    action_stop()
    action_start(env)
    return 0;

def action_build(command_args: list[str], env = dict[str, str] | None):
    print("🛠️  Reconstruction des images...")
    run_command(["docker-compose", "build", "--no-cache"], env)
    return 0;

def action_logs(command_args: list[str], env = dict[str, str] | None):
    print("📜 Affichage des logs en direct (Ctrl+C pour quitter)...")
    # On passe directement la main à docker-compose, pas besoin de 'run_command'
    try:
        subprocess.run(["docker-compose", "logs", "-f"] + command_args, env)
    except KeyboardInterrupt:
        print("\nArrêt de l'affichage des logs.")
    return 0;

def action_shell(command_args: list[str], env = dict[str, str] | None):
    service = command_args[0] if command_args else "php"
    print(f"💻 Connexion au shell du conteneur '{service}'...")
    # os.execvp remplace le processus Python par le shell, pour une meilleure interactivité
    os.execvpe("docker-compose", ["docker-compose", "exec", service, "sh"], env)
    return 0;

def action_composer(command_args: list[str], env = dict[str, str] | None):
    if not command_args:
        print("❌ Erreur: Veuillez spécifier une commande Composer.")
        print("Exemple: ./manage.py composer install")
        sys.exit(1)
    print(f"📦 Exécution de 'composer {' '.join(command_args)}' dans le conteneur php...")
    run_command(["docker-compose", "exec", "php", "composer"] + command_args, env)
    return 0;

def action_clean(command_args: list[str], env = dict[str, str] | None):
    confirm = input("🤔 Êtes-vous sûr de vouloir tout supprimer (conteneurs ET données) ? [o/N] ")
    if confirm.lower() == 'o':
        print("🧹 Nettoyage complet de l'environnement...")
        run_command(["docker-compose", "down", "-v", "--remove-orphans"])
        print("✅ Nettoyage terminé.")
    else:
        print("Opération annulée.")
    return 0;

def action_backup(command_args: list[str], env = dict[str, str] | None):
    print("📥 Sauvegarde des fichiers de configuration...")
    files_to_backup = ['.env', 'etc/', 'www/'] # Adaptez cette liste à vos besoins
    existing_files = [f for f in files_to_backup if os.path.exists(f)]
    if not existing_files:
        print("⚠️ Aucun fichier de configuration à sauvegarder n'a été trouvé.")
        sys.exit(1)
    run_command(["tar", "czvf", "backup.tar.gz"] + existing_files)
    print("✅ Sauvegarde créée dans 'backup.tar.gz'.")
    return 0;

def action_restore(command_args: list[str], env = dict[str, str] | None):
    if not os.path.exists('backup.tar.gz'):
        print("❌ Le fichier 'backup.tar.gz' n'existe pas.")
        sys.exit(1)
    print("📤 Restauration des fichiers de configuration...")
    run_command(["tar", "xzvf", "backup.tar.gz"])
    print("✅ Fichiers restaurés depuis l'archive.")
    return 0;

def action_usage(command_args: list[str], env = dict[str, str] | None):
    usage()
    return 1;

def run_action(command: str, args: list[str]) -> int:
# Charge les variables du .env
    env = dotenv_values(".env")
    for key in default_env:
        if not key in env:
            env[key] = default_env[key]
    fptr = {
        "start":    action_start,
        "stop":     action_stop,
        "restart":  action_restart,
        "build":    action_build,
        "logs":     action_logs,
        "shell":    action_shell,
        "composer": action_composer,
        "clean":    action_clean,
        "backup":   action_backup,
        "restore":  action_restore,
        "":         action_usage
    };
    return (fptr.get(command, ""))(args, env=env)