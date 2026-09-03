"""Capa visual moderna y responsive para las pantallas de inicio."""

import re
import streamlit as st


_LOGO_HTML = r'''
<div style="width:100%;margin:0 0 1.2rem 0;overflow:visible;">
  <svg viewBox="0 0 520 125" role="img" aria-label="CTEIB Velocistas" style="display:block;width:min(430px,82vw);height:auto;overflow:visible;">
    <defs>
      <linearGradient id="p" x1="0" x2="1"><stop offset="0" stop-color="#5a08b6"/><stop offset="1" stop-color="#7e2bd2"/></linearGradient>
      <linearGradient id="r" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient>
    </defs>
    <g transform="skewX(-9)">
      <text x="42" y="58" fill="url(#p)" font-family="Arial Black,Arial,sans-serif" font-size="64" font-weight="900" letter-spacing="-4">CTEIB</text>
      <polygon points="2,78 72,78 72,85 2,85" fill="#f60962"/>
      <polygon points="18,91 72,91 72,98 18,98" fill="#f60962"/>
      <polygon points="34,104 72,104 72,111 34,111" fill="#f60962"/>
      <text x="82" y="111" fill="url(#r)" font-family="Arial Black,Arial,sans-serif" font-size="57" font-weight="900" letter-spacing="-4">VELOCISTAS</text>
    </g>
  </svg>
</div>
'''

_EXTRA_CSS = r'''
<style>
:root{--vp:#5c0ab9;--vp2:#7b25d1;--vr:#fa0a63;--ink:#171b2d;--muted:#858a98}
/* Evita que el logo se meta debajo de la barra superior de Streamlit. */
.block-container{max-width:1040px!important;padding-top:5.4rem!important;padding-bottom:3rem!important}
header[data-testid="stHeader"]{background:rgba(255,255,255,.92)!important}

.home-hero{margin:.1rem 0 1.7rem}
.home-hello{font-size:clamp(2.35rem,5vw,3.5rem);font-weight:900;letter-spacing:-.05em;line-height:1;color:var(--ink)}
.home-sub{font-size:1.08rem;color:var(--muted);margin-top:.55rem;font-weight:650}

/* Tarjetas modernas: el layout se refuerza aquí y también inline. */
.home-card{box-sizing:border-box!important;width:100%!important}
.home-card-icon{flex:0 0 auto!important}
.home-card-copy{min-width:0!important;flex:1 1 auto!important}
.home-card-title{font-size:1.34rem!important;font-weight:900!important;letter-spacing:-.025em!important;color:var(--ink)!important;line-height:1.12!important}
.home-card-sub{font-size:.97rem!important;color:var(--muted)!important;margin-top:.48rem!important;font-weight:560!important}
.home-card-num{display:inline-flex!important;width:34px!important;height:34px!important;border-radius:999px!important;align-items:center!important;justify-content:center!important;color:#fff!important;font-weight:900!important;margin-top:.85rem!important}
.home-card-arrow{font-size:2rem!important;font-weight:800!important;margin-left:auto!important;align-self:center!important}

/* El botón real de Streamlit se integra visualmente como pie de tarjeta. */
div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"]{margin-top:-.5rem!important}
div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"] button{
  min-height:50px!important;border-radius:0 0 23px 23px!important;border:1px solid rgba(92,10,185,.12)!important;border-top:0!important;
  background:linear-gradient(90deg,#f3ecff,#fbf8ff)!important;color:var(--vp)!important;font-weight:850!important;
  justify-content:flex-start!important;padding-left:1.35rem!important;box-shadow:0 13px 28px rgba(33,20,69,.08)!important
}
div[data-testid="stColumn"]:has(.home-card[data-tone="pink"]) div[data-testid="stButton"] button{
  background:linear-gradient(90deg,#fff0f5,#fff8fb)!important;color:var(--vr)!important;border-color:rgba(250,10,99,.12)!important
}

.stButton>button{border-radius:15px;min-height:46px;font-weight:750;transition:.15s ease}
.stButton>button:hover{transform:translateY(-1px)}

@media(max-width:700px){
  .block-container{padding-top:4.6rem!important;padding-left:.75rem!important;padding-right:.75rem!important}
  .home-hero{margin-bottom:1.15rem}.home-hello{font-size:2.15rem}.home-sub{font-size:.92rem}
  div[data-testid="stHorizontalBlock"]{gap:.65rem!important}
  .home-card-title{font-size:1.02rem!important}.home-card-sub{font-size:.78rem!important}.home-card-num{width:28px!important;height:28px!important;font-size:.8rem!important}.home-card-arrow{font-size:1.42rem!important}
  div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"] button{min-height:44px!important;border-radius:0 0 18px 18px!important;font-size:.8rem!important;padding-left:.8rem!important}
}
@media(max-width:430px){
  .block-container{padding-top:4.35rem!important}
  .home-card-title{font-size:.92rem!important}.home-card-sub{font-size:.7rem!important}.home-card-arrow{font-size:1.2rem!important}
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
    icon_bg = "linear-gradient(145deg,#ffd3e4,#ffe6f0)" if pink else "linear-gradient(145deg,#e5d4ff,#f2e7ff)"
    accent = "#fa0a63" if pink else "#5c0ab9"
    badge = "linear-gradient(135deg,#fa0a63,#ff4985)" if pink else "linear-gradient(135deg,#5c0ab9,#7b25d1)"
    return f'''
<div class="home-card" data-tone="{tone}" style="position:relative;display:flex;align-items:center;gap:1.15rem;min-height:158px;padding:1.35rem 1.35rem 1.25rem;border:1px solid rgba(92,10,185,.11);border-radius:23px 23px 0 0;background:linear-gradient(145deg,#fff 0%,#fff 72%,#fbf8ff 100%);box-shadow:0 13px 28px rgba(33,20,69,.08);overflow:hidden;">
  <div class="home-card-icon" style="display:flex;align-items:center;justify-content:center;width:82px;height:82px;border-radius:22px;font-size:2.35rem;background:{icon_bg};">{icon}</div>
  <div class="home-card-copy">
    <div class="home-card-title">{title}</div>
    <div class="home-card-sub">{subtitle}</div>
    <span class="home-card-num" style="background:{badge};box-shadow:0 6px 15px {accent}33;">{number}</span>
  </div>
  <div class="home-card-arrow" style="color:{accent};">→</div>
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
