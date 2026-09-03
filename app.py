import streamlit as st
import streamlit.components.v1 as components

# Fuerza el icono real de CTEIB Velocistas cuando legacy_app configure la página.
_original_set_page_config = st.set_page_config

def _set_page_config_cteib(*args, **kwargs):
    kwargs["page_title"] = "CTEIB Velocistas"
    kwargs["page_icon"] = "assets/cteib-icon.png"
    return _original_set_page_config(*args, **kwargs)

st.set_page_config = _set_page_config_cteib

# Punto de entrada real de la app. El resto de la lógica se conserva intacta en
# legacy_app.py; aquí solo modernizamos la pantalla de acceso antes de ejecutarla.
_original_markdown = st.markdown
_head_icon_injected = False

_LOGIN_OLD = '<div class="brand">SPRINT MONITOR</div><div class="hello">100 / 200 m</div><div class="sub">Entrenamiento, bienestar, competición y evolución.</div>'

_LOGIN_NEW = r'''
<style>
:root{--cteib-purple:#5a12c6;--cteib-pink:#ff0b68;--cteib-ink:#11172a;--cteib-muted:#7f8493}
.block-container:has(.cteib-login){max-width:520px!important;padding-top:5.8rem!important;padding-bottom:3rem!important}
.cteib-login{margin:0 0 1rem;text-align:left}
.cteib-login-logo{width:min(390px,88vw);margin:0 auto .8rem}
.cteib-login-logo svg{display:block;width:100%;height:auto;overflow:visible}
.cteib-login-copy{font-size:1rem;line-height:1.45;color:var(--cteib-muted);font-weight:560;margin:.1rem 0 .9rem;text-align:center}
.block-container:has(.cteib-login) div[data-testid="stTabs"] button[role="tab"]{font-size:1rem!important;font-weight:800!important;padding:.75rem .85rem!important}
.block-container:has(.cteib-login) div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--cteib-purple),var(--cteib-pink))!important;height:3px!important;border-radius:999px!important}
.block-container:has(.cteib-login) div[data-testid="stForm"]{border:1px solid rgba(90,18,198,.08)!important;border-radius:28px!important;padding:1.3rem 1.2rem 1.2rem!important;background:#fff!important;box-shadow:0 20px 55px rgba(45,25,90,.12)!important;margin-top:.7rem!important}
.block-container:has(.cteib-login) div[data-testid="stTextInput"] label{font-weight:850!important;color:var(--cteib-ink)!important}
.block-container:has(.cteib-login) div[data-testid="stTextInput"] input{min-height:58px!important;border-radius:18px!important;background:#f4f2f8!important;border:1px solid transparent!important;font-size:1rem!important;padding-left:1rem!important}
.block-container:has(.cteib-login) div[data-testid="stTextInput"] input:focus{border-color:rgba(90,18,198,.28)!important;box-shadow:0 0 0 3px rgba(90,18,198,.08)!important}
.block-container:has(.cteib-login) div[data-testid="stForm"] button{min-height:58px!important;border-radius:18px!important;border:0!important;background:linear-gradient(100deg,var(--cteib-purple),#a52bbf 52%,var(--cteib-pink))!important;color:#fff!important;font-size:1.05rem!important;font-weight:900!important;box-shadow:0 12px 26px rgba(120,25,166,.23)!important}
.block-container:has(.cteib-login) div[data-testid="stForm"] button:hover{transform:translateY(-1px)!important;filter:saturate(1.06)!important}
.cteib-login-benefit{display:flex;align-items:center;gap:.9rem;margin:1rem 0 .25rem;padding:1rem;border-radius:22px;background:linear-gradient(135deg,#f6efff,#fff2f8);border:1px solid rgba(90,18,198,.06)}
.cteib-login-benefit-icon{display:flex;align-items:center;justify-content:center;flex:0 0 54px;width:54px;height:54px;border-radius:17px;background:linear-gradient(145deg,#eadcff,#ffdcea);font-size:1.65rem}
.cteib-login-benefit-title{font-weight:900;color:var(--cteib-ink)}
.cteib-login-benefit-copy{font-size:.86rem;color:var(--cteib-muted);line-height:1.35;margin-top:.15rem}
@media(max-width:640px){
 .block-container:has(.cteib-login){max-width:480px!important;padding-top:4.8rem!important;padding-left:1rem!important;padding-right:1rem!important}
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


def _inject_mobile_icon_links():
    global _head_icon_injected
    if _head_icon_injected:
        return
    _head_icon_injected = True
    components.html(
        """
        <script>
        try {
          const doc = window.parent.document;
          const icon = doc.querySelector('link[rel="shortcut icon"], link[rel="icon"]');
          if (icon && icon.href) {
            doc.querySelectorAll('link[rel="apple-touch-icon"]').forEach(x => x.remove());
            const apple = doc.createElement('link');
            apple.rel = 'apple-touch-icon';
            apple.href = icon.href;
            doc.head.appendChild(apple);

            const manifest = {
              name: 'CTEIB Velocistas',
              short_name: 'CTEIB Velocistas',
              display: 'standalone',
              start_url: window.parent.location.href,
              background_color: '#ffffff',
              theme_color: '#5a12c6',
              icons: [
                {src: icon.href, sizes: '192x192', type: 'image/png'},
                {src: icon.href, sizes: '512x512', type: 'image/png'}
              ]
            };
            const blob = new Blob([JSON.stringify(manifest)], {type: 'application/manifest+json'});
            const url = URL.createObjectURL(blob);
            doc.querySelectorAll('link[rel="manifest"]').forEach(x => x.remove());
            const link = doc.createElement('link');
            link.rel = 'manifest';
            link.href = url;
            doc.head.appendChild(link);
            doc.title = 'CTEIB Velocistas';
          }
        } catch (e) { console.log('CTEIB icon setup skipped', e); }
        </script>
        """,
        height=0,
        width=0,
    )


def _markdown_with_direct_login(body, *args, **kwargs):
    result = _original_markdown(body, *args, **kwargs)
    if isinstance(body, str) and '.block-container' in body:
        _inject_mobile_icon_links()
    if isinstance(body, str) and body == _LOGIN_OLD:
        # Renderiza encima el login moderno y oculta visualmente el bloque antiguo.
        _original_markdown(_LOGIN_NEW, unsafe_allow_html=True)
    return result


st.markdown = _markdown_with_direct_login

# Ejecuta la aplicación original completa con el login ya sustituido.
import legacy_app  # noqa: E402,F401
