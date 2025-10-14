import sys
import subprocess

def run_command(command: str, env = dict[str, str] | None, **kwargs):
    """Exécute une commande système et gère les erreurs."""
    print(f"▶️  Exécution: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, env=env, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Erreur: 'docker-compose' n'est pas installé ou n'est pas dans le PATH.")
        sys.exit(1)