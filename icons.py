"""
Icônes SVG inline pour AgriAccess Togo.

Remplace tous les emojis ("autocollants") par des pictogrammes vectoriels
cohérents avec l'identité visuelle du dashboard. Chaque icône utilise
`currentColor` pour hériter de la couleur définie en CSS par le conteneur
parent — aucune dépendance réseau, rendu identique partout.
"""

LEAF = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 40C8 24 20 8 40 8c0 20-16 32-32 32Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M11 37C18 28 26 20 36 13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>"""

FARM = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 41h36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M10 41V23l8-7 8 7v18" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M26 41V17l8-6 8 6v24" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="18" cy="31" r="2.2" fill="currentColor"/><circle cx="34" cy="27" r="2.2" fill="currentColor"/></svg>"""

ZAAP = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="6" width="16" height="16" rx="2" stroke="currentColor" stroke-width="3"/><rect x="26" y="6" width="16" height="16" rx="2" stroke="currentColor" stroke-width="3" opacity="0.5"/><rect x="6" y="26" width="16" height="16" rx="2" stroke="currentColor" stroke-width="3" opacity="0.5"/><rect x="26" y="26" width="16" height="16" rx="2" stroke="currentColor" stroke-width="3"/></svg>"""

MARKET = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 18l3-9h26l3 9" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M6 18h36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M10 18v20a2 2 0 0 0 2 2h24a2 2 0 0 0 2-2V18" stroke="currentColor" stroke-width="3"/><path d="M19 40V28h10v12" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>"""

COOP = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="16" cy="16" r="6" stroke="currentColor" stroke-width="3"/><circle cx="32" cy="16" r="6" stroke="currentColor" stroke-width="3"/><circle cx="24" cy="33" r="6" stroke="currentColor" stroke-width="3"/><path d="M19 20l7 9M29 20l-7 9" stroke="currentColor" stroke-width="2.5" opacity="0.7"/></svg>"""

MAP_PIN = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 44s14-13.5 14-24A14 14 0 0 0 10 20c0 10.5 14 24 14 24Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><circle cx="24" cy="20" r="5" stroke="currentColor" stroke-width="3"/></svg>"""

HEATMAP = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 4c4 8-4 10-4 16a8 8 0 0 0 16 0c0-4-2-6-4-9 1 5-2 7-4 5 1-6-2-9-4-12Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M16 30a8 8 0 0 0 16 0" stroke="currentColor" stroke-width="3"/></svg>"""

TARGET = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="16" stroke="currentColor" stroke-width="3"/><circle cx="24" cy="24" r="9" stroke="currentColor" stroke-width="3"/><circle cx="24" cy="24" r="2.5" fill="currentColor"/></svg>"""

CHART_BARS = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8 42V18M19 42V24M30 42V8M41 42V30" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M6 42h38" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>"""

NOTE = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="6" width="32" height="36" rx="2.5" stroke="currentColor" stroke-width="3"/><path d="M15 16h18M15 24h18M15 32h12" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>"""

DATABASE = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="24" cy="10" rx="16" ry="6" stroke="currentColor" stroke-width="3"/><path d="M8 10v28c0 3.3 7.2 6 16 6s16-2.7 16-6V10" stroke="currentColor" stroke-width="3"/><path d="M8 24c0 3.3 7.2 6 16 6s16-2.7 16-6" stroke="currentColor" stroke-width="3"/></svg>"""

SEEDLING = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 44V28" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M24 28C24 16 12 14 8 14c0 12 8 16 16 14Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M24 24C24 14 34 12 40 12c0 11-7.5 15-16 12Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>"""

NURSERY = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 44h20M16 44V30M32 44V30" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><rect x="10" y="30" width="28" height="6" rx="1.5" stroke="currentColor" stroke-width="3"/><path d="M24 30V14" stroke="currentColor" stroke-width="3"/><path d="M24 18c-6-1-9-6-9-10 6 0 10 3 11 8" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M24 18c6-1 9-6 9-10-6 0-10 3-11 8" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/></svg>"""


def chip(svg: str) -> str:
    """Petit conteneur span pour aligner une icône inline avec du texte."""
    return f'<span style="display:inline-flex;width:1em;height:1em;vertical-align:-0.15em;">{svg}</span>'
