"""Diseño móvil moderno para la pantalla de acceso de Sprint Monitor."""

import streamlit as st

_LOGIN_CSS = r'''
<style>
:root{--login-purple:#5b12c7;--login-purple2:#7a28d7;--login-pink:#ff0b68;--login-ink:#10172b;--login-muted:#7e8495}

/* Solo se activa cuando existe .login-branding */
.block-container:has(.login-branding){max-width:620px!important;padding-top:6.8rem!important;padding-bottom:2.5rem!important}

.login-branding{position:relative;margin:0 0 1.15rem;overflow:visible}
.login-branding:after{content:"";position:absolute;z-index:-1;right:-22vw;top:-2.2rem;width:70vw;height:135px;opacity:.58;background:linear-gradient(168deg,transparent 0 18%,rgba(255,11,104,.20) 19% 23%,transparent 24% 31%,rgba(113,66,225,.14) 32% 36%,transparent 37% 45%,rgba(255,11,104,.12) 46% 50%,transparent 51%);transform:skewX(-18deg)}
.login-logo{width:min(410px,88vw);margin:0 auto .95rem;overflow:visible}
.login-logo svg{display:block;width:100%;height:auto;overflow:visible}
.login-tagline{font-size:1.18rem;line-height:1.48;color:var(--login-muted);font-weight:560;margin:.15rem 0 1.15rem;text-align:left}

/* Tabs */
.block-container:has(.login-branding) div[data-testid="stTabs"] button[role="tab"]{font-size:1.02rem!important;font-weight:800!important;padding:.7rem .75rem!important}
.block-container:has(.login-branding) div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--login-purple),var(--login-pink))!important;height:3px!important;border-radius:999px!important}

/* Formulario como tarjeta móvil */
.block-container:has(.login-branding) div[data-testid="stForm"]{border:1px solid rgba(91,18,199,.08)!important;border-radius:28px!important;padding:1.35rem 1.25rem 1.25rem!important;background:rgba(255,255,255,.97)!important;box-shadow:0 18px 50px rgba(53,31,101,.11)!important;margin-top:.65rem!important}
.block-container:has(.login-branding) div[data-testid="stTextInput"] label{font-size:1rem!important;font-weight:850!important;color:var(--login-ink)!important;margin-bottom:.35rem!important}
.block-container:has(.login-branding) div[data-testid="stTextInput"] input{min-height:58px!important;border-radius:18px!important;background:linear-gradient(90deg,#f6f3fb,#f3f1f8)!important;border:1px solid transparent!important;font-size:1rem!important;padding-left:1rem!important}
.block-container:has(.login-branding) div[data-testid="stTextInput"] input:focus{border-color:rgba(91,18,199,.28)!important;box-shadow:0 0 0 3px rgba(91,18,199,.08)!important}

/* Botón principal */
.block-container:has(.login-branding) div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
.block-container:has(.login-branding) div[data-testid="stForm"] button{min-height:58px!important;border-radius:18px!important;border:0!important;background:linear-gradient(100deg,var(--login-purple) 0%,#a22bc1 52%,var(--login-pink) 100%)!important;color:white!important;font-size:1.05rem!important;font-weight:900!important;box-shadow:0 12px 26px rgba(120,25,166,.22)!important;margin-top:.35rem!important}
.block-container:has(.login-branding) div[data-testid="stForm"] button:hover{transform:translateY(-1px)!important;filter:saturate(1.05)!important}

/* Texto de apoyo */
.login-benefit{display:flex;align-items:center;gap:1rem;margin:1.1rem 0 .6rem;padding:1.05rem 1.1rem;border-radius:22px;background:linear-gradient(135deg,#f7f1ff,#fff5fa);border:1px solid rgba(91,18,199,.06)}
.login-benefit-icon{display:flex;align-items:center;justify-content:center;flex:0 0 58px;width:58px;height:58px;border-radius:18px;background:linear-gradient(145deg,#eadcff,#f6e8ff);font-size:1.85rem}
.login-benefit-title{font-size:1rem;font-weight:900;color:var(--login-ink)}
.login-benefit-copy{font-size:.88rem;color:var(--login-muted);line-height:1.4;margin-top:.18rem}
.login-secure{text-align:center;color:var(--login-muted);font-size:.82rem;margin-top:.75rem}

@media(max-width:640px){
  .block-container:has(.login-branding){padding-top:5.7rem!important;padding-left:1rem!important;padding-right:1rem!important;max-width:520px!important}
  .login-logo{width:min(340px,86vw);margin-bottom:.8rem}.login-tagline{font-size:1rem;margin-bottom:.85rem}
  .block-container:has(.login-branding) div[data-testid="stForm"]{border-radius:24px!important;padding:1.05rem .95rem 1rem!important}
  .block-container:has(.login-branding) div[data-testid="stTextInput"] input{min-height:54px!important;border-radius:16px!important}
  .block-container:has(.login-branding) div[data-testid="stForm"] button{min-height:54px!important;border-radius:16px!important}
}
</style>
'''

_LOGIN_HTML = r'''
<div class="login-branding">
  <div class="login-logo">
    <svg viewBox="0 0 520 135" role="img" aria-label="CTEIB Velocistas">
      <defs>
        <linearGradient id="lp" x1="0" x2="1"><stop offset="0" stop-color="#5510bc"/><stop offset="1" stop-color="#7d2bd6"/></linearGradient>
        <linearGradient id="lr" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient>
      </defs>
      <g transform="translate(8 7) skewX(-9)">
        <text x="55" y="58" fill="url(#lp)" font-family="Arial Black,Arial,sans-serif" font-size="64" font-weight="900" letter-spacing="-4">CTEIB</text>
        <polygon points="10,79 84,79 84,86 10,86" fill="#f60962"/>
        <polygon points="27,92 84,92 84,99 27,99" fill="#f60962"/>
        <polygon points="44,105 84,105 84,112 44,112" fill="#f60962"/>
        <text x="94" y="113" fill="url(#lr)" font-family="Arial Black,Arial,sans-serif" font-size="55" font-weight="900" letter-spacing="-4">VELOCISTAS</text>
      </g>
    </svg>
  </div>
  <div class="login-tagline">Entrenamiento, bienestar, competición y evolución.</div>
</div>
'''

_BENEFIT_HTML = r'''
<div class="login-benefit">
  <div class="login-benefit-icon">🏃</div>
  <div><div class="login-benefit-title">Mejora cada día</div><div class="login-benefit-copy">Controla tus entrenamientos, cuida tu bienestar y sigue tu evolución.</div></div>
</div>
<div class="login-secure">🛡️ Tus datos están protegidos</div>
'''


def install_login_branding():
    if getattr(st, "_sprint_login_branding_installed", False):
        return
    original_markdown = st.markdown
    original_stop = st.stop
    injected = {"css": False, "login_seen": False}

    def markdown(body, *args, **kwargs):
        if not injected["css"]:
            original_markdown(_LOGIN_CSS, unsafe_allow_html=True)
            injected["css"] = True
        if isinstance(body, str) and 'class="brand">SPRINT MONITOR' in body and '100 / 200 m' in body:
            injected["login_seen"] = True
            body = _LOGIN_HTML
            kwargs["unsafe_allow_html"] = True
        return original_markdown(body, *args, **kwargs)

    def stop():
        if injected["login_seen"]:
            original_markdown(_BENEFIT_HTML, unsafe_allow_html=True)
        return original_stop()

    st.markdown = markdown
    st.stop = stop
    st._sprint_login_branding_installed = True
