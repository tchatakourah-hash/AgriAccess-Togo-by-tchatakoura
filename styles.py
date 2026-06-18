"""
Thème visuel AgriAccess Togo — style « Togo AI Lab » (vert / blanc).

Palette et typographie pensées pour un rendu institutionnel, contrasté et
lisible : titres et onglets grands et gras, cartes de métriques en vert
plein (texte blanc) pour un fort contraste, bannière signature en SVG
(pas de pictogrammes emoji, pas de dépendance à des images externes).
"""

# ─────────────────────────────────────────────────────────────────────────
# Palette — Togo AI Lab
# ─────────────────────────────────────────────────────────────────────────
GREEN_DARK = "#0B3D1E"      # vert profond — fond sidebar, texte fort
GREEN_PRIMARY = "#0B6E2E"   # vert principal — boutons, cartes, accents
GREEN_BRIGHT = "#15A94B"    # vert vif — survols, accents secondaires
GOLD_ACCENT = "#F2A900"     # or/jaune récolte — alertes, highlights
CREAM = "#FBF8F1"           # fond de page, doux et chaleureux
WHITE = "#FFFFFF"
INK = "#10241A"             # texte principal, presque noir-vert
RED_ALERT = "#C0392B"
ORANGE_MED = "#E67E22"
BLUE_INFO = "#2980B9"

FONT_DISPLAY = "'Sora', 'Poppins', sans-serif"
FONT_BODY = "'Inter', 'Source Sans Pro', sans-serif"

CUSTOM_CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>

/* ── Fond général ─────────────────────────────────────────────────── */
.stApp {{
    background: {CREAM};
}}
html, body, [class*="css"] {{
    font-family: {FONT_BODY};
    color: {INK};
}}

/* ── Sidebar fixe (ne défile pas avec la page) ───────────────────── */
section[data-testid="stSidebar"] {{
    position: sticky !important;
    top: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
}}

/* ── Titres : grands, gras, vert profond ─────────────────────────── */
h1, h2, h3, h4 {{
    font-family: {FONT_DISPLAY};
    color: {GREEN_DARK};
    font-weight: 800;
    letter-spacing: -0.01em;
}}
h1 {{ font-size: 2.6rem !important; line-height: 1.1; }}
h2 {{ font-size: 1.9rem !important; }}
h3 {{ font-size: 1.4rem !important; }}

/* ── Titres de section critiques (onglets cartes/analyses) ───────────
   Ces titres doivent rester clairement lisibles en toutes circonstances.
   La règle générique h1..h4 ci-dessus suffit normalement, mais on la
   renforce ici avec une sélecteur plus spécifique + !important + la
   propriété -webkit-text-fill-color : certains navigateurs en mode
   sombre forcé (ou des styles internes à Streamlit plus spécifiques)
   peuvent sinon imposer une autre couleur de texte que celle voulue. */
[data-testid="stMarkdownContainer"] h3.dash-title,
h3.dash-title {{
    color: {GREEN_DARK} !important;
    -webkit-text-fill-color: {GREEN_DARK} !important;
    opacity: 1 !important;
}}

[data-testid="stCaptionContainer"] p, .stCaption {{
    font-size: 1.05rem !important;
    color: {INK}cc;
    font-weight: 500;
}}

/* ── Bannière "hero" en en-tête (SVG signature, pas de photo externe) ─ */
.hero-banner {{
    position: relative;
    width: 100%;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 28px rgba(11, 61, 30, 0.25);
}}
.hero-banner svg {{
    width: 100%;
    height: 220px;
    display: block;
}}
.hero-overlay {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 2rem 2.6rem;
}}
.hero-eyebrow {{
    font-family: {FONT_DISPLAY};
    color: {GOLD_ACCENT};
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.85rem;
    margin-bottom: 0.4rem;
}}
.hero-title {{
    font-family: {FONT_DISPLAY};
    color: {WHITE};
    font-weight: 800;
    font-size: 2.8rem;
    line-height: 1.08;
    margin: 0 0 0.5rem 0;
    text-shadow: 0 2px 14px rgba(0,0,0,0.35);
}}
.hero-subtitle {{
    color: {WHITE}e6;
    font-size: 1.08rem;
    font-weight: 500;
    max-width: 640px;
    text-shadow: 0 1px 8px rgba(0,0,0,0.3);
}}
@media (max-width: 900px) {{
    .hero-title {{ font-size: 1.9rem; }}
    .hero-banner svg {{ height: 170px; }}
}}

/* ── Bandeau de repères régionaux (icônes, pas de photos externes) ─── */
.region-strip {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 1.6rem;
}}
.region-strip .region-chip {{
    background: {WHITE};
    border: 2px solid {GREEN_PRIMARY}22;
    border-radius: 12px;
    padding: 16px 10px;
    text-align: center;
    box-shadow: 0 3px 10px rgba(11,61,30,0.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-height: 92px;
}}
.region-strip .region-chip svg {{
    width: 26px; height: 26px;
    color: {GREEN_PRIMARY};
}}
.region-strip .region-chip .region-name {{
    font-family: {FONT_DISPLAY};
    font-weight: 700;
    font-size: 0.88rem;
    color: {GREEN_DARK};
    display: block;
}}
.region-strip .region-chip .region-count {{
    font-size: 0.76rem;
    color: {INK}99;
    font-weight: 600;
}}
@media (max-width: 900px) {{
    .region-strip {{ grid-template-columns: repeat(2, 1fr); }}
}}

/* ── Sidebar : vert profond, texte blanc, gros boutons ───────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {GREEN_DARK} 0%, #0E4D26 100%);
}}
[data-testid="stSidebar"] * {{
    color: {WHITE} !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: {WHITE} !important;
    font-weight: 800 !important;
}}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {{
    color: {WHITE}cc !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: {WHITE}33;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {WHITE};
    border-radius: 10px;
    border: none;
}}
[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: {INK} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] {{
    margin-top: 0.4rem;
}}
[data-testid="stSidebar"] [role="slider"] {{
    background-color: {GOLD_ACCENT} !important;
}}

/* Logo / bloc d'identité dans la sidebar */
.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 18px 0;
    border-bottom: 2px solid {GREEN_BRIGHT}55;
    margin-bottom: 18px;
}}
.sidebar-brand .logo-badge {{
    background: {GOLD_ACCENT};
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.sidebar-brand .logo-badge svg {{
    width: 26px; height: 26px;
    color: {GREEN_DARK};
}}
.sidebar-brand .brand-text {{
    line-height: 1.15;
}}
.sidebar-brand .brand-text .brand-name {{
    font-family: {FONT_DISPLAY};
    font-weight: 800;
    font-size: 1.05rem;
    color: {WHITE};
    display: block;
}}
.sidebar-brand .brand-text .brand-sub {{
    font-size: 0.72rem;
    color: {GOLD_ACCENT};
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}

/* ── Métriques : cartes vert plein, fort contraste, texte blanc ──── */
[data-testid="stMetric"] {{
    background: linear-gradient(135deg, {GREEN_PRIMARY} 0%, {GREEN_DARK} 100%);
    padding: 18px 20px;
    border-radius: 14px;
    border: none;
    box-shadow: 0 6px 18px rgba(11, 61, 30, 0.28);
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    color: {WHITE}e6 !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {WHITE} !important;
    font-family: {FONT_DISPLAY};
    font-weight: 800 !important;
    font-size: 2.1rem !important;
}}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
    color: {GOLD_ACCENT} !important;
}}
/* Variantes de couleur pour différencier les cartes au survol visuel */
.metric-zaap [data-testid="stMetric"] {{
    background: linear-gradient(135deg, {GREEN_BRIGHT} 0%, {GREEN_PRIMARY} 100%);
}}
.metric-info [data-testid="stMetric"] {{
    background: linear-gradient(135deg, {BLUE_INFO} 0%, #1B4F72 100%);
}}
.metric-alert [data-testid="stMetric"] {{
    background: linear-gradient(135deg, {GOLD_ACCENT} 0%, #B97900 100%);
}}

/* ── Onglets : grands, gras, capsule pleine quand actif ──────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    border-bottom: none;
    flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: {WHITE};
    border: 2px solid {GREEN_PRIMARY}33;
    border-radius: 12px;
    padding: 14px 28px;
    font-family: {FONT_DISPLAY};
    font-weight: 700;
    font-size: 1.08rem;
    letter-spacing: 0.01em;
    color: {GREEN_DARK};
    transition: all 0.15s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    border-color: {GREEN_PRIMARY};
    background-color: {GREEN_PRIMARY}0d;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {GREEN_PRIMARY}, {GREEN_DARK}) !important;
    color: {WHITE} !important;
    border-color: {GREEN_DARK} !important;
    box-shadow: 0 4px 14px rgba(11,61,30,0.3);
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: transparent;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 1.4rem;
}}

/* ── Boutons : grands, gras, vert plein ───────────────────────────── */
.stButton > button, .stDownloadButton > button {{
    background: linear-gradient(135deg, {GREEN_PRIMARY}, {GREEN_DARK});
    color: {WHITE};
    font-family: {FONT_DISPLAY};
    font-weight: 700;
    font-size: 1rem;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1.6rem;
    box-shadow: 0 4px 14px rgba(11,61,30,0.25);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(11,61,30,0.35);
    color: {WHITE};
    border: none;
}}

/* Selectbox / slider en zone principale */
[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border-color: {GREEN_PRIMARY}55 !important;
}}
[role="slider"] {{
    background-color: {GREEN_PRIMARY} !important;
}}

/* ── Cartes / encarts informatifs ─────────────────────────────────── */
.info-card {{
    background: {WHITE};
    border-left: 6px solid {GREEN_PRIMARY};
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 3px 12px rgba(11,61,30,0.08);
    margin-bottom: 1rem;
}}
.info-card h4 {{
    margin-top: 0;
    color: {GREEN_DARK};
}}
.legend-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {GREEN_PRIMARY}14;
    color: {GREEN_DARK};
    font-weight: 700;
    font-size: 0.85rem;
    border-radius: 999px;
    padding: 6px 14px;
    margin-right: 8px;
}}
.legend-pill .dot {{
    width: 10px; height: 10px; border-radius: 50%;
}}

/* ── Petits commentaires pédagogiques sous chaque carte/graphique ──── */
.note-box {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: {GREEN_PRIMARY}0d;
    border-left: 4px solid {GREEN_PRIMARY}66;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0 1.2rem 0;
    font-size: 0.92rem;
    line-height: 1.55;
    color: {INK}e6;
}}
.note-box svg {{
    width: 18px; height: 18px;
    flex-shrink: 0;
    margin-top: 2px;
    color: {GREEN_PRIMARY};
}}
.note-box strong {{ color: {GREEN_DARK}; }}

/* ── Onglets de la section "Sources des données" sidebar ─────────── */
.source-line {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.88rem;
    margin: 3px 0;
}}
.source-line svg {{ width: 16px; height: 16px; flex-shrink: 0; }}

/* ── Synthèse / footer ────────────────────────────────────────────── */
.synthesis-card {{
    background: linear-gradient(135deg, {GREEN_DARK}, #0E4D26);
    color: {WHITE};
    border-radius: 18px;
    padding: 26px 30px;
    box-shadow: 0 8px 24px rgba(11,61,30,0.3);
}}
.synthesis-card h3 {{ color: {WHITE} !important; display: flex; align-items: center; gap: 12px; margin-top: 0; }}
.synthesis-card h3 svg {{ width: 30px; height: 30px; flex-shrink: 0; }}
.synthesis-card ul {{ font-size: 1.02rem; line-height: 1.7; }}
.synthesis-card strong {{ color: {GOLD_ACCENT}; }}

/* ── Graphiques Plotly (onglet Analyses) ──────────────────────────── */
/* CORRECTIF — chartes affichées sur fond blanc pur (#FFFFFF) directement
   posé sur le fond crème de la page (#FBF8F1), deux teintes trop proches
   pour se distinguer nettement : aucune bordure, aucune ombre, aucune
   séparation visuelle entre le graphique et la page. Résultat perçu comme
   "flou" / peu lisible. On enveloppe chaque graphique Plotly dans une carte
   blanche nette avec bordure et ombre — même traitement visuel que les
   "info-card" déjà utilisées ailleurs dans le dashboard — pour que le
   contour du graphique se détache clairement du fond, sans toucher au
   contenu ni aux couleurs des courbes/barres elles-mêmes. */
[data-testid="stPlotlyChart"] {{
    background: {WHITE};
    border: 1px solid {GREEN_PRIMARY}22;
    border-radius: 14px;
    padding: 14px 10px 4px 10px;
    box-shadow: 0 3px 14px rgba(11,61,30,0.10);
    margin-bottom: 0.6rem;
}}

footer, [data-testid="stToolbar"] {{ visibility: visible; }}

/* DataFrames */
[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
}}

</style>
"""
