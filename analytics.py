"""
Calculs analytiques pour le dashboard AgriAccess Togo.

Chaque fonction est mise en cache et reçoit des arguments simples (pas de
GeoDataFrame complet quand on peut l'éviter) pour que le cache Streamlit
fonctionne correctement entre les rechargements.
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.neighbors import BallTree

from data_loader import CRS_PROJECTED, CRS_WGS84

EARTH_RADIUS_KM = 6371.0


@st.cache_data(show_spinner=False)
def nearest_distance_km(
    origin_lats: np.ndarray,
    origin_lons: np.ndarray,
    target_lats: np.ndarray,
    target_lons: np.ndarray,
) -> np.ndarray:
    """Distance (km) de chaque point d'origine au point cible le plus proche.

    Utilise un BallTree avec métrique haversine : exact sur une sphère et
    bien plus rapide qu'une boucle de calcul de distance point à point,
    même sur des dizaines de milliers de points.
    """
    target_rad = np.radians(np.column_stack([target_lats, target_lons]))
    origin_rad = np.radians(np.column_stack([origin_lats, origin_lons]))
    tree = BallTree(target_rad, metric="haversine")
    dist_rad, _ = tree.query(origin_rad, k=1)
    return dist_rad.flatten() * EARTH_RADIUS_KM


@st.cache_data(show_spinner=False)
def count_within_radius(
    origin_lats: np.ndarray,
    origin_lons: np.ndarray,
    target_lats: np.ndarray,
    target_lons: np.ndarray,
    radius_km: float,
) -> np.ndarray:
    """Nombre de points cibles dans un rayon donné (km) autour de chaque origine.

    Calcul exact sur l'ensemble des points (pas d'échantillonnage) : un
    BallTree avec query_radius reste rapide même sur 13 000+ points.
    """
    target_rad = np.radians(np.column_stack([target_lats, target_lons]))
    origin_rad = np.radians(np.column_stack([origin_lats, origin_lons]))
    tree = BallTree(target_rad, metric="haversine")
    radius_rad = radius_km / EARTH_RADIUS_KM
    counts = tree.query_radius(origin_rad, r=radius_rad, count_only=True)
    return counts


@st.cache_data(show_spinner=False)
def compute_zaap_coverage(
    _exploitations: gpd.GeoDataFrame, _zaap: gpd.GeoDataFrame
) -> pd.Series:
    """Indique pour chaque exploitation si elle se trouve dans une zone ZAAP/ZAPB.

    Le préfixe underscore sur les paramètres indique à Streamlit de ne pas
    hasher ces objets volumineux pour la clé de cache (on cache plutôt le
    résultat, recalculé seulement si la fonction est rappelée dans le run).

    Implémentation par jointure spatiale (sjoin) plutôt que par
    `unary_union` : les polygones ZAAP/ZAPB issus de données ouvertes
    contiennent parfois de légères invalidités topologiques (anneaux
    auto-intersectants, sommets dupliqués) qui font échouer `unary_union`
    avec une `TopologyException: side location conflict`. Une jointure
    spatiale point-dans-polygone évite ce problème car elle ne nécessite
    pas de fusionner les géométries entre elles — chaque polygone est
    testé indépendamment. Les géométries sont aussi réparées par
    précaution (`make_valid`, avec repli sur `buffer(0)` si indisponible).
    """
    exploit_proj = _exploitations.to_crs(CRS_PROJECTED).copy()
    zaap_proj = _zaap.to_crs(CRS_PROJECTED).copy()

    zaap_proj["geometry"] = _repair_geometries(zaap_proj.geometry)

    points = gpd.GeoDataFrame(
        {"_orig_index": exploit_proj.index},
        geometry=exploit_proj.geometry.centroid,
        crs=exploit_proj.crs,
    )

    joined = gpd.sjoin(points, zaap_proj[["geometry"]], how="left", predicate="within")
    in_zaap = joined.groupby("_orig_index")["index_right"].apply(lambda s: s.notna().any())
    in_zaap = in_zaap.reindex(exploit_proj.index, fill_value=False)

    return pd.Series(in_zaap.values, index=_exploitations.index, name="dans_zaap")


def _repair_geometries(geoms: gpd.GeoSeries) -> gpd.GeoSeries:
    """Répare les géométries topologiquement invalides sans changer leur forme visible.

    Essaie `make_valid()` (Shapely >= 2.0, la méthode recommandée) puis
    retombe sur `buffer(0)` (fonctionne sur toutes les versions) si la
    première n'est pas disponible ou échoue. Sur une invalidité sévère,
    `make_valid()` peut renvoyer une GeometryCollection mêlant points,
    lignes et polygones : on ne garde alors que la partie polygonale,
    seule pertinente pour un test "point dans la zone".
    """
    try:
        repaired = geoms.make_valid()
    except Exception:
        repaired = geoms.buffer(0)

    needs_extraction = repaired.geom_type.isin(["GeometryCollection"])
    if needs_extraction.any():
        repaired.loc[needs_extraction] = repaired.loc[needs_extraction].apply(_largest_polygonal_part)

    return repaired


def _largest_polygonal_part(geom):
    """Extrait la plus grande composante Polygon/MultiPolygon d'une GeometryCollection."""
    polys = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
    if not polys:
        return geom
    return max(polys, key=lambda g: g.area)


def aggregate_by_canton(
    _exploitations: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Agrège les indicateurs clés par canton pour la carte choroplèthe.

    Évite d'afficher 13 000+ polygones individuels sur une carte Folium
    (illisible et lent) ; chaque canton devient une ligne avec ses moyennes
    et son nombre d'exploitations.

    Note : pas de @st.cache_data ici. Cette fonction reçoit un sous-ensemble
    déjà filtré par région (potentiellement différent à chaque exécution),
    et le calcul (groupby sur quelques milliers de lignes au plus) est de
    toute façon quasi instantané — un cache basé sur un objet non hashé
    (préfixe _) renverrait ici le résultat de la toute première région
    appelée, ce qui serait un bug silencieux.
    """
    df = _exploitations.copy()
    group_cols = ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd"]
    agg = df.groupby(group_cols, dropna=False).agg(
        nb_exploitations=("dans_zaap", "size"),
        taux_zaap=("dans_zaap", "mean"),
        dist_marche_moy_km=("dist_marche_km", "mean"),
        score_acces_moy=("score_acces", "mean"),
        sans_coop_10km=("nb_coop_rayon", lambda s: (s == 0).sum()),
        centroid_lat=("centroid_lat", "mean"),
        centroid_lon=("centroid_lon", "mean"),
    ).reset_index()
    agg["taux_zaap"] = (agg["taux_zaap"] * 100).round(1)
    agg["dist_marche_moy_km"] = agg["dist_marche_moy_km"].round(2)
    agg["score_acces_moy"] = agg["score_acces_moy"].round(1)
    return agg


def access_score(distance_km: np.ndarray, max_distance_km: float = 20.0) -> np.ndarray:
    """Score d'accès 0-100 : 100 = marché juste à côté, 0 = à max_distance_km ou plus.

    Décroissance linéaire ; les distances au-delà du seuil sont plafonnées à 0
    plutôt que de devenir négatives.
    """
    score = 100 - (distance_km / max_distance_km) * 100
    return np.clip(score, 0, 100)


@st.cache_data(show_spinner=False)
def compute_all_indicators(
    _exploitations: gpd.GeoDataFrame,
    _marches: gpd.GeoDataFrame,
    _zaap: gpd.GeoDataFrame,
    _cooperatives: gpd.GeoDataFrame,
    coop_radius_km: float,
) -> gpd.GeoDataFrame:
    """Calcule tous les indicateurs au niveau exploitation et renvoie la couche enrichie."""
    result = _exploitations.copy()

    result["dist_marche_km"] = nearest_distance_km(
        result["centroid_lat"].to_numpy(),
        result["centroid_lon"].to_numpy(),
        _marches["centroid_lat"].to_numpy(),
        _marches["centroid_lon"].to_numpy(),
    )
    result["score_acces"] = access_score(result["dist_marche_km"].to_numpy())

    result["nb_coop_rayon"] = count_within_radius(
        result["centroid_lat"].to_numpy(),
        result["centroid_lon"].to_numpy(),
        _cooperatives["centroid_lat"].to_numpy(),
        _cooperatives["centroid_lon"].to_numpy(),
        coop_radius_km,
    )

    result["dans_zaap"] = compute_zaap_coverage(result, _zaap)

    return result
