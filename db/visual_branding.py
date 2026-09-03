"""Identidad visual CTEIB Velocistas aplicada directamente al HTML generado."""

import re
import streamlit as st

_LOGO_HTML = '''
<div class="cteib-logo-wrap">
  <div class="cteib-logo-mark">
    <div class="cteib-logo-top">CTEIB</div>
    <div class="cteib-logo-bottom"><span class="cteib-speed">◀◀◀</span>VELOCISTAS</div>
  </div>
  <div class="cteib-speedlines" aria-hidden="true"></div>
</div>
'''

_EXTRA_CSS = '''
<style>
:root{--cteib-purple:#5b0bb8;--cteib-purple2:#7b22d3;--cteib-pink:#ff0b64;--cteib-ink:#151a2d;--cteib-muted:#7f8493}
.block-container{max-width:980px!important;padding-top:2.7rem!important;padding-bottom:3rem!important}

.cteib-logo-wrap{position:relative;display:flex;align-items:flex-start;justify-content:space-between;min-height:92px;margin:0 0 1rem;overflow:visible}
.cteib-logo-mark{position:relative;z-index:2;line-height:.76;transform:skew(-7deg);padding-top:.2rem}
.cteib-logo-top,.cteib-logo-bottom{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-style:italic;font-weight:950;letter-spacing:-.06em;text-transform:uppercase;white-space:nowrap}
.cteib-logo-top{font-size:clamp(2.65rem,5vw,4rem);color:var(--cteib-purple)}
.cteib-logo-bottom{font-size:clamp(2.05rem,4.2vw,3.2rem);color:var(--cteib-pink);margin-left:.28rem}
.cteib-speed{font-size:.62em;letter-spacing:-.18em;margin-right:.18em}
.cteib-speedlines{position:absolute;right:-4%;top:.55rem;width:48%;height:72px;opacity:.42;background:linear-gradient(168deg,transparent 0 19%,rgba(255,11,100,.42) 20% 22%,transparent 23% 31%,rgba(91,11,184,.30) 32% 34%,transparent 35% 44%,rgba(255,11,100,.28) 45% 47%,transparent 48% 100%);transform:skewX(-24deg)}

.home-hero{margin:.2rem 0 1.55rem}
.home-hello{font-size:clamp(2.25rem,5vw,3.35rem);font-weight:900;letter-spacing:-.045em;line-height:1.02;color:var(--cteib-ink)}
.home-sub{font-size:1.04rem;color:var(--cteib-muted);margin-top:.45rem;font-weight:600}

.home-card{position:relative;display:grid;grid-template-columns:88px 1fr 30px;gap:1rem;align-items:center;border:1px solid rgba(91,11,184,.10);border-radius:24px 24px 0 0;padding:1.35rem 1.45rem 1.2rem;min-height:158px;background:linear-gradient(145deg,#fff 0%,#fff 68%,#fbf8ff 100%);box-shadow:0 12px 30px rgba(34,20,70,.08);margin:0}
.home-card-icon{display:flex;align-items:center;justify-content:center;width:82px;height:82px;border-radius:22px;font-size:2.35rem;background:linear-gradient(145deg,#e8d8ff 0%,#f6deff 100%);box-shadow:inset 0 0 0 1px rgba(91,11,184,.04)}
.home-card[data-tone="pink"] .home-card-icon{background:linear-gradient(145deg,#ffd3e2,#ffe4ef)}
.home-card-copy{min-width:0}.home-card-title{font-size:1.34rem;font-weight:900;letter-spacing:-.025em;color:var(--cteib-ink);line-height:1.12}.home-card-sub{font-size:.96rem;color:var(--cteib-muted);margin-top:.5rem;font-weight:540}.home-card-meta{display:flex;align-items:center;gap:.6rem;margin-top:.9rem}.home-card-num{display:inline-flex;width:34px;height:34px;border-radius:50%;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--cteib-purple),var(--cteib-purple2));color:#fff;font-size:.94rem;font-weight:900;box-shadow:0 6px 15px rgba(91,11,184,.24)}.home-card[data-tone="pink"] .home-card-num{background:linear-gradient(135deg,var(--cteib-pink),#ff477f);box-shadow:0 6px 15px rgba(255,11,100,.22)}
.home-card-arrow{font-size:2rem;font-weight:800;color:var(--cteib-purple);align-self:center;justify-self:end}.home-card[data-tone="pink"] .home-card-arrow{color:var(--cteib-pink)}

/* Convierte el botón real de Streamlit en el pie de la tarjeta. */
div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"]{margin-top:-.05rem!important}
div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"] button{border-radius:0 0 24px 24px!important;min-height:54px!important;border:1px solid rgba(91,11,184,.10)!important;border-top:0!important;background:linear-gradient(90deg,#f5efff,#fbf7ff)!important;color:var(--cteib-purple)!important;font-weight:850!important;text-align:left!important;justify-content:flex-start!important;padding-left:1.45rem!important;box-shadow:0 12px 30px rgba(34,20,70,.08)!important;transition:.15s ease!important}
div[data-testid="stColumn"]:has(.home-card[data-tone="pink"]) div[data-testid="stButton"] button{background:linear-gradient(90deg,#fff0f5,#fff8fa)!important;color:var(--cteib-pink)!important;border-color:rgba(255,11,100,.10)!important}
div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"] button:hover{transform:translateY(-1px);filter:saturate(1.06);border-color:rgba(91,11,184,.24)!important}

.stButton>button{border-radius:15px;min-height:46px;font-weight:750;width:100%;transition:.15s ease}
.stButton>button:hover{transform:translateY(-1px);border-color:rgba(77,7,152,.35)}

@media(max-width:700px){
  .block-container{padding-top:1.8rem!important;padding-left:.75rem!important;padding-right:.75rem!important}
  .cteib-logo-wrap{min-height:70px;margin-bottom:.65rem}.cteib-logo-top{font-size:2.45rem}.cteib-logo-bottom{font-size:1.88rem}.cteib-speedlines{display:none}
  .home-hello{font-size:2.15rem}.home-sub{font-size:.9rem}.home-hero{margin-bottom:1rem}
  div[data-testid="stHorizontalBlock"]{gap:.65rem!important}
  .home-card{grid-template-columns:56px 1fr 20px;gap:.72rem;min-height:126px;padding:.95rem .9rem .85rem;border-radius:19px 19px 0 0}.home-card-icon{width:54px;height:54px;border-radius:16px;font-size:1.65rem}.home-card-title{font-size:1.03rem}.home-card-sub{font-size:.78rem;margin-top:.3rem}.home-card-meta{margin-top:.55rem}.home-card-num{width:28px;height:28px;font-size:.8rem}.home-card-arrow{font-size:1.45rem}
  div[data-testid="stColumn"]:has(.home-card) div[data-testid="stButton"] button{min-height:45px!important;border-radius:0 0 19px 19px!important;padding-left:.9rem!important;font-size:.82rem!important}
}
@media(max-width:430px){
  .cteib-logo-top{font-size:2.05rem}.cteib-logo-bottom{font-size:1.58rem}
  .home-card{grid-template-columns:48px 1fr 18px;padding:.82rem .72rem .72rem;min-height:116px}.home-card-icon{width:46px;height:46px;border-radius:14px;font-size:1.45rem}.home-card-title{font-size:.94rem}.home-card-sub{font-size:.72rem}.home-card-arrow{font-size:1.25rem}
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
    return f'''
<div class="home-card" data-tone="{tone}">
  <div class="home-card-icon">{icon}</div>
  <div class="home-card-copy">
    <div class="home-card-title">{title}</div>
    <div class="home-card-sub">{subtitle}</div>
    <div class="home-card-meta"><span class="home-card-num">{number}</span></div>
  </div>
  <div class="home-card-arrow">→</div>
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
