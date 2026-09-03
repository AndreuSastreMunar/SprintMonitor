"""Última capa visual del login, instalada después de todos los parches de db."""

import streamlit as st

_LOGIN_FINAL_CSS = r'''
<style>
.block-container:has(.cteib-login-final){max-width:560px!important;padding-top:5.8rem!important;padding-bottom:2.5rem!important}
.cteib-login-final{position:relative;margin:0 0 1rem}
.cteib-login-final:after{content:"";position:absolute;z-index:-1;right:-34vw;top:-4rem;width:82vw;height:170px;opacity:.55;background:linear-gradient(168deg,transparent 0 16%,rgba(255,11,104,.18) 17% 21%,transparent 22% 29%,rgba(101,45,210,.13) 30% 34%,transparent 35% 42%,rgba(255,11,104,.10) 43% 47%,transparent 48%);transform:skewX(-18deg)}
.cteib-login-logo{width:min(400px,88vw);margin:0 auto .85rem}
.cteib-login-logo svg{display:block;width:100%;height:auto;overflow:visible}
.cteib-login-copy{font-size:1.08rem;line-height:1.45;color:#7d8392;font-weight:560;margin:.1rem 0 1rem}
.block-container:has(.cteib-login-final) div[data-testid="stTabs"] button[role="tab"]{font-size:1rem!important;font-weight:800!important;padding:.7rem .75rem!important}
.block-container:has(.cteib-login-final) div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,#5b12c7,#ff0b68)!important;height:3px!important;border-radius:999px!important}
.block-container:has(.cteib-login-final) div[data-testid="stForm"]{border:1px solid rgba(91,18,199,.08)!important;border-radius:28px!important;padding:1.3rem 1.2rem 1.2rem!important;background:#fff!important;box-shadow:0 18px 50px rgba(53,31,101,.11)!important;margin-top:.55rem!important}
.block-container:has(.cteib-login-final) div[data-testid="stTextInput"] label{font-size:1rem!important;font-weight:850!important;color:#10172b!important;margin-bottom:.35rem!important}
.block-container:has(.cteib-login-final) div[data-testid="stTextInput"] input{min-height:58px!important;border-radius:18px!important;background:linear-gradient(90deg,#f6f3fb,#f3f1f8)!important;border:1px solid transparent!important;font-size:1rem!important;padding-left:1rem!important}
.block-container:has(.cteib-login-final) div[data-testid="stTextInput"] input:focus{border-color:rgba(91,18,199,.28)!important;box-shadow:0 0 0 3px rgba(91,18,199,.08)!important}
.block-container:has(.cteib-login-final) div[data-testid="stForm"] button{min-height:58px!important;border-radius:18px!important;border:0!important;background:linear-gradient(100deg,#5b12c7 0%,#a22bc1 52%,#ff0b68 100%)!important;color:#fff!important;font-size:1.05rem!important;font-weight:900!important;box-shadow:0 12px 26px rgba(120,25,166,.22)!important;margin-top:.35rem!important}
.block-container:has(.cteib-login-final) div[data-testid="stForm"] button:hover{transform:translateY(-1px)!important;filter:saturate(1.05)!important}
@media(max-width:640px){.block-container:has(.cteib-login-final){padding-top:4.8rem!important;padding-left:1rem!important;padding-right:1rem!important;max-width:520px!important}.cteib-login-logo{width:min(330px,86vw)}.cteib-login-copy{font-size:.98rem}.block-container:has(.cteib-login-final) div[data-testid="stForm"]{border-radius:24px!important;padding:1rem .95rem!important}.block-container:has(.cteib-login-final) div[data-testid="stTextInput"] input,.block-container:has(.cteib-login-final) div[data-testid="stForm"] button{min-height:54px!important;border-radius:16px!important}}
</style>
'''

_LOGIN_FINAL_HTML = r'''
<div class="cteib-login-final">
  <div class="cteib-login-logo">
    <svg viewBox="0 0 520 135" role="img" aria-label="CTEIB Velocistas">
      <defs>
        <linearGradient id="flp" x1="0" x2="1"><stop offset="0" stop-color="#5510bc"/><stop offset="1" stop-color="#7d2bd6"/></linearGradient>
        <linearGradient id="flr" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient>
      </defs>
      <g transform="translate(8 7) skewX(-9)">
        <text x="55" y="58" fill="url(#flp)" font-family="Arial Black,Arial,sans-serif" font-size="64" font-weight="900" letter-spacing="-4">CTEIB</text>
        <polygon points="10,79 84,79 84,86 10,86" fill="#f60962"/>
        <polygon points="27,92 84,92 84,99 27,99" fill="#f60962"/>
        <polygon points="44,105 84,105 84,112 44,112" fill="#f60962"/>
        <text x="94" y="113" fill="url(#flr)" font-family="Arial Black,Arial,sans-serif" font-size="55" font-weight="900" letter-spacing="-4">VELOCISTAS</text>
      </g>
    </svg>
  </div>
  <div class="cteib-login-copy">Entrenamiento, bienestar, competición y evolución.</div>
</div>
'''


def install_login_final_patch():
    if getattr(st, "_cteib_login_final_patch", False):
        return
    base_markdown = st.markdown
    css_done = {"value": False}

    def markdown(body, *args, **kwargs):
        if not css_done["value"]:
            base_markdown(_LOGIN_FINAL_CSS, unsafe_allow_html=True)
            css_done["value"] = True
        if isinstance(body, str) and 'SPRINT MONITOR' in body and '100 / 200 m' in body and 'Entrenamiento, bienestar, competición y evolución.' in body:
            body = _LOGIN_FINAL_HTML
            kwargs["unsafe_allow_html"] = True
        return base_markdown(body, *args, **kwargs)

    st.markdown = markdown
    st._cteib_login_final_patch = True
