import runpy
import streamlit as st

# Punto de entrada estable de Sprint Monitor.
# Toda la lógica vive en legacy_app.py, que debe ejecutarse en CADA rerun de
# Streamlit. No usamos `import legacy_app` porque Python lo cachea y, tras
# pulsar un botón, el siguiente rerun podía quedar completamente en blanco.

_original_set_page_config = st.set_page_config


def _set_page_config_cteib(*args, **kwargs):
    kwargs["page_title"] = "CTEIB Velocistas"
    kwargs["page_icon"] = "assets/cteib-icon.png"
    return _original_set_page_config(*args, **kwargs)


st.set_page_config = _set_page_config_cteib

_original_markdown = st.markdown
_LOGIN_OLD = '<div class="brand">SPRINT MONITOR</div><div class="hello">100 / 200 m</div><div class="sub">Entrenamiento, bienestar, competición y evolución.</div>'

_LOGIN_NEW = r'''
<style>
:root{--cteib-purple:#5a12c6;--cteib-pink:#ff0b68;--cteib-ink:#11172a;--cteib-muted:#7f8493}
.block-container:has(.cteib-login){max-width:520px!important;padding-top:5.6rem!important;padding-bottom:3rem!important}
.cteib-login{margin:0 0 1rem;text-align:center}
.cteib-login-logo{width:min(390px,88vw);margin:0 auto .65rem}
.cteib-login-logo svg{display:block;width:100%;height:auto;overflow:visible}
.cteib-login-copy{font-size:1rem;line-height:1.45;color:var(--cteib-muted);font-weight:560;margin:.15rem 0 .9rem;text-align:center}
.block-container:has(.cteib-login) div[data-testid="stTabs"] button[role="tab"]{font-size:1rem!important;font-weight:800!important;padding:.75rem .85rem!important}
.block-container:has(.cteib-login) div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--cteib-purple),var(--cteib-pink))!important;height:3px!important;border-radius:999px!important}
.block-container:has(.cteib-login) div[data-testid="stForm"]{border:1px solid rgba(90,18,198,.08)!important;border-radius:28px!important;padding:1.3rem 1.2rem 1.2rem!important;background:#fff!important;box-shadow:0 20px 55px rgba(45,25,90,.12)!important;margin-top:.7rem!important}
.block-container:has(.cteib-login) div[data-testid="stTextInput"] label{font-weight:800!important;color:var(--cteib-ink)!important}
.block-container:has(.cteib-login) div[data-testid="stTextInput"] input{min-height:58px!important;border-radius:18px!important;background:#f4f2f8!important;border:1px solid transparent!important;font-size:1rem!important;padding-left:1rem!important}
.block-container:has(.cteib-login) div[data-testid="stForm"] button{min-height:58px!important;border-radius:18px!important;border:0!important;background:linear-gradient(100deg,var(--cteib-purple),#a52bbf 52%,var(--cteib-pink))!important;color:#fff!important;font-size:1.05rem!important;font-weight:900!important;box-shadow:0 12px 26px rgba(120,25,166,.23)!important}
@media(max-width:640px){
 .block-container:has(.cteib-login){max-width:480px!important;padding-top:4.6rem!important;padding-left:1rem!important;padding-right:1rem!important}
 .cteib-login-logo{width:min(330px,86vw)}
 .block-container:has(.cteib-login) div[data-testid="stForm"]{padding:1.05rem .95rem 1rem!important;border-radius:24px!important}
 .block-container:has(.cteib-login) div[data-testid="stTextInput"] input,.block-container:has(.cteib-login) div[data-testid="stForm"] button{min-height:54px!important;border-radius:16px!important}
}
</style>
<div class="cteib-login">
  <div class="cteib-login-logo">
    <svg viewBox="0 0 520 140" role="img" aria-label="CTEIB Velocistas">
      <defs>
        <linearGradient id="p" x1="0" x2="1"><stop offset="0" stop-color="#4d0798"/><stop offset="1" stop-color="#7a2bd5"/></linearGradient>
        <linearGradient id="r" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient>
      </defs>
      <g transform="translate(8 8) skewX(-9)">
        <text x="55" y="58" fill="url(#p)" font-family="Arial Black,Arial,sans-serif" font-size="64" font-weight="900" letter-spacing="-4">CTEIB</text>
        <polygon points="10,79 84,79 84,86 10,86" fill="#f60962"/>
        <polygon points="27,92 84,92 84,99 27,99" fill="#f60962"/>
        <polygon points="44,105 84,105 84,112 44,112" fill="#f60962"/>
        <text x="94" y="113" fill="url(#r)" font-family="Arial Black,Arial,sans-serif" font-size="55" font-weight="900" letter-spacing="-4">VELOCISTAS</text>
      </g>
    </svg>
  </div>
  <div class="cteib-login-copy">Entrenamiento, bienestar, competición y evolución.</div>
</div>
'''


def _markdown_with_single_login(body, *args, **kwargs):
    if isinstance(body, str) and body == _LOGIN_OLD:
        return _original_markdown(_LOGIN_NEW, unsafe_allow_html=True)
    return _original_markdown(body, *args, **kwargs)


st.markdown = _markdown_with_single_login

# Ejecuta toda la aplicación original cada vez que Streamlit hace rerun.
runpy.run_path("legacy_app.py", run_name="__main__")
