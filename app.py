"""
AgriAccess Togo — Dashboard interactif
Data Challenge Agriculture | Défi 1 — Géographie du tissu agricole au Togo

Soumission : 22/06/2026
"""
from __future__ import annotations

import re

import streamlit as st
from streamlit_folium import st_folium

import charts
import icons
import narration

try:
    import maps
    from analytics import compute_all_indicators, aggregate_by_canton
    from data_loader import load_all_layers, get_region_list, filter_by_region
except ImportError as e:
    st.error(
        "Erreur de chargement des dépendances géospatiales (geopandas/pyogrio/fiona). "
        "Sur Streamlit Cloud, cela vient presque toujours de bibliothèques système "
        "manquantes (GDAL/GEOS/PROJ). Vérifiez qu'un fichier `packages.txt` contenant "
        "`gdal-bin`, `libgdal-dev`, `libgeos-dev` et `libproj-dev` est bien présent à la "
        "racine du dépôt, puis relancez le déploiement (Manage app → Reboot)."
    )
    st.exception(e)
    st.stop()

from styles import CUSTOM_CSS


def html(template: str) -> str:
    """Aplatit un template HTML multi-lignes en une seule ligne avant de le
    passer à st.markdown(unsafe_allow_html=True).

    st.markdown() fait d'abord passer le texte par un moteur Markdown avant
    d'autoriser le HTML brut : toute ligne indentée de 4 espaces ou plus
    (ce qui arrive très facilement avec des f-strings indentées comme dans
    ce fichier) est alors interprétée comme un bloc de code et affichée
    telle quelle au lieu d'être rendue — c'est le bug du HTML visible à
    l'écran. Supprimer les retours à la ligne et l'indentation élimine
    totalement le problème.
    """
    return re.sub(r"\s*\n\s*", " ", template.strip())


def note(text: str) -> None:
    """Affiche un petit commentaire pédagogique sous une carte ou un graphique.

    Toujours la même mise en forme (icône + encadré vert clair) pour que ces
    commentaires soient visuellement reconnaissables partout sur le
    dashboard, sans répéter le balisage à chaque appel.
    """
    st.markdown(html(f'<div class="note-box">{icons.NOTE}<div>{text}</div></div>'), unsafe_allow_html=True)


def section_title(text: str) -> None:
    """Affiche un titre de section (équivalent à st.subheader) avec une
    couleur verte forcée explicitement en CSS (classe `dash-title`), pour
    garantir sa lisibilité quel que soit le thème du navigateur ou de
    Streamlit — voir la règle correspondante dans styles.py.
    """
    st.markdown(html(f'<h3 class="dash-title">{text}</h3>'), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# Configuration de page
# ─────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriAccess Togo",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# Bannière "hero" — illustration SVG signature (pas de photo externe :
# rendu garanti, aucune dépendance réseau, aucun risque de droits d'auteur)
# ─────────────────────────────────────────────────────────────────────────
HERO_SVG = """
<svg viewBox="0 0 1400 280" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B3D1E"/>
      <stop offset="100%" stop-color="#0E5C2C"/>
    </linearGradient>
    <linearGradient id="hillGrad1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#15A94B"/>
      <stop offset="100%" stop-color="#0B6E2E"/>
    </linearGradient>
    <linearGradient id="hillGrad2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1F8A40"/>
      <stop offset="100%" stop-color="#0B6E2E"/>
    </linearGradient>
    <linearGradient id="sunGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFD566"/>
      <stop offset="100%" stop-color="#F2A900"/>
    </linearGradient>
  </defs>
  <rect width="1400" height="280" fill="url(#skyGrad)"/>
  <circle cx="1240" cy="68" r="48" fill="url(#sunGrad)" opacity="0.95"/>
  <path d="M0,175 Q200,120 420,165 T860,145 T1400,170 V280 H0 Z" fill="url(#hillGrad1)" opacity="0.55"/>
  <path d="M0,215 Q180,185 380,208 T760,198 T1140,213 T1400,203 V280 H0 Z" fill="url(#hillGrad2)"/>
  <g stroke="#0B3D1E" stroke-width="3" opacity="0.3">
    <path d="M0,232 Q200,202 420,226 T860,216 T1400,226" fill="none"/>
    <path d="M0,250 Q200,222 420,244 T860,236 T1400,244" fill="none"/>
    <path d="M0,267 Q200,241 420,261 T860,255 T1400,261" fill="none"/>
  </g>
  <g fill="#0B3D1E" opacity="0.85">
    <g transform="translate(150,150)">
      <rect x="-4" y="0" width="8" height="55" rx="3"/>
      <path d="M0,0 C-30,-10 -45,-30 -50,-45 C-30,-35 -10,-20 0,0 Z"/>
      <path d="M0,0 C30,-10 45,-30 50,-45 C30,-35 10,-20 0,0 Z"/>
      <path d="M0,0 C-15,-25 -15,-45 -8,-60 C2,-45 5,-25 0,0 Z"/>
    </g>
    <g transform="translate(1020,158) scale(0.85)">
      <rect x="-4" y="0" width="8" height="55" rx="3"/>
      <path d="M0,0 C-30,-10 -45,-30 -50,-45 C-30,-35 -10,-20 0,0 Z"/>
      <path d="M0,0 C30,-10 45,-30 50,-45 C30,-35 10,-20 0,0 Z"/>
      <path d="M0,0 C-15,-25 -15,-45 -8,-60 C2,-45 5,-25 0,0 Z"/>
    </g>
  </g>
</svg>
"""

st.markdown(
    html(
        f"""
        <div class="hero-banner">
            {HERO_SVG}
            <div class="hero-overlay">
                <div class="hero-eyebrow">Togo AI Lab · Data Challenge Agriculture</div>
                <div class="hero-title">AgriAccess Togo</div>
                <div class="hero-subtitle">
                    Tableau de bord géographique du tissu agricole togolais — exploitations,
                    ZAAP, marchés et coopératives, région par région.
                </div>
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────
# Chargement des données
# ─────────────────────────────────────────────────────────────────────────
with st.spinner("Chargement des couches géographiques…"):
    layers = load_all_layers()

exploitations_raw = layers["exploitations"]
marches = layers["marches"]
zaap = layers["zaap"]
cooperatives = layers["cooperatives"]

# Bandeau de repères régionaux (icône + nombre d'exploitations par région)
region_counts = (
    exploitations_raw["region_nom_bdd"].value_counts().reindex(get_region_list(exploitations_raw))
)
st.markdown(
    '<div class="region-strip">' + "".join(
        f'<div class="region-chip">{icons.MAP_PIN}'
        f'<span class="region-name">{region}</span>'
        f'<span class="region-count">{int(count):,} exploitations</span></div>'
        for region, count in region_counts.items()
    ) + "</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────
# Barre latérale — identité + filtres
# ─────────────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    html(
        f"""
        <div class="sidebar-brand">
            <div class="logo-badge">{icons.LEAF}</div>
            <div class="brand-text">
                <span class="brand-name">AgriAccess Togo</span>
                <span class="brand-sub">Togo AI Lab</span>
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.sidebar.header("Filtres")

regions = ["Toutes les régions"] + get_region_list(exploitations_raw)
selected_region = st.sidebar.selectbox("Région", regions)

coop_radius = st.sidebar.slider(
    "Rayon de recherche des coopératives (km)",
    min_value=5,
    max_value=25,
    value=10,
    step=5,
    help="Distance utilisée pour compter les coopératives à proximité de chaque exploitation.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Sources des données**")
st.sidebar.markdown(
    '<div class="source-line">' + icons.DATABASE + ' <span>geodata.gouv.tg · opendata.gouv.tg</span></div>'
    f'<div class="source-line">{icons.FARM}<span>{len(exploitations_raw):,} exploitations</span></div>'
    f'<div class="source-line">{icons.MARKET}<span>{len(marches):,} marchés</span></div>'
    f'<div class="source-line">{icons.ZAAP}<span>{len(zaap):,} zones ZAAP/ZAPB</span></div>'
    f'<div class="source-line">{icons.COOP}<span>{len(cooperatives):,} coopératives</span></div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────
# Calcul des indicateurs (mis en cache, recalculé seulement si le rayon change)
# ─────────────────────────────────────────────────────────────────────────
with st.spinner("Calcul des indicateurs d'accès et de couverture…"):
    exploitations = compute_all_indicators(
        exploitations_raw, marches, zaap, cooperatives, coop_radius
    )

exploitations_filtered = filter_by_region(exploitations, selected_region)
marches_filtered = filter_by_region(marches, selected_region)
cooperatives_filtered = filter_by_region(cooperatives, selected_region)
zaap_filtered = filter_by_region(zaap, selected_region)
canton_stats = aggregate_by_canton(exploitations_filtered)

region_label = selected_region if selected_region != "Toutes les régions" else "tout le Togo"
st.markdown(
    '<style>.view-title-pin svg{width:22px;height:22px;display:block;}</style>'
    f'<h3 style="display:flex;align-items:center;gap:10px;color:#000000;">'
    f'<span class="view-title-pin" style="display:inline-flex;color:#000000;">{icons.MAP_PIN}</span>'
    f'Vue : {region_label}</h3>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────
# Métriques clés
# ─────────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Exploitations", f"{len(exploitations_filtered):,}")

nb_dans_zaap = int(exploitations_filtered["dans_zaap"].sum())
with col2:
    st.markdown('<div class="metric-zaap">', unsafe_allow_html=True)
    st.metric(
        "Nb exploitations dans ZAAP",
        f"{nb_dans_zaap:,}",
        help="Nombre d'exploitations dont le centroïde se situe à l'intérieur d'une zone ZAAP/ZAPB.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

col3.metric("Couverture ZAAP", f"{exploitations_filtered['dans_zaap'].mean() * 100:.1f}%")

with col4:
    st.markdown('<div class="metric-info">', unsafe_allow_html=True)
    st.metric(
        "Distance moyenne marché",
        f"{exploitations_filtered['dist_marche_km'].mean():.1f} km",
    )
    st.markdown("</div>", unsafe_allow_html=True)

sans_coop = (exploitations_filtered["nb_coop_rayon"] == 0).sum()
with col5:
    st.markdown('<div class="metric-alert">', unsafe_allow_html=True)
    st.metric(
        f"Sans coopérative à {coop_radius} km",
        f"{sans_coop:,}",
        help="Nombre d'exploitations n'ayant aucune coopérative recensée dans le rayon choisi.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────
# Onglets cartographiques
# ─────────────────────────────────────────────────────────────────────────
tab_carte, tab_densite, tab_zaap, tab_analyses = st.tabs(
    ["CARTE D'ACCÈS", "DENSITÉ", "COUVERTURE ZAAP", "ANALYSES"]
)

with tab_carte:
    section_title("Score d'accès aux marchés par exploitation")
    st.markdown(
        '<span class="legend-pill"><span class="dot" style="background:#0B6E2E"></span>Bon accès</span>'
        '<span class="legend-pill"><span class="dot" style="background:#E67E22"></span>Accès moyen</span>'
        '<span class="legend-pill"><span class="dot" style="background:#C0392B"></span>Accès difficile</span>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Utilisez le sélecteur de calques en haut à droite de la carte pour afficher ou masquer "
        "les exploitations, ZAAP, marchés et coopératives. Filtrez par région dans la barre latérale "
        "pour afficher le détail par exploitation."
    )
    if selected_region == "Toutes les régions":
        st.info(
            f"Vue nationale : affichage agrégé par canton ({len(canton_stats)} cantons). "
            "Sélectionnez une région pour voir le détail par exploitation."
        )
    m = maps.build_carte_acces(
        exploitations_filtered,
        marches_filtered,
        zaap_filtered,
        cooperatives_filtered,
        canton_stats,
        selected_region,
        coop_radius,
    )
    # PERFORMANCE — returned_objects=[] : par défaut, st_folium renvoie à
    # Streamlit l'état complet de la carte (centre, zoom, dernier clic...) à
    # chaque interaction, ce qui force un aller-retour navigateur ⇄ serveur
    # et peut redéclencher un rendu complet de la page. Cette valeur de
    # retour n'est jamais utilisée ici : la désactiver supprime cet
    # aller-retour inutile et rend l'affichage de la carte plus réactif.
    st_folium(m, width=None, height=520, key="map_acces", use_container_width=True, returned_objects=[])
    note(narration.carte_acces(exploitations_filtered))

with tab_densite:
    section_title("Densité spatiale des exploitations agricoles")
    st.markdown(
        '<span class="legend-pill"><span class="dot" style="background:#FDE9A8"></span>Faible</span>'
        '<span class="legend-pill"><span class="dot" style="background:#F2A900"></span>Modérée</span>'
        '<span class="legend-pill"><span class="dot" style="background:#E67E22"></span>Élevée</span>'
        '<span class="legend-pill"><span class="dot" style="background:#C0392B"></span>Très élevée</span>',
        unsafe_allow_html=True,
    )
    st.caption("Chaque bulle représente une zone du territoire, colorée et dimensionnée selon le nombre d'exploitations qu'elle contient.")
    m_heat = maps.build_carte_densite(exploitations_filtered, zaap_filtered, selected_region)
    st_folium(m_heat, width=None, height=520, key="map_densite", use_container_width=True, returned_objects=[])
    note(narration.carte_densite(exploitations_filtered))

with tab_zaap:
    section_title("Exploitations situées dans une zone ZAAP / ZAPB")
    st.markdown(
        '<span class="legend-pill"><span class="dot" style="background:#0B6E2E"></span>Dans ZAAP/ZAPB</span>'
        '<span class="legend-pill"><span class="dot" style="background:#C0392B"></span>Hors zone</span>',
        unsafe_allow_html=True,
    )
    m_zaap = maps.build_carte_zaap(exploitations_filtered, zaap_filtered, selected_region)
    st_folium(m_zaap, width=None, height=520, key="map_zaap", use_container_width=True, returned_objects=[])
    note(narration.carte_zaap(exploitations_filtered))

with tab_analyses:
    section_title("Analyses comparatives")

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(charts.exploitations_par_region(exploitations_filtered), use_container_width=True)
        note(narration.chart_exploitations_par_region(exploitations_filtered))
    with col_b:
        st.plotly_chart(charts.couverture_zaap_par_region(exploitations_filtered), use_container_width=True)
        note(narration.chart_couverture_zaap_par_region(exploitations_filtered))

    col_c, col_d = st.columns(2)
    with col_c:
        st.plotly_chart(charts.distribution_distance_marche(exploitations_filtered), use_container_width=True)
        note(narration.chart_distribution_distance(exploitations_filtered))
    with col_d:
        st.plotly_chart(charts.score_acces_par_region(exploitations_filtered), use_container_width=True)
        note(narration.chart_score_acces_par_region(exploitations_filtered))

    st.plotly_chart(charts.couverture_cooperatives(exploitations_filtered, coop_radius), use_container_width=True)
    note(narration.chart_couverture_cooperatives(exploitations_filtered, coop_radius))

    st.markdown("#### Cantons les moins bien desservis")
    st.caption("Classés par score d'accès aux marchés le plus faible.")
    st.dataframe(charts.top_cantons_table(canton_stats), use_container_width=True, hide_index=True)
    note(narration.table_top_cantons())

# ─────────────────────────────────────────────────────────────────────────
# Résumé général de la page
# ─────────────────────────────────────────────────────────────────────────
st.markdown("---")

synth = narration.synthese_globale(exploitations_filtered, coop_radius, region_label)

st.markdown(
    html(
        f"""
        <div class="synthesis-card">
            <h3>{icons.NOTE} Résumé général de la page — état des lieux</h3>
            <p style="margin-top:-6px;opacity:0.9;">{synth['intro']}
                Ce résumé reprend, en quelques phrases, les constats détaillés dans les
                onglets ci-dessus.</p>
            <ul>
                <li>{synth['zaap']}</li>
                <li>{synth['acces']}</li>
                <li>{synth['coop']}</li>
            </ul>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.caption(
    "Données : geodata.gouv.tg / opendata.gouv.tg — Togo AI Lab Data Challenge Agriculture, Défi 1."
)
