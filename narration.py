"""
Commentaires pédagogiques affichés sous chaque carte et chaque graphique.

Objectif : qu'une personne qui ne connaît ni les SIG ni les statistiques
comprenne, à chaque étape, (1) ce qu'elle regarde et (2) ce que cela révèle
concrètement sur le terrain. Toutes les phrases sont calculées à partir des
données filtrées affichées à l'écran (région choisie, rayon des
coopératives) : elles changent avec les filtres, jamais de chiffre codé en
dur qui pourrait devenir incohérent avec ce que montre la carte ou le
graphique juste au-dessus.

Chaque fonction renvoie un fragment HTML (texte + chiffres en gras) destiné
à être inséré dans un `note_box()` (voir app.py), pas un texte brut : on
peut donc se permettre <strong>, <em>, etc.
"""
from __future__ import annotations

import pandas as pd


def _pct(n: float, total: float) -> float:
    return 0.0 if total == 0 else n / total * 100


def _fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", " ")


def _single_region(df: pd.DataFrame) -> str | None:
    """Renvoie le nom de la région si la sélection actuelle n'en contient
    qu'une seule, sinon None.

    Sert à éviter des phrases comparatives absurdes du type « la région X
    présente la meilleure couverture » quand X est, par construction,
    la seule région affichée (l'utilisateur l'a déjà choisie dans le filtre).
    """
    if "region_nom_bdd" not in df.columns:
        return None
    uniques = df["region_nom_bdd"].dropna().unique()
    return uniques[0] if len(uniques) == 1 else None


# ─────────────────────────────────────────────────────────────────────────
# Onglet "Carte d'accès"
# ─────────────────────────────────────────────────────────────────────────
def carte_acces(df: pd.DataFrame) -> str:
    total = len(df)
    bon = (df["score_acces"] >= 60).sum()
    moyen = ((df["score_acces"] >= 30) & (df["score_acces"] < 60)).sum()
    difficile = (df["score_acces"] < 30).sum()
    return (
        "<strong>Ce que montre cette carte</strong> — chaque point est une exploitation, "
        "colorée selon son <em>score d'accès au marché</em> : ce score vaut 100 quand le "
        "marché le plus proche est juste à côté, et descend vers 0 à mesure que la distance "
        "augmente (0 à partir de 20&nbsp;km). Vert = bon accès, orange = accès moyen, "
        "rouge = accès difficile. "
        f"<strong>Sur la sélection actuelle</strong> : {_pct(bon, total):.0f}% des exploitations "
        f"sont en bon accès, {_pct(moyen, total):.0f}% en accès moyen et "
        f"<strong>{_pct(difficile, total):.0f}% en accès difficile</strong> (plus de 14&nbsp;km en "
        "moyenne du marché le plus proche)."
    )


# ─────────────────────────────────────────────────────────────────────────
# Onglet "Densité"
# ─────────────────────────────────────────────────────────────────────────
def carte_densite(df: pd.DataFrame) -> str:
    total = len(df)
    intro = (
        "<strong>Ce que montre cette carte</strong> — chaque bulle représente une zone du "
        "territoire ; sa couleur et sa taille indiquent le nombre d'exploitations qui s'y "
        "trouvent (jaune pâle/petite bulle = faible densité, rouge/grande bulle = très forte "
        "densité). "
    )
    if total == 0 or "region_nom_bdd" not in df.columns:
        return intro
    only_region = _single_region(df)
    if only_region is not None:
        return intro + (
            f"<strong>Sur la sélection actuelle</strong> : {_fmt(total)} exploitations sont "
            f"affichées pour la région <strong>{only_region}</strong>. Les zones les plus "
            "lumineuses correspondent aux localités où l'activité agricole recensée est la plus "
            "dense au sein de cette région."
        )
    par_region = df["region_nom_bdd"].value_counts()
    top_region = par_region.idxmax()
    top_count = int(par_region.max())
    return intro + (
        f"<strong>Sur la sélection actuelle</strong> : la région <strong>{top_region}</strong> "
        f"concentre le plus d'exploitations recensées ({_fmt(top_count)} sur "
        f"{_fmt(total)}, soit {_pct(top_count, total):.0f}% du total affiché)."
    )


# ─────────────────────────────────────────────────────────────────────────
# Onglet "Couverture ZAAP"
# ─────────────────────────────────────────────────────────────────────────
def carte_zaap(df: pd.DataFrame) -> str:
    total = len(df)
    nb_dans = int(df["dans_zaap"].sum()) if total else 0
    return (
        "<strong>Ce que montre cette carte</strong> — vert : l'exploitation se trouve à "
        "l'intérieur d'une zone d'aménagement agricole planifiée (ZAAP/ZAPB) ; rouge : elle "
        "se trouve hors de toute zone ZAAP/ZAPB recensée. "
        f"<strong>Sur la sélection actuelle</strong> : <strong>{_fmt(nb_dans)} exploitation(s)</strong> "
        f"sur {_fmt(total)} ({_pct(nb_dans, total):.1f}%) sont situées en zone ZAAP/ZAPB. "
        "<strong>Point d'attention sur les données</strong> : les zones ZAAP/ZAPB recensées dans "
        "ce jeu de données ne couvrent que les régions Savanes, Plateaux et (très marginalement) "
        "Centrale — aucune zone n'est cartographiée dans le Maritime ni le Kara. Un taux de 0% "
        "pour ces deux régions reflète donc une absence de zones ZAAP dans la donnée source, pas "
        "une erreur de calcul ni un défaut d'aménagement réel du territoire."
    )


# ─────────────────────────────────────────────────────────────────────────
# Onglet "Analyses" — un commentaire par graphique
# ─────────────────────────────────────────────────────────────────────────
def chart_exploitations_par_region(df: pd.DataFrame) -> str:
    intro = (
        "<strong>Comment lire ce graphique</strong> — chaque barre est le nombre d'exploitations "
        "agricoles recensées dans une région ; plus la barre est longue, plus la région compte "
        "d'exploitations. "
    )
    only_region = _single_region(df)
    if only_region is not None:
        return intro + (
            f"<strong>Constat</strong> : la sélection actuelle ne contient qu'une seule région "
            f"(<strong>{only_region}</strong>, {_fmt(len(df))} exploitations) — choisissez "
            "« Toutes les régions » dans la barre latérale pour comparer."
        )
    counts = df["region_nom_bdd"].value_counts()
    top, bottom = counts.idxmax(), counts.idxmin()
    return intro + (
        f"<strong>Constat</strong> : <strong>{top}</strong> arrive en tête avec "
        f"{_fmt(counts.max())} exploitations, contre seulement {_fmt(counts.min())} pour "
        f"<strong>{bottom}</strong>."
    )


def chart_couverture_zaap_par_region(df: pd.DataFrame) -> str:
    intro = (
        "<strong>Comment lire ce graphique</strong> — pour chaque région, la part de ses "
        "exploitations situées à l'intérieur d'une zone ZAAP/ZAPB. "
    )
    caveat = (
        "Rappel : seules les régions où des zones ZAAP ont été cartographiées (Savanes, "
        "Plateaux, Centrale) peuvent afficher un taux supérieur à 0%."
    )
    only_region = _single_region(df)
    if only_region is not None:
        taux = df["dans_zaap"].mean() * 100
        return intro + f"<strong>Constat</strong> : {taux:.1f}% pour {only_region}. {caveat}"
    taux = df.groupby("region_nom_bdd")["dans_zaap"].mean().mul(100)
    top = taux.idxmax()
    return intro + (
        f"<strong>Constat</strong> : <strong>{top}</strong> affiche la meilleure couverture "
        f"({taux.max():.1f}%). {caveat}"
    )


def chart_distribution_distance(df: pd.DataFrame) -> str:
    moy = df["dist_marche_km"].mean()
    p90 = df["dist_marche_km"].quantile(0.9)
    return (
        "<strong>Comment lire ce graphique</strong> — chaque barre regroupe les exploitations "
        "selon leur distance au marché le plus proche ; la ligne pointillée rouge marque la "
        "moyenne. Une distribution étalée vers la droite signifie qu'une partie des "
        "exploitations est loin de tout marché. "
        f"<strong>Constat</strong> : distance moyenne de <strong>{moy:.1f}&nbsp;km</strong> ; "
        f"10% des exploitations sont à plus de <strong>{p90:.1f}&nbsp;km</strong> du marché le "
        "plus proche."
    )


def chart_score_acces_par_region(df: pd.DataFrame) -> str:
    intro = (
        "<strong>Comment lire ce graphique</strong> — chaque boîte résume, pour une région, la "
        "distribution du score d'accès aux marchés (0 = accès difficile, 100 = accès facile) : "
        "le trait au milieu est la médiane, la boîte contient la moitié centrale des "
        "exploitations, les traits fins montrent l'étendue des cas extrêmes. "
    )
    only_region = _single_region(df)
    if only_region is not None:
        med = df["score_acces"].median()
        return intro + (
            f"<strong>Constat</strong> : médiane de {med:.0f}/100 pour {only_region}."
        )
    med = df.groupby("region_nom_bdd")["score_acces"].median()
    worst = med.idxmin()
    return intro + (
        f"<strong>Constat</strong> : <strong>{worst}</strong> a la médiane la plus basse "
        f"({med.min():.0f}/100) — c'est la région où l'accès aux marchés est, dans l'ensemble, le "
        "plus difficile."
    )


def chart_couverture_cooperatives(df: pd.DataFrame, radius_km: float) -> str:
    intro = (
        "<strong>Comment lire ce graphique</strong> — pour chaque région, le pourcentage "
        f"d'exploitations n'ayant aucune coopérative recensée à moins de {radius_km:.0f}&nbsp;km. "
        "Plus la barre est longue, plus le réseau coopératif y est clairsemé. "
    )
    only_region = _single_region(df)
    if only_region is not None:
        taux = (df["nb_coop_rayon"] == 0).mean() * 100
        return intro + f"<strong>Constat</strong> : {taux:.0f}% pour {only_region}."
    sans_coop = (df["nb_coop_rayon"] == 0).groupby(df["region_nom_bdd"]).mean().mul(100)
    worst = sans_coop.idxmax()
    return intro + (
        f"<strong>Constat</strong> : <strong>{worst}</strong> est la région la moins bien "
        f"desservie, avec {sans_coop.max():.0f}% des exploitations sans coopérative à proximité."
    )


def table_top_cantons() -> str:
    return (
        "<strong>Comment lire ce tableau</strong> — les 15 cantons où le score d'accès moyen aux "
        "marchés est le plus faible, classés du plus préoccupant au moins préoccupant. La "
        "colonne « Sans coop. proche » indique, pour chaque canton, combien d'exploitations n'ont "
        "aucune coopérative recensée dans le rayon choisi dans la barre latérale : ce sont les "
        "cantons à examiner en priorité pour une intervention (nouveau marché, route d'accès, "
        "appui aux coopératives, etc.)."
    )


# ─────────────────────────────────────────────────────────────────────────
# Résumé global de la page (en bas du dashboard)
# ─────────────────────────────────────────────────────────────────────────
def synthese_globale(
    df: pd.DataFrame, coop_radius_km: float, region_label: str
) -> dict[str, str]:
    """Renvoie les morceaux de texte du résumé général affiché en bas de page.

    Calculé une seule fois à partir des données déjà filtrées par la barre
    latérale, donc cohérent avec tout ce qui est affiché au-dessus dans les
    onglets.
    """
    total = len(df)
    nb_dans_zaap = int(df["dans_zaap"].sum())
    sans_coop = int((df["nb_coop_rayon"] == 0).sum())
    dist_moy = df["dist_marche_km"].mean()
    only_region = _single_region(df)

    if only_region is not None:
        zaap_line = (
            f"<strong>{_fmt(nb_dans_zaap)} exploitations</strong> se trouvent dans une zone "
            f"ZAAP/ZAPB, soit <strong>{_pct(nb_dans_zaap, total):.1f}%</strong> du total pour "
            f"{only_region}. Rappel : ces zones ne sont cartographiées que dans 3 des 5 régions "
            "du pays (Savanes, Plateaux, Centrale) — un taux de 0% ailleurs reflète une absence "
            "de zones dans la donnée source, pas une erreur de calcul."
        )
        acces_line = (
            f"<strong>Accès aux marchés</strong> : distance moyenne de "
            f"<strong>{dist_moy:.1f}&nbsp;km</strong> au marché le plus proche pour {only_region}."
        )
    else:
        best_region_zaap = df.groupby("region_nom_bdd")["dans_zaap"].mean().idxmax()
        worst_region_access = df.groupby("region_nom_bdd")["score_acces"].mean().idxmin()
        zaap_line = (
            f"<strong>{_fmt(nb_dans_zaap)} exploitations</strong> se trouvent dans une zone "
            f"ZAAP/ZAPB, soit <strong>{_pct(nb_dans_zaap, total):.1f}%</strong> du total. La "
            f"région <strong>{best_region_zaap}</strong> présente la meilleure couverture — mais "
            "rappel : ces zones ne sont cartographiées que dans 3 des 5 régions du pays, ce qui "
            "limite structurellement la couverture nationale, indépendamment de tout calcul."
        )
        acces_line = (
            f"<strong>Accès aux marchés</strong> : distance moyenne de "
            f"<strong>{dist_moy:.1f}&nbsp;km</strong> au marché le plus proche. La région "
            f"<strong>{worst_region_access}</strong> affiche le score d'accès le plus faible et "
            "mériterait une attention prioritaire (nouveaux marchés, désenclavement routier)."
        )

    return {
        "intro": (
            f"État des lieux pour <strong>{region_label}</strong>, sur "
            f"<strong>{_fmt(total)} exploitations</strong> analysées."
        ),
        "zaap": zaap_line,
        "acces": acces_line,
        "coop": (
            f"<strong>Réseau coopératif</strong> : <strong>{_fmt(sans_coop)} exploitations</strong> "
            f"({_pct(sans_coop, total):.1f}%) n'ont aucune coopérative recensée dans un rayon de "
            f"{coop_radius_km:.0f}&nbsp;km — un signal pour cibler l'appui à la structuration "
            "coopérative."
        ),
    }
