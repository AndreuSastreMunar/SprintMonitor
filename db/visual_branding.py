"""Capa visual moderna y responsive para las pantallas de inicio."""

import re
import streamlit as st


_LOGO_HTML = r'''
<div style="width:100%;margin:2.2rem 0 1.35rem 0;overflow:visible;">
  <svg viewBox="0 0 560 150" role="img" aria-label="CTEIB Velocistas" style="display:block;width:min(470px,86vw);height:auto;overflow:visible;">
    <defs>
      <linearGradient id="p" x1="0" x2="1"><stop offset="0" stop-color="#5a08b6"/><stop offset="1" stop-color="#7e2bd2"/></linearGradient>
      <linearGradient id="r" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient>
    </defs>
    <g transform="translate(8,10) skewX(-9)">
      <text x="48" y="63" fill="url(#p)" font-family="Arial Black,Arial,sans-serif" font-size="68" font-weight="900" letter-spacing="-4">CTEIB</text>
      <polygon points="4,85 84,85 84,93 4,93" fill="#f60962"/>
      <polygon points="20,99 84,99 84,107 20,107" fill="#f60962"/>
      <polygon points="38,113 84,113 84,121 38,121" fill="#f60962"/>
      <text x="94" y="123" fill="url(#r)" font-family="Arial Black,Arial,sans-serif" font-size="60" font-weight="900" letter-spacing="-4">VELOCISTAS</text>
    </g>
  </svg>
</div>
'''

_EXTRA_CSS = r'''
<style>
:root{--vp:#5c0ab9;--vp2:#7b25d1;--vr:#fa0a63;--ink:#151a2d;--muted:#7e8493}
.block-container{max-width:1120px!important;padding-top:7.6rem!important;padding-bottom:3.2rem!important}
header[data-testid="stHeader"]{background:rgba(255,255,255,.96)!important}

.home-hero{margin:.15rem 0 1.9rem}
.home-hello{font-size:clamp(2.5rem,5vw,3.75rem);font-weight:900;letter-spacing:-.05em;line-height:1;color:var(--ink)}
.home-sub{font-size:1.1rem;color:var(--muted);margin-top:.62rem;font-weight:650}

.home-card{box-sizing:border-box!important;width:100%!important}
.home-card-title{font-size:1.45rem!important;font-weight:900!important;letter-spacing:-.025em!important;color:var(--ink)!important;line-height:1.1!important}
.home-card-sub{font-size:1rem!important;color:var(--muted)!important;margin-top:.48rem!important;font-weight:560!important}

/* El botón de Streamlit queda pegado al pie de la tarjeta como en el mockup. */
div[data-testid="stColumn"] div[data-testid="stButton"]{margin-top:-.48rem!important}
div[data-testid="stColumn"] div[data-testid="stButton"] button{
  min-height:54px!important;border-radius:0 0 24px 24px!important;border:1px solid rgba(92,10,185,.12)!important;border-top:0!important;
  background:linear-gradient(90deg,#f4eeff,#fbf8ff)!important;color:var(--vp)!important;font-weight:850!important;
  justify-content:flex-start!important;padding-left:1.55rem!important;box-shadow:0 13px 30px rgba(33,20,69,.09)!important
}
div[data-testid="stColumn"] div[data-testid="stButton"] button:hover{transform:translateY(-1px)!important;filter:saturate(1.05)}

/* Conserva botones normales fuera de las columnas de las tarjetas. */
.stButton>button{font-weight:750;transition:.15s ease}

@media(max-width:700px){
  .block-container{padding-top:6.1rem!important;padding-left:.78rem!important;padding-right:.78rem!important}
  .home-hero{margin-bottom:1.2rem}.home-hello{font-size:2.2rem}.home-sub{font-size:.92rem}
  div[data-testid="stHorizontalBlock"]{gap:.7rem!important}
  .home-card-title{font-size:1.04rem!important}.home-card-sub{font-size:.78rem!important}
  div[data-testid="stColumn"] div[data-testid="stButton"] button{min-height:45px!important;border-radius:0 0 18px 18px!important;font-size:.8rem!important;padding-left:.9rem!important}
}
@media(max-width:430px){
  .block-container{padding-top:5.8rem!important}
  .home-card-title{font-size:.94rem!important}.home-card-sub{font-size:.71rem!important}
}
</style>
'''


def _extract(body, class_name, default=""):
    match = re.search(rf'<div class="{class_name}">(.*?)</div>', body, re.S)
    return match.group(1).strip() if match else default


def _tone_for(title):
    return "pink" if title in {"Wellness", "Ciclo menstrual"} else "purple"


def _modernize_card(body):
    if '<div class="menu-card">' not in body:
        return body
    icon = _extract(body, "menu-icon", "•")
    title = _extract(body, "menu-title", "")
    subtitle = _extract(body, "menu-sub", "")
    number = _extract(body, "menu-num", "")
    tone = _tone_for(title)
    pink = tone == "pink"
    accent = "#fa0a63" if pink else "#5c0ab9"
    icon_bg = "linear-gradient(145deg,#ffd3e3,#ffe8f0)" if pink else "linear-gradient(145deg,#e7d8ff,#f1e8ff)"
    badge_bg = "linear-gradient(135deg,#fa0a63,#ff4c86)" if pink else "linear-gradient(135deg,#5c0ab9,#7b25d1)"
    footer_bg = "linear-gradient(90deg,#fff0f5,#fff8fb)" if pink else "linear-gradient(90deg,#f4eeff,#fbf8ff)"
    border = "rgba(250,10,99,.12)" if pink else "rgba(92,10,185,.12)"
    return f'''
<div class="home-card" data-tone="{tone}" style="position:relative;display:flex;align-items:center;gap:1.35rem;min-height:178px;padding:1.5rem 1.55rem 1.35rem;border:1px solid {border};border-radius:24px 24px 0 0;background:linear-gradient(145deg,#ffffff 0%,#ffffff 72%,#fbf9ff 100%);box-shadow:0 14px 32px rgba(31,20,66,.09);overflow:hidden;">
  <div style="display:flex;flex:0 0 auto;align-items:center;justify-content:center;width:96px;height:96px;border-radius:24px;font-size:2.75rem;background:{icon_bg};box-shadow:inset 0 0 0 1px {border};">{icon}</div>
  <div style="min-width:0;flex:1 1 auto;">
    <div class="home-card-title">{title}</div>
    <div class="home-card-sub">{subtitle}</div>
    <div style="margin-top:.95rem;display:flex;align-items:center;gap:.7rem;">
      <span style="display:inline-flex;width:38px;height:38px;border-radius:999px;align-items:center;justify-content:center;background:{badge_bg};color:#fff;font-weight:900;font-size:1rem;box-shadow:0 7px 16px {accent}33;">{number}</span>
    </div>
  </div>
  <div style="flex:0 0 auto;margin-left:auto;color:{accent};font-size:2.15rem;font-weight:900;line-height:1;">→</div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:10px;background:{footer_bg};opacity:.75;"></div>
</div>
'''


def _modernize_hero(body):
    if '<div class="hero">' not in body:
        return body
    hello = _extract(body, "hello", "")
    sub = _extract(body, "sub", "")
    return _LOGO_HTML + f'''
<div class="home-hero">
  <div class="home-hello">{hello}</div>
  <div class="home-sub">{sub}</div>
</div>
'''


def install_visual_branding():
    if getattr(st, "_cteib_visual_branding_installed", False):
        return
    original_markdown = st.markdown
    injected = {"done": False}

    def markdown_with_brand(body, *args, **kwargs):
        if not injected["done"]:
            original_markdown(_EXTRA_CSS, unsafe_allow_html=True)
            injected["done"] = True
        if isinstance(body, str):
            if '<div class="hero">' in body:
                body = _modernize_hero(body)
                kwargs["unsafe_allow_html"] = True
            elif '<div class="menu-card">' in body:
                body = _modernize_card(body)
                kwargs["unsafe_allow_html"] = True
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_brand
    st._cteib_visual_branding_installed = True
