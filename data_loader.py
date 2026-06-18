"""
Chargement et préparation des couches géospatiales du Data Challenge Agriculture Togo.

Toutes les fonctions sont mises en cache par Streamlit pour éviter de recalculer
à chaque interaction utilisateur.
"""
from __future__ import annotations

import json

import geopandas as gpd
import pandas as pd
import streamlit as st

DATA_DIR = "data"
CRS_WGS84 = 4326          # coordonnées GPS standard (lat/lon)
CRS_PROJECTED = 32631     # UTM zone 31N, adapté au Togo pour des calculs de distance en mètres

FILES = {
    "exploitations": "exploitations.json",
    "marches": "marches.json",
    "zaap": "zaap.json",
    "cooperatives": "cooperatives.json",
}

# Colonnes texte pouvant contenir un artefact d'encodage (UTF-8 mal interprété
# en latin-1 lors d'un export antérieur) — observé sur exploitations.json.
TEXT_COLUMNS_TO_REPAIR = [
    "region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd",
    "nom_localite", "cooperative_type", "cooperative_nom", "marche_nom",
    "cooperative_statut", "organisme", "jour",
]


def _repair_mojibake(value):
    """Corrige un texte UTF-8 mal ré-encodé en latin-1 (ex. 'coopÃ©rative' -> 'coopérative').

    Sans risque : si le texte ne contient pas le motif typique d'un double
    encodage, il est renvoyé inchangé.
    """
    if not isinstance(value, str) or "Ã" not in value:
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value


@st.cache_data(show_spinner=False)
def load_layer(name: str) -> gpd.GeoDataFrame:
    """Charge une couche GeoJSON, corrige l'encodage et la reprojette en WGS84.

    PERFORMANCE — moteur de lecture : geopandas peut lire un GeoJSON avec deux
    moteurs, `fiona` (historique, pur Python, lent sur de gros fichiers) ou
    `pyogrio` (basé sur GDAL/Arrow, 5 à 15x plus rapide sur ce type de
    fichier). `exploitations.json` pèse plus de 10 Mo : c'est la couche qui
    bénéficie le plus de ce choix. On force `pyogrio` explicitement plutôt
    que de compter sur la détection automatique de geopandas, avec un repli
    silencieux sur le moteur par défaut si `pyogrio` n'est pas installé
    (l'app continue de fonctionner, juste moins vite).
    """
    try:
        gdf = gpd.read_file(f"{DATA_DIR}/{FILES[name]}", engine="pyogrio")
    except Exception:
        gdf = gpd.read_file(f"{DATA_DIR}/{FILES[name]}")
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    else:
        gdf = gdf.to_crs(CRS_WGS84)

    for col in TEXT_COLUMNS_TO_REPAIR:
        if col in gdf.columns:
            gdf[col] = gdf[col].map(_repair_mojibake)

    return gdf


@st.cache_data(show_spinner=False)
def load_all_layers() -> dict[str, gpd.GeoDataFrame]:
    """Charge les quatre couches et ajoute une colonne de centroïde (point représentatif).

    Les couches 'exploitations', 'marches' et 'zaap' sont des polygones dans
    les données source ; on calcule leur centroïde une seule fois ici pour
    tous les calculs de distance et d'affichage en aval (bien plus rapide
    que de le recalculer à chaque fonction).
    """
    layers = {name: load_layer(name) for name in FILES}

    for name in ("exploitations", "marches", "cooperatives", "zaap"):
        gdf = layers[name]
        if gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).any():
            # PERFORMANCE : .centroid sur 13 000+ polygones n'est pas gratuit.
            # On le calcule une seule fois (variable `centroid`) et on en
            # tire .x / .y, plutôt que d'appeler .geometry.centroid deux fois
            # (la version précédente le recalculait intégralement pour la
            # longitude, puis une seconde fois pour la latitude).
            centroid = gdf.geometry.centroid
            layers[name] = gdf.assign(centroid_lon=centroid.x, centroid_lat=centroid.y)
        else:
            layers[name] = gdf.assign(
                centroid_lon=gdf.geometry.x,
                centroid_lat=gdf.geometry.y,
            )
    return layers


def get_region_list(gdf: gpd.GeoDataFrame) -> list[str]:
    """Liste triée des régions présentes dans une couche, sans valeurs nulles."""
    col = "region_nom_bdd"
    if col not in gdf.columns:
        return []
    return sorted(v for v in gdf[col].dropna().unique() if v)


def filter_by_region(gdf: gpd.GeoDataFrame, region: str | None) -> gpd.GeoDataFrame:
    """Filtre une couche sur une région donnée. 'Toutes' ou None renvoie tout."""
    if not region or region == "Toutes les régions":
        return gdf
    return gdf[gdf["region_nom_bdd"] == region]
