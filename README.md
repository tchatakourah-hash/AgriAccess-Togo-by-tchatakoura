link: https://agriaccess-togo-by-tchatakoura-cvpgkge3wgirxpjnnmoypu.streamlit.app/
---
title: AgriAccess Togo
emoji: 🌱
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.58.0
app_file: app.py
pinned: false
---

# AgriAccess Togo

Tableau de bord interactif de la géographie du tissu agricole togolais, réalisé
pour le **Data Challenge Agriculture — Défi 1** (soumission 22/06/2026).

Thème visuel **Togo AI Lab** (vert / blanc) : bannière illustrée en SVG,
métriques en cartes vert plein à fort contraste, onglets et boutons grands et
gras, carte Folium avec calques activables/désactivables. Aucune dépendance
réseau pour l'habillage visuel : tout est généré en code (SVG), donc l'app
fonctionne de façon identique en local, en déploiement, ou hors-ligne.

## Objectif

Visualiser et analyser les exploitations agricoles, marchés, coopératives et
zones d'aménagement agricole planifiées (ZAAP/ZAPB) du Togo afin d'identifier :

- la densité spatiale des exploitations,
- la couverture des zones ZAAP (dont le nombre d'exploitations situées en ZAAP),
- l'accessibilité aux marchés,
- le réseau coopératif et ses zones sous-desservies.

## Données

Données ouvertes issues de [geodata.gouv.tg](http://geodata.gouv.tg/) et
[opendata.gouv.tg](http://opendata.gouv.tg/) :

| Fichier | Description | Géométrie | Nb. d'entités |
|---|---|---|---|
| `data/exploitations.json` | Petites exploitations agricoles | Polygones | 13 119 |
| `data/marches.json` | Marchés | Polygones | 1 078 |
| `data/zaap.json` | ZAAP/ZAPB — champs individuels | Polygones | 1 883 |
| `data/cooperatives.json` | Coopératives agricoles | Points | 6 859 |

Toutes les couches couvrent les 5 régions du Togo (Maritime, Plateaux,
Centrale, Kara, Savanes) et sont en EPSG:4326.

**Note qualité des données** : `exploitations.json` contient un artefact
d'encodage (UTF-8 mal interprété en latin-1) sur certaines lignes des champs
`cooperative_type` / `cooperative_nom` (ex. "coopÃ©rative" au lieu de
"coopérative"). Il est corrigé automatiquement au chargement
(`data_loader.py::_repair_mojibake`), sans perte d'information.

`zaap.json` contient également des polygones topologiquement invalides
(anneaux auto-intersectants — 133 zones sur 1 883, soit ~7%), un défaut
courant sur des données issues de digitalisation manuelle. Ces géométries
faisaient échouer `unary_union` avec une `TopologyException: side location
conflict`. Elles sont réparées automatiquement au calcul de la couverture
ZAAP (`analytics.py::_repair_geometries`, via `make_valid()`), sans
modification visible de leur forme.

**Point d'attention analytique** : les zones ZAAP/ZAPB ne couvrent que 3 des
5 régions (Savanes, Plateaux, Centrale) — la couverture ZAAP nationale est
donc structurellement faible. C'est un constat réel des données, pas une
erreur de calcul ; le dashboard le met en évidence plutôt que de le masquer.

## Structure du projet

```
agriaccess/
├── app.py            # Point d'entrée Streamlit
├── data_loader.py    # Chargement, réparation d'encodage, préparation des couches
├── analytics.py      # Calculs : distances, densités, couverture ZAAP, accès coopératives
├── maps.py           # Génération des cartes Folium (calques activables)
├── charts.py         # Graphiques Plotly
├── narration.py      # Commentaires pédagogiques sous chaque carte/graphique + résumé
├── styles.py         # Thème CSS Togo AI Lab (vert/blanc) + bannière SVG
├── icons.py           # Pictogrammes SVG (remplacent les emojis dans toute l'app)
├── requirements.txt
└── data/              # Jeux de données GeoJSON
```

## Installation locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fonctionnalités clés

- **Filtre Région** dans la barre latérale : applique le filtre à toutes les
  couches (exploitations, ZAAP, marchés, coopératives) et aux graphiques.
- **Carte Folium à calques** : exploitations, ZAAP/ZAPB, marchés et
  coopératives peuvent être activés/désactivés individuellement via le
  sélecteur de calques en haut à droite de chaque carte.
- **Métrique dédiée "Nb exploitations dans ZAAP"** : nombre brut (et non
  seulement le taux en %) d'exploitations dont le centroïde se situe à
  l'intérieur d'une zone ZAAP/ZAPB.
- **Rayon de recherche des coopératives** ajustable (5 à 25 km).
- **Identité visuelle Togo AI Lab** : aucun pictogramme emoji dans
  l'interface — bannière, logo, repères de région et synthèse utilisent des
  icônes vectorielles (`icons.py`) ; onglets et cartes de métriques à fort
  contraste (fond vert plein, texte blanc) pour une lisibilité maximale.
- **Commentaires pédagogiques** (`narration.py`) : sous chaque carte et
  chaque graphique, un encadré explique en langage simple ce qui est affiché
  et ce que les chiffres révèlent sur la sélection en cours (région, rayon
  des coopératives) — pensé pour une lecture par un public non spécialiste
  des données ou des SIG. Un résumé général, calculé à partir des mêmes
  données filtrées, clôt la page.

## Performance

Le chargement initial (lecture des 4 couches GeoJSON, calcul des
indicateurs, génération des cartes) est l'opération la plus coûteuse de
l'app ; plusieurs choix réduisent ce coût sans changer le résultat affiché :

- **Lecture GeoJSON via `pyogrio`** plutôt que `fiona` (moteur historique de
  geopandas) : nettement plus rapide sur des fichiers de plusieurs Mo comme
  `exploitations.json` (10 Mo). Repli automatique sur le moteur par défaut
  si `pyogrio` n'est pas installé.
- **Marqueurs cartographiques allégés** : les marchés et coopératives
  utilisaient des `folium.Icon` (glyphe FontAwesome + calcul d'ancrage par
  marqueur) ; remplacés par des `CircleMarker` (pastille colorée), bien
  moins coûteux à dessiner en grand nombre, sans perte d'information
  (popups conservés).
- **`prefer_canvas=True`** sur chaque carte Folium : dessine les formes
  vectorielles sur une seule toile graphique plutôt qu'un élément DOM par
  marqueur/cercle.
- **GeoJSON ZAAP allégé** : seules les colonnes utilisées par l'infobulle
  (et la géométrie) sont envoyées au navigateur, au lieu de tout le
  GeoDataFrame.
- **`returned_objects=[]`** sur chaque carte Streamlit-Folium : la valeur de
  retour (état de la carte) n'est pas utilisée par l'app ; la désactiver
  évite un aller-retour navigateur ⇄ serveur à chaque interaction.
- **Mise en cache** (`st.cache_data` / `st.cache_resource`) à tous les
  niveaux : lecture des couches, calcul des indicateurs, construction des
  cartes. Un correctif a aussi été apporté à la clé de cache de la carte
  d'accès, qui ignorait auparavant le rayon des coopératives (voir
  commentaire dans `maps.py::build_carte_acces`).

## Méthodologie

- **Distance au marché le plus proche** : calculée avec un `BallTree`
  (métrique haversine) sur les centroïdes, exact et performant même sur
  plusieurs milliers de points.
- **Couverture ZAAP** : jointure spatiale (`geopandas.sjoin`, prédicat
  `within`) entre le centroïde de chaque exploitation et les polygones
  ZAAP/ZAPB individuels (géométries réparées au préalable). Préférée à une
  fusion (`unary_union`) de toutes les zones, qui échoue sur des polygones
  invalides et est plus coûteuse à grande échelle.
- **Réseau coopératif** : nombre de coopératives dans un rayon ajustable
  (5 à 25 km) autour de chaque exploitation.
- **Agrégation cantonale** : les vues nationales agrègent par canton plutôt
  que d'afficher chaque exploitation individuellement, pour rester lisibles
  et performantes à l'échelle du pays.

## Auteur

Réalisé dans le cadre du Togo AI Lab Data Challenge.
