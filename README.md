# Traitement de Conversion des Pages HTML en PDF

## Description

Ce projet est un programme en Python conçu pour scanner toutes les URLs d’un site web et convertir chaque page HTML en un fichier PDF distinct. Il suit la structure de navigation du site pour préserver l’ordre naturel de consultation.

## Bibliothèques Utilisées

Le développement s’appuie sur les bibliothèques suivantes :

Le développement s’appuie sur les bibliothèques suivantes :

- [**requests**](https://docs.python-requests.org/en/master/): pour effectuer des requêtes HTTP. Cette bibliothèque permet d’accéder facilement aux URL, de récupérer et d’envoyer des données sur le web.
- [**BeautifulSoup4**](https://www.crummy.com/software/BeautifulSoup/): pour analyser et parcourir les documents HTML et XML, facilitant ainsi l'extraction de données depuis des pages web.
- [**PyPDF2**](https://pypdf2.readthedocs.io/): pour manipuler les fichiers PDF. Elle permet d’effectuer des opérations telles que la fusion de plusieurs fichiers PDF en un seul.
- [**pdfkit**](https://pypi.org/project/pdfkit/): pour convertir des documents HTML en PDF en utilisant wkhtmltopdf, permettant la création de fichiers PDF à partir de contenu web.

## Objectif Général

Le programme convertit les pages HTML d'un site en ligne en fichiers PDF, en suivant l’ordre logique de navigation du site. Ce traitement est automatisé et accède directement aux pages pour reproduire une navigation naturelle.

## Fonctionnalités du Programme

### Conversion Page par Page

- Chaque page HTML est convertie en un fichier PDF individuel.
- Les fichiers PDF sont stockés dans un répertoire dédié.

### Nom des Fichiers PDF

- Les fichiers PDF sont nommés de manière structurée, par exemple : `001_accueil.pdf`, `002_p1.pdf`, etc.
- Cela facilite l’identification rapide de chaque page en fonction de l’ordre de conversion.

### Ordre de Conversion

- La conversion respecte l’ordre des liens présents sur chaque page, pour conserver la navigation naturelle.
- Par exemple, si la page d’accueil contient des liens vers `p1.html`, `p2.html`, `p3.html`, ces pages seront converties dans cet ordre.
- Les sous-liens sont convertis après leur page parente, selon l’ordre de navigation.

### Exploration des Pages HTML

Le programme utilise **BeautifulSoup4** pour :

- Explorer la structure des pages HTML.
- Identifier et extraire les balises de liens (`<a>`) afin de déterminer l'ordre de conversion des pages.

## Ajustements Suite aux Découvertes pendant le Développement

Au cours du développement, plusieurs ajustements ont été nécessaires pour optimiser le traitement des URLs :

- **Ignorer les ancres** : Les ancres (`#`) désignent des liens internes à une page, pointant vers des sections spécifiques sans constituer de nouvelles pages. Leur exclusion permet d’éviter des redondances inutiles dans les fichiers PDF, car le contenu est déjà capturé dans la page principale.

- **Exclusion des URLs de fichiers** : Les URLs pointant vers des ressources comme des PDF, images ou documents téléchargeables (par exemple, `example.com/doc.pdf` ou `example.com/image.jpg`) sont ignorées. Le programme se concentre uniquement sur la conversion des pages HTML en PDF, afin de se limiter aux pages de contenu.

- **Normalisation des URLs se terminant par un slash** : Les URLs finissant par `/` sont normalisées en retirant le slash final (par exemple, `example.com/page/` devient `example.com/page`). Un slash final indique souvent une page ou un répertoire, et sa suppression permet d’éviter de traiter plusieurs fois la même URL, simplifiant ainsi le suivi des liens.

Ce programme constitue une solution complète pour la capture et la conversion des pages HTML d’un site en fichiers PDF, tout en respectant la logique de navigation et en minimisant les doublons.
