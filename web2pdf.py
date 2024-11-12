#!/usr/bin/env python

# Bibliothèques de la librairie standard
from collections import deque
from urllib.parse import urljoin, urlparse
import logging
import time
import argparse
import os
import re
import shutil

# Bibliothèques externes
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
import pdfkit

# Configurer le logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def merge_pdf_files_in_sequence(directory, output_file):
    # Liste les fichiers PDF dans le répertoire
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    # Trie les fichiers par numéro de séquence en utilisant un tri basé sur le préfixe numérique
    # pdf_files.sort(key=lambda x: int(re.match(r"^\d+", x).group()))
    pdf_files.sort(
        key=lambda x: (
            int(re.match(r"^\d{4}(?=_)", x).group())
            if re.match(r"^\d{4}_", x)
            else float("inf")
        )
    )

    # Initialise le merger pour combiner les PDF
    merger = PdfMerger()

    # Ajoute chaque fichier PDF trié dans le fichier de sortie
    for pdf_file in pdf_files:
        merger.append(os.path.join(directory, pdf_file))

    # Enregistre le fichier PDF combiné
    merger.write(output_file)
    merger.close()


def convert_to_pdf(url, output_file):

    options = {
        "page-size": "A4",
        "margin-top": "10mm",
        "margin-bottom": "10mm",
        "orientation": "Portrait",
        "header-center": "ZOWE 3.0 LTS",
        "encoding": "UTF-8",
        "zoom": 1.1,
    }
    config = pdfkit.configuration(
        wkhtmltopdf="/usr/bin/wkhtmltopdf"
    )  # Remplacez par le chemin vers wkhtmltopdf
    pdfkit.from_url(url, output_file, options=options, configuration=config)


def crawl_website(start_url, output_dir, allowed_path, test):
    # Initialiser une queue pour la navigation
    queue = deque([start_url])  # Contient uniquement l'URL de départ

    # Sets pour éviter les doublons et pour compter les URLs
    visited = set()
    url_count = 0  # Compteur d'URL trouvées
    filtered_url_count = 0  # Compteur d'URL traitées après filtrage
    failed_url_count = 0  # Compteur d'URL en échec
    ignored_file_count = (
        0  # Compteur d'URL ignorées car elles pointent vers des fichiers
    )

    # liste d'exentions de fichiers
    file_extensions = sorted(
        {
            ".7z",
            ".aac",
            ".avi",
            ".bmp",
            ".csv",
            ".doc",
            ".docx",
            ".flac",
            ".flv",
            ".gif",
            ".gz",
            ".ini",
            ".jpeg",
            ".jpg",
            ".json",
            ".md",
            ".m4a",
            ".mkv",
            ".mov",
            ".mp3",
            ".mp4",
            ".ods",
            ".odt",
            ".ogg",
            ".odp",
            ".pdf",
            ".png",
            ".ppt",
            ".pptx",
            ".rar",
            ".rtf",
            ".svg",
            ".tar",
            ".tar.bz2",
            ".tar.gz",
            ".tiff",
            ".txt",
            ".wav",
            ".webm",
            ".webp",
            ".wmv",
            ".xls",
            ".xlsx",
            ".xml",
            ".yaml",
            ".yml",
            ".zip",
        }
    )

    # Numéro de séquence utilisé comme préfixe pour les fichiers PDF générés.
    file_number = 0

    # Créer le répertoire de sortie si nécessaire
    # os.makedirs(output_dir, exist_ok=True)
    if os.path.exists(output_dir):
        # Vider le répertoire s'il existe déjà
        shutil.rmtree(output_dir)

    # Créer le répertoire vide
    os.makedirs(output_dir)

    while queue and (file_number < 3 if test else True):
        current_url = queue.popleft()

        # Ne pas traiter les URLs déjà visitées
        if current_url in visited:
            continue

        # Vérifier si l'URL se termine par une extension de fichier
        if any(current_url.endswith(ext) for ext in file_extensions):
            ignored_file_count += 1
            logging.info(f"N°:{file_number:4}, URL Ignorée:{current_url}")
            continue  # Passer à l'URL suivante

        visited.add(current_url)
        url_count += 1

        # Effectuer une requête HTTP pour récupérer le contenu de la page
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()

            content = response.text
            filtered_url_count += 1  # Compte cette URL comme traitée avec succès

            # Analyser le contenu avec BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")

            # Analyse l'URL actuelle pour extraire les composants (schéma, hôte, chemin, etc.)
            parsed_url = urlparse(current_url)

            # Récupère uniquement le chemin de l'URL et supprime tout slash final, s'il existe.
            # Cela permet d'éviter un segment de chemin vide lors de la division en parties.
            # path = parsed_url.path.rstrip("/")
            path = parsed_url.path.split("/")

            # Divise le chemin en segments de chemin en utilisant '/' comme séparateur.
            # Cela crée une liste où chaque élément représente un segment du chemin.
            # path_parts = path.split("/")

            # Incrémente le compteur de fichier pour utiliser un numéro unique dans le nom.
            file_number += 1

            # Construit le nom du fichier PDF en utilisant le numéro de séquence,
            # le dernier segment du chemin (qui identifie la ressource), et ajoute l'extension .pdf.
            # filename = f"{output_dir}/{file_number:04d}_{path_parts[-1]}.pdf"
            filename = f"{output_dir}/{file_number:04d}_{path[-1]}.pdf"

            # Créer le fichier pdf vide pour faire un test
            open(filename, "a").close()

            # Afficher l'URL actuelle
            logging.info(f"N°:{file_number:4}, URL Trouvée:{current_url}")
            convert_to_pdf(current_url, filename)

            # Trouver tous les liens
            links = soup.find_all("a")
            for link in links:
                href = link.get("href")
                if href:
                    # Ignorer les ancres et traiter les liens relatifs
                    href = href.split("#")[0]
                    if not href:
                        continue

                    # Construire l'URL complète pour les liens relatifs et supprimer le slash final
                    full_url = urljoin(current_url, href).rstrip("/")

                    # Vérifier que l'URL est interne au site et correspond au chemin souhaité
                    if (
                        urlparse(full_url).netloc == urlparse(start_url).netloc
                        and allowed_path in full_url
                    ):
                        # Vérifier que l'URL n'est pas déjà dans la queue
                        if full_url not in visited and full_url not in queue:
                            queue.append(full_url)  # Ajouter le lien à la queue

            # Attendre avant de faire une nouvelle requête pour éviter de surcharger le serveur
            time.sleep(1)

        except requests.Timeout:
            logging.warning(f"Timeout lors de la requête pour {current_url}")
            failed_url_count += 1
        except requests.ConnectionError:
            logging.warning(f"Problème de connexion pour {current_url}")
            failed_url_count += 1
        except requests.RequestException as e:
            logging.warning(f"Erreur lors de la requête pour {current_url} : {e}")
            failed_url_count += 1

    # Afficher les résultats finaux
    logging.info("Résultats de l'exploration :")
    logging.info(f"- Nombre total d'URL trouvées : {url_count}")
    logging.info(f"- Nombre d'URL traitées avec succès : {filtered_url_count}")
    logging.info(f"- Nombre d'URL de fichier ignorées : {ignored_file_count}")
    logging.info(f"- Nombre d'URL en échec : {failed_url_count}")
    return file_number


def parse_args():
    # Définir les arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Crawl a website")
    parser.add_argument(
        "-s", "--start-url", required=True, help="URL to start crawling"
    )
    parser.add_argument(
        "-a", "--allowed-path", required=True, help="Allowed path to filter URLs"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./pdffiles",
        help="Output directory for PDF files (default: ./pdffiles)",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        default=False,
        help="Limit processing to 3 URLs for testing purposes",
    )
    return parser.parse_args()


def main():
    # Parser les arguments en ligne de commande
    args = parse_args()
    if crawl_website(args.start_url, args.output_dir, args.allowed_path, args.test) > 0:
        filename = args.output_dir.rstrip("/") + "/zowe_3-0.pdf
        merge_pdf_files_in_sequence(
            args.output_dir, filename"
        )
        logging.info(f"Output file {filename} generated.")


if __name__ == "__main__":
    main()
