"""
Graphiques Plotly pour les analyses du dashboard AgriAccess Togo.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLOR_PRIMARY = "#0B6E2E"
COLOR_DARK = "#0B3D1E"
COLOR_GOLD = "#F2A900"
COLOR_SEQUENCE = ["#0B6E2E", "#F2A900", "#2980B9", "#C0392B", "#0B3D1E", "#15A94B"]
TEMPLATE = "plotly_white"

FONT = dict(family="Inter, Sora, sans-serif", color="#10241A")


def _style(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        font=FONT,
        title=dict(text=title, font=dict(size=18, family="Sora, sans-serif", color=COLOR_DARK)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=60, l=10, r=10, b=10),
    )
    # CORRECTIF — sur fond blanc pur sans grille ni contour marqués, les
    # graphiques perdaient leurs repères visuels (axes, échelle, grille à
    # peine visibles) et paraissaient flous une fois posés sur le fond crème
    # de la page. On renforce explicitement le contraste interne : grille
    # fine mais visible, ligne de base des axes nette, texte des axes plus
    # foncé — sans changer les couleurs des données elles-mêmes.
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E4E0D6",
        gridwidth=1,
        showline=True,
        linecolor="#C9C3B4",
        linewidth=1,
        zeroline=False,
        tickfont=dict(color=COLOR_DARK),
        title_font=dict(color=COLOR_DARK),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E4E0D6",
        gridwidth=1,
        showline=True,
        linecolor="#C9C3B4",
        linewidth=1,
        zeroline=False,
        tickfont=dict(color=COLOR_DARK),
        title_font=dict(color=COLOR_DARK),
    )
    return fig


def exploitations_par_region(df: pd.DataFrame) -> go.Figure:
    counts = df["region_nom_bdd"].value_counts().sort_values(ascending=True)
    fig = px.bar(
        counts,
        orientation="h",
        labels={"value": "Nombre d'exploitations", "index": "Région"},
        color_discrete_sequence=[COLOR_PRIMARY],
        template=TEMPLATE,
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Nombre d'exploitations")
    return _style(fig, "Exploitations agricoles par région")


def couverture_zaap_par_region(df: pd.DataFrame) -> go.Figure:
    taux = (
        df.groupby("region_nom_bdd")["dans_zaap"]
        .mean()
        .mul(100)
        .round(1)
        .sort_values(ascending=True)
    )
    fig = px.bar(
        taux,
        orientation="h",
        labels={"value": "Taux de couverture ZAAP (%)", "index": "Région"},
        color_discrete_sequence=[COLOR_GOLD],
        template=TEMPLATE,
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Couverture ZAAP (%)")
    return _style(fig, "Couverture ZAAP par région")


def distribution_distance_marche(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="dist_marche_km",
        nbins=40,
        labels={"dist_marche_km": "Distance au marché le plus proche (km)"},
        color_discrete_sequence=["#2980B9"],
        template=TEMPLATE,
    )
    fig.add_vline(
        x=df["dist_marche_km"].mean(),
        line_dash="dash",
        line_color="#C0392B",
        annotation_text=f"Moyenne : {df['dist_marche_km'].mean():.1f} km",
    )
    fig.update_layout(yaxis_title="Nombre d'exploitations")
    return _style(fig, "Distribution des distances aux marchés")


def score_acces_par_region(df: pd.DataFrame) -> go.Figure:
    fig = px.box(
        df,
        x="region_nom_bdd",
        y="score_acces",
        color="region_nom_bdd",
        labels={"region_nom_bdd": "Région", "score_acces": "Score d'accès au marché (0-100)"},
        color_discrete_sequence=COLOR_SEQUENCE,
        template=TEMPLATE,
    )
    fig.update_layout(showlegend=False)
    return _style(fig, "Score d'accès aux marchés par région")


def couverture_cooperatives(df: pd.DataFrame, radius_km: float) -> go.Figure:
    sans_coop = (df["nb_coop_rayon"] == 0).groupby(df["region_nom_bdd"]).sum()
    total = df.groupby("region_nom_bdd").size()
    taux_sans_coop = (sans_coop / total * 100).round(1).sort_values(ascending=True)
    fig = px.bar(
        taux_sans_coop,
        orientation="h",
        labels={"value": f"% sans coopérative à {radius_km:.0f} km", "index": "Région"},
        color_discrete_sequence=["#C0392B"],
        template=TEMPLATE,
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title=f"% sans coopérative à {radius_km:.0f} km")
    return _style(fig, f"Exploitations sans coopérative à moins de {radius_km:.0f} km")


def top_cantons_table(canton_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Cantons les moins bien desservis : score d'accès faible, peu de coopératives proches."""
    cols = [
        "region_nom_bdd",
        "prefecture_nom_bdd",
        "canton_nom_bdd",
        "nb_exploitations",
        "taux_zaap",
        "dist_marche_moy_km",
        "score_acces_moy",
        "sans_coop_10km",
    ]
    return (
        canton_df[cols]
        .sort_values("score_acces_moy", ascending=True)
        .head(n)
        .rename(
            columns={
                "region_nom_bdd": "Région",
                "prefecture_nom_bdd": "Préfecture",
                "canton_nom_bdd": "Canton",
                "nb_exploitations": "Exploitations",
                "taux_zaap": "Couverture ZAAP (%)",
                "dist_marche_moy_km": "Dist. marché moy. (km)",
                "score_acces_moy": "Score d'accès",
                "sans_coop_10km": "Sans coop. proche",
            }
        )
    )
