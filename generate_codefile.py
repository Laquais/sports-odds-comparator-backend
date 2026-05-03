import os

# --- CONFIGURATION ---
# Les extensions que vous voulez inclure dans le contexte
EXTENSIONS_ACCEPTEES = {'.py', '.vue', '.js', '.sql', '.html', '.css'}

# Les dossiers à bannir absolument
DOSSIERS_EXCLUS = {'venv', 'node_modules', '.git', '__pycache__', '.idea', '.vscode', 'dist', 'build'}

# Nom du fichier de sortie


def est_fichier_texte(filepath):
    """Vérifie si le fichier a une extension acceptée."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in EXTENSIONS_ACCEPTEES


def generer_contexte():
    root_dir = os.getcwd()  # Dossier courant

    with open(FICHIER_SORTIE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"--- PROJET EXPORTÉ LE {os.path.basename(root_dir)} ---\n")
        outfile.write("Voici l'intégralité du code source du projet. \n")
        outfile.write("Utilise ce contexte pour répondre aux questions.\n\n")

        count = 0

        # Parcours récursif des dossiers
        for root, dirs, files in os.walk(root_dir):
            # Filtrer les dossiers exclus (modification in-place de dirs)
            dirs[:] = [d for d in dirs if d not in DOSSIERS_EXCLUS]

            for file in files:
                filepath = os.path.join(root, file)

                if est_fichier_texte(filepath) and file != FICHIER_SORTIE and file != os.path.basename(__file__):
                    rel_path = os.path.relpath(filepath, root_dir)
                    print(f"Ajout de : {rel_path}")

                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            contenu = infile.read()

                            # On formate le header pour que Gemini comprenne bien la séparation
                            outfile.write(f"\n{'=' * 50}\n")
                            outfile.write(f"FICHIER : {rel_path}\n")
                            outfile.write(f"{'=' * 50}\n")
                            outfile.write(contenu)
                            outfile.write("\n")
                            count += 1
                    except Exception as e:
                        print(f"Erreur de lecture sur {rel_path}: {e}")

    print(f"\n✅ Terminé ! {count} fichiers fusionnés dans '{FICHIER_SORTIE}'.")
    print("👉 Il ne vous reste plus qu'à uploader ce fichier .txt dans AI Studio.")


if __name__ == "__main__":
    generer_contexte()