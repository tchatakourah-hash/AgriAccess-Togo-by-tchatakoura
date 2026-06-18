"""
Génération des cartes Folium pour le dashboard AgriAccess Togo.

Toutes les couches sont ajoutées comme des FeatureGroups nommés afin d'être
activées/désactivées individuellement via le sélecteur de calques Folium
(LayerControl) en haut à droite de la carte. Les noms de calques sont du
texte simple (pas d'emoji) pour rester cohérents avec le reste de l'habillage.
"""
from __future__ import annotations

import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster

TOGO_CENTER = [8.6, 0.9]
DEFAULT_ZOOM = 7

COLOR_PRIMARY = "#0B6E2E"   # vert AgriAccess
COLOR_DARK = "#0B3D1E"
COLOR_GOLD = "#F2A900"
COLOR_ACCENT = "#E67E22"
COLOR_ALERT = "#C0392B"

MAX_DETAIL_POINTS = 2500  # garde-fou si une couche contient énormément de points


def base_map(zoom: int = DEFAULT_ZOOM, tiles: str = "CartoDB positron") -> folium.Map:
    # PERFORMANCE — prefer_canvas=True : par défaut, Leaflet dessine les
    # marqueurs et cercles en SVG (un élément DOM par forme). Avec des
    # milliers de points (exploitations, coopératives), le navigateur devient
    # le facteur limitant. En mode "canvas", Leaflet dessine tout sur une
    # seule toile graphique : le gain est surtout perceptible au survol/zoom,
    # mais aussi au premier rendu, sans rien changer à l'apparence des cartes.
    return folium.Map(location=TOGO_CENTER, zoom_start=zoom, tiles=tiles, prefer_canvas=True)


def _fit_bounds_to_points(m: folium.Map, points: gpd.GeoDataFrame, padding: float = 0.15) -> None:
    """Cadre la carte sur l'étendue réelle des points fournis.

    CORRECTIF — sur une sélection régionale, le zoom fixe (7 ou 8) part
    toujours du centre du Togo : si la région choisie est petite ou excentrée,
    une bonne partie des points (et donc de la zone de chaleur) peut se
    retrouver hors du cadre visible au premier rendu, ce qui se perçoit comme
    « la carte n'affiche rien ». Recadrer sur l'étendue réelle des données
    élimine ce problème quelle que soit la région sélectionnée.

    CORRECTIF 2 — `.min()` / `.max()` sur une colonne pandas renvoient des
    `numpy.float64`, pas des `float` Python natifs. Contrairement à
    `add_heatmap` (qui passait déjà par `.tolist()`/`float(...)`), ces valeurs
    étaient transmises telles quelles à `fit_bounds()`. Le rendu HTML d'une
    carte Folium sérialise ses paramètres en JSON via Jinja2 : un
    `numpy.float64` n'est pas JSON-sérialisable nativement, ce qui faisait
    échouer le rendu de CETTE carte précisément (la seule des trois à appeler
    fit_bounds) sans toucher au reste de la page, ce qui correspond exactement
    au symptôme observé (carte de densité totalement absente, alors que
    « Carte d'accès » et « Couverture ZAAP » s'affichent normalement).
    """
    valid = points.dropna(subset=["centroid_lat", "centroid_lon"])
    if valid.empty:
        return
    lat_min, lat_max = float(valid["centroid_lat"].min()), float(valid["centroid_lat"].max())
    lon_min, lon_max = float(valid["centroid_lon"].min()), float(valid["centroid_lon"].max())
    # Une marge fixe minimale évite un zoom excessif quand tous les points
    # sont quasiment au même endroit (étendue proche de zéro).
    lat_pad = max((lat_max - lat_min) * padding, 0.05)
    lon_pad = max((lon_max - lon_min) * padding, 0.05)
    m.fit_bounds(
        [
            [lat_min - lat_pad, lon_min - lon_pad],
            [lat_max + lat_pad, lon_max + lon_pad],
        ]
    )


def _cap(gdf: gpd.GeoDataFrame, max_points: int = MAX_DETAIL_POINTS) -> gpd.GeoDataFrame:
    """Échantillonne une couche si elle dépasse max_points.

    Construire un folium.Marker par ligne dans une boucle Python est l'un
    des principaux postes de lenteur de l'app : ce garde-fou, déjà utilisé
    pour les exploitations, s'applique maintenant aussi aux marchés et
    surtout aux coopératives (jusqu'à 6 800+ points en vue « Toutes les
    régions », contre 1 078 marchés et un maximum de 2 500 exploitations
    déjà plafonné).
    """
    if len(gdf) > max_points:
        return gdf.sample(max_points, random_state=42)
    return gdf


def add_zaap_layer(m: folium.Map, zaap: gpd.GeoDataFrame, name: str = "Zones ZAAP / ZAPB") -> folium.FeatureGroup:
    fg = folium.FeatureGroup(name=name, show=True)
    # CORRECTIF — région sans aucune zone ZAAP/ZAPB (cas réel des données :
    # seules Savanes, Plateaux et Centrale en contiennent ; Maritime et Kara
    # n'en ont aucune — voir README). Une fois filtré sur l'une de ces deux
    # régions, `zaap` est vide : folium.GeoJson sérialise alors une
    # FeatureCollection sans aucune feature, donc sans aucune propriété, et
    # GeoJsonTooltip lève une AssertionError en validant ses `fields` contre
    # une liste de clés vide ("value in keys"). On évite simplement
    # d'ajouter la couche GeoJson/tooltip quand il n'y a rien à afficher :
    # le calque "Zones ZAAP / ZAPB" reste listé dans le sélecteur (vide),
    # sans casser le rendu de la carte.
    if zaap.empty:
        fg.add_to(m)
        return fg
    # PERFORMANCE — on n'envoie au navigateur que les colonnes réellement
    # utilisées (géométrie + les 2 champs du tooltip) plutôt que tout le
    # GeoDataFrame (qui inclut centroid_lon/lat, dans_zaap, etc.). Folium
    # sérialise ce GeoDataFrame en JSON et l'embarque tel quel dans la page :
    # moins de colonnes = un fichier HTML plus léger à transférer et à
    # parser côté navigateur, sans aucun changement visuel.
    slim = zaap[["geometry", "nom_localite", "commune_nom_bdd"]]
    folium.GeoJson(
        slim,
        style_function=lambda _: {
            "color": COLOR_PRIMARY,
            "weight": 1.5,
            "fillColor": COLOR_PRIMARY,
            "fillOpacity": 0.18,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["nom_localite", "commune_nom_bdd"],
            aliases=["Localité", "Commune"],
        ),
        # smooth_factor : simplifie légèrement le tracé des polygones au
        # rendu (côté Leaflet, pas sur les données sources) — invisible à
        # l'échelle d'affichage du Togo, mais moins de points à dessiner.
        smooth_factor=1.5,
    ).add_to(fg)
    fg.add_to(m)
    return fg


def add_marches_layer(m: folium.Map, marches: gpd.GeoDataFrame, name: str = "Marchés") -> folium.FeatureGroup:
    fg = folium.FeatureGroup(name=name, show=True)
    cluster = MarkerCluster().add_to(fg)
    # PERFORMANCE — folium.Icon (utilisé précédemment) charge une glyph
    # FontAwesome et calcule un positionnement de "pin" complexe pour
    # CHAQUE marqueur : sur 1 000+ marchés, cela alourdit nettement le
    # rendu. Un CircleMarker plein (même information, juste une pastille
    # colorée) est beaucoup plus léger à dessiner et tout aussi lisible sur
    # une carte de cette échelle.
    for _, row in _cap(marches).iterrows():
        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=5,
            color=COLOR_GOLD,
            fill=True,
            fill_color=COLOR_GOLD,
            fill_opacity=0.9,
            weight=1,
            popup=folium.Popup(
                f"<b>{row.get('marche_nom', 'Marché')}</b><br>"
                f"Commune : {row.get('commune_nom_bdd', '—')}<br>"
                f"Jours : {row.get('jour', '—')}",
                max_width=250,
            ),
        ).add_to(cluster)
    fg.add_to(m)
    return fg


def add_cooperatives_layer(
    m: folium.Map, cooperatives: gpd.GeoDataFrame, name: str = "Coopératives"
) -> folium.FeatureGroup:
    fg = folium.FeatureGroup(name=name, show=False)
    cluster = MarkerCluster().add_to(fg)
    # Voir le commentaire de add_marches_layer : CircleMarker plutôt que
    # folium.Icon, pour la même raison de performance (jusqu'à 2 500
    # coopératives affichées simultanément en vue nationale).
    for _, row in _cap(cooperatives).iterrows():
        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=4,
            color=COLOR_DARK,
            fill=True,
            fill_color=COLOR_DARK,
            fill_opacity=0.85,
            weight=1,
            popup=folium.Popup(
                f"<b>{row.get('cooperative_nom', 'Coopérative')}</b><br>"
                f"Commune : {row.get('commune_nom_bdd', '—')}<br>"
                f"Statut : {row.get('cooperative_statut', '—')}",
                max_width=250,
            ),
        ).add_to(cluster)
    fg.add_to(m)
    return fg


def add_exploitation_points(
    m: folium.Map,
    exploitations: gpd.GeoDataFrame,
    color_field: str = "score_acces",
    name: str = "Exploitations",
) -> folium.FeatureGroup:
    """Affiche les exploitations individuelles, colorées par score d'accès.

    À utiliser uniquement sur un sous-ensemble déjà filtré (région ou
    préfecture) afin de rester sous MAX_DETAIL_POINTS et garder la carte fluide.
    """
    fg = folium.FeatureGroup(name=name, show=True)
    subset = _cap(exploitations)

    for _, row in subset.iterrows():
        score = row.get(color_field, 50)
        color = COLOR_ALERT if score < 30 else COLOR_ACCENT if score < 60 else COLOR_PRIMARY
        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.75,
            weight=0.5,
            popup=(
                f"Score d'accès : {score:.0f}/100<br>"
                f"Distance marché : {row.get('dist_marche_km', 0):.1f} km<br>"
                f"Coopératives à proximité : {row.get('nb_coop_rayon', 0)}<br>"
                f"Dans ZAAP : {'Oui' if row.get('dans_zaap') else 'Non'}"
            ),
        ).add_to(fg)
    fg.add_to(m)
    return fg


DENSITY_GRID_CELL_DEG = 0.09  # ~9-10 km de côté, adapté à l'échelle du Togo
DENSITY_GRID_COLORS = [
    (0.15, "#FDE9A8"),  # faible densité — jaune pâle
    (0.35, COLOR_GOLD),
    (0.65, COLOR_ACCENT),
    (1.01, COLOR_ALERT),  # forte densité — rouge
]
DENSITY_MIN_RADIUS = 7   # pixels
DENSITY_MAX_RADIUS = 26  # pixels


def add_heatmap(m: folium.Map, points: gpd.GeoDataFrame, name: str = "Densité") -> folium.FeatureGroup:
    """Affiche la concentration spatiale des exploitations sous forme de bulles colorées.

    CORRECTIF 1 — la version précédente s'appuyait sur le plugin Leaflet.heat
    (folium.plugins.HeatMap), qui charge un fichier JavaScript supplémentaire
    depuis un CDN externe pour fonctionner. Si ce CDN est lent, bloqué ou
    temporairement indisponible (réseau d'entreprise, pare-feu, blocage
    régional, panne du CDN...), la classe JS qui dessine la couche n'est
    jamais définie : la couche reste alors invisible, sans aucune erreur
    visible côté Streamlit ou Python. On reconstruit donc la même
    information (où les exploitations sont les plus concentrées) avec
    uniquement des primitives Leaflet de base, déjà utilisées avec succès
    partout ailleurs dans ce dashboard.

    CORRECTIF 2 — une première version dessinait des `Rectangle` (un
    polygone dont la taille est définie en degrés géographiques, donc fixe
    sur le terrain). À l'échelle nationale, une cellule de quelques
    kilomètres ne représente plus que 1-2 pixels à l'écran : la couche
    s'affichait techniquement, mais devenait invisible à l'œil ("la carte
    apparaît mais sans chaleur"). `CircleMarker`, comme `Circle` et
    contrairement à `Rectangle`/`Circle`, a un rayon défini en **pixels
    d'écran** et non en unités géographiques : la bulle garde donc une
    taille constante et bien visible à n'importe quel niveau de zoom,
    exactement comme le faisait le plugin Leaflet.heat d'origine.
    """
    fg = folium.FeatureGroup(name=name, show=True)
    valid = points.dropna(subset=["centroid_lat", "centroid_lon"])
    if valid.empty:
        fg.add_to(m)
        return fg

    # Regroupe les exploitations dans une grille régulière, puis compte le
    # nombre de points par cellule : c'est ce compte qui pilote la couleur
    # et la taille de la bulle affichée au centre de chaque cellule.
    lat_bin = (valid["centroid_lat"] / DENSITY_GRID_CELL_DEG).round() * DENSITY_GRID_CELL_DEG
    lon_bin = (valid["centroid_lon"] / DENSITY_GRID_CELL_DEG).round() * DENSITY_GRID_CELL_DEG
    grid = (
        pd.DataFrame({"lat_bin": lat_bin, "lon_bin": lon_bin})
        .groupby(["lat_bin", "lon_bin"])
        .size()
        .reset_index(name="count")
    )
    max_count = int(grid["count"].max()) or 1

    # Tri par densité croissante : les bulles les plus grandes (zones les
    # plus denses) sont ajoutées en dernier, donc dessinées au-dessus —
    # elles restent visibles même quand des bulles voisines se superposent.
    for _, row in grid.sort_values("count").iterrows():
        count = float(row["count"])
        ratio = count / max_count
        color = next(c for threshold, c in DENSITY_GRID_COLORS if ratio <= threshold)
        # Échelle en racine carrée : la surface de la bulle (pas son rayon)
        # est à peu près proportionnelle au nombre d'exploitations, ce qui
        # est perceptuellement plus juste qu'une échelle linéaire du rayon.
        radius = DENSITY_MIN_RADIUS + (DENSITY_MAX_RADIUS - DENSITY_MIN_RADIUS) * (ratio ** 0.5)
        folium.CircleMarker(
            location=[float(row["lat_bin"]), float(row["lon_bin"])],
            radius=radius,
            color=color,
            weight=0,
            fill=True,
            fill_color=color,
            # fill_opacity : un plancher minimal garantit que même les
            # bulles les moins denses restent visibles dès le premier
            # rendu, sans attendre un zoom poussé.
            fill_opacity=0.55 + 0.25 * ratio,
            popup=f"{int(count)} exploitation(s) dans cette zone",
        ).add_to(fg)
    fg.add_to(m)
    return fg


def add_canton_choropleth(
    m: folium.Map, canton_df: pd.DataFrame, value_field: str, legend: str, name: str = "Score moyen par canton"
) -> folium.FeatureGroup:
    """Cercles proportionnels par canton (alternative simple à un vrai choroplèthe
    polygonal quand on ne dispose pas des limites administratives en GeoJSON)."""
    fg = folium.FeatureGroup(name=name, show=True)
    if canton_df.empty:
        fg.add_to(m)
        return fg
    vmax = canton_df[value_field].max() or 1
    for _, row in canton_df.iterrows():
        value = row[value_field]
        radius = 4 + 16 * (value / vmax)
        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=radius,
            color=COLOR_PRIMARY,
            fill=True,
            fill_color=COLOR_PRIMARY,
            fill_opacity=0.5,
            weight=1,
            popup=(
                f"<b>{row['canton_nom_bdd']}</b> ({row['commune_nom_bdd']})<br>"
                f"{legend} : {value:.1f}<br>"
                f"Exploitations : {int(row['nb_exploitations'])}"
            ),
        ).add_to(fg)
    fg.add_to(m)
    return fg


def add_layer_control(m: folium.Map) -> None:
    """Ajoute le sélecteur de calques (cases à cocher) en haut à droite de la carte."""
    folium.LayerControl(collapsed=False, position="topright").add_to(m)


# ─────────────────────────────────────────────────────────────────────────
# Constructeurs de cartes mis en cache
# ─────────────────────────────────────────────────────────────────────────
# CORRECTIF — pas de cache sur les objets folium.Map eux-mêmes.
#
# Ces fonctions étaient auparavant décorées avec @st.cache_resource, qui met
# en cache un objet Python "vivant" partagé par TOUTES les sessions/requêtes
# du déploiement. Un objet folium.Map est mutable (sa structure interne de
# couches est modifiée pendant le rendu HTML). Quand deux requêtes arrivent
# en parallèle (deux visiteurs, ou simplement deux ré-exécutions rapprochées
# du script par Streamlit), elles peuvent toutes les deux déclencher le
# rendu du même objet partagé en même temps : l'une parcourt la liste des
# couches pendant que l'autre la modifie, ce qui provoque un
# `RuntimeError: OrderedDict mutated during iteration` (intermittent, donc
# difficile à reproduire de façon fiable).
#
# Sans cache ici, chaque appel reconstruit un objet folium.Map indépendant,
# ce qui élimine totalement ce risque de concurrence. Le coût en performance
# reste faible : les couches ajoutées (zaap, marchés, coopératives,
# exploitations) utilisent déjà des CircleMarker légers et des GeoJSON
# allégés (voir add_*_layer ci-dessus) ; l'essentiel du travail coûteux
# (chargement des données, calcul des indicateurs, agrégation cantonale)
# reste mis en cache en amont via st.cache_data dans data_loader.py et
# analytics.py.


def build_carte_acces(
    _exploitations_filtered: gpd.GeoDataFrame,
    _marches_filtered: gpd.GeoDataFrame,
    _zaap_filtered: gpd.GeoDataFrame,
    _cooperatives_filtered: gpd.GeoDataFrame,
    _canton_stats: pd.DataFrame,
    region_key: str,
    coop_radius_km: float,
) -> folium.Map:
    # CORRECTIF — les popups de cette carte affichent "Coopératives à
    # proximité" (nb_coop_rayon), qui dépend du rayon choisi dans la barre
    # latérale. Avant ce correctif, ce rayon n'entrait pas dans la clé de
    # cache (seul region_key y participait) : changer le curseur sans
    # changer de région renvoyait une carte mise en cache avec l'ancien
    # rayon, donc des popups au contenu périmé. coop_radius_km est un float
    # simple et bon marché à hasher, donc on l'ajoute à la signature pour
    # que le cache se régénère correctement quand il change.
    is_national = region_key == "Toutes les régions"
    m = base_map(zoom=7 if is_national else 8)
    add_zaap_layer(m, _zaap_filtered)
    add_marches_layer(m, _marches_filtered)
    add_cooperatives_layer(m, _cooperatives_filtered)
    if is_national:
        add_canton_choropleth(m, _canton_stats, "score_acces_moy", "Score d'accès moyen")
    else:
        add_exploitation_points(m, _exploitations_filtered)
    add_layer_control(m)
    return m


def build_carte_densite(
    _exploitations_filtered: gpd.GeoDataFrame,
    _zaap_filtered: gpd.GeoDataFrame,
    region_key: str,
) -> folium.Map:
    is_national = region_key == "Toutes les régions"
    # CORRECTIF (fond de carte) — le fond "CartoDB dark_matter" était chargé
    # depuis un CDN externe (basemaps.cartocdn.com) : sur un réseau qui
    # bloque ce domaine (proxy d'entreprise, pare-feu), le fond restait
    # blanc. On revient au même fond clair "CartoDB positron" que les autres
    # cartes de l'app (déjà éprouvé sur les onglets « Carte d'accès » et
    # « Couverture ZAAP »), ce qui élimine cette dépendance supplémentaire
    # sans rien retirer à la lisibilité : la grille de densité (jaune →
    # rouge, voir add_heatmap) reste parfaitement lisible sur fond clair.
    m = base_map(zoom=7 if is_national else 8)
    add_heatmap(m, _exploitations_filtered)
    add_zaap_layer(m, _zaap_filtered)
    add_layer_control(m)
    # Cadrage explicite sur l'étendue réelle des exploitations affichées :
    # garantit que la grille de densité est toujours dans le champ visible,
    # même pour une région de petite taille ou excentrée par rapport au
    # centre du Togo utilisé comme position de départ par défaut.
    # try/except défensif : un échec de cadrage ne doit jamais faire
    # disparaître la carte entière (c'est précisément ce qui s'est produit
    # avec des numpy.float64 non convertis, voir docstring de la fonction) —
    # en dernier recours, on préfère un cadrage par défaut moins précis à une
    # carte totalement absente.
    try:
        _fit_bounds_to_points(m, _exploitations_filtered)
    except Exception:
        pass
    return m


def build_carte_zaap(
    _exploitations_filtered: gpd.GeoDataFrame,
    _zaap_filtered: gpd.GeoDataFrame,
    region_key: str,
) -> folium.Map:
    is_national = region_key == "Toutes les régions"
    m = base_map(zoom=7 if is_national else 8)
    add_zaap_layer(m, _zaap_filtered)
    subset = _exploitations_filtered.copy()
    subset["score_acces"] = subset["dans_zaap"].map({True: 100, False: 0})
    add_exploitation_points(m, subset, color_field="score_acces")
    add_layer_control(m)
    return m
