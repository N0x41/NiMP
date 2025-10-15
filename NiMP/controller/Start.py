#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

try:
    import docker # type: ignore
    import dotenv # type: ignore
    import git # type: ignore

    from NiMP.controller.Core import Handler
    from NiMP.config.Actions import action_usage, run_action

    #client = docker.from_env()
except ModuleNotFoundError as e:
    print("Mandatory dependencies are missing:", e)
    print("Please install them with python3 -m pip install --upgrade -r requirements.txt")
    exit(1)
except ImportError as e:
    print("An error occurred while loading the dependencies!")
    print()
    if "git executable" in e.msg:
        print("Git is missing in your PATH, it must be installed locally on your computer.")
        print()
    print("Details:")
    print(e)
    exit(1)
except KeyboardInterrupt:
    exit(1)

def main() -> int:
    """Fonction principale du script."""
    # Vérifie si un .env existe
    if not os.path.exists('.env'):
        print("⚠️ Fichier .env non trouvé. Veuillez en créer un (vous pouvez copier .env.example).")
        sys.exit(1)

    # Récupère la commande et les arguments
    args = sys.argv[1:]
    if not args:
        args = ['']

    command = args[0]
    command_args = args[1:]

    # --- Gestion des commandes ---
    sys.exit(run_action(command, command_args))