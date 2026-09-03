import base64
import io
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# -----------------------------------------------------------------------------
# Icono instalable CTEIB Velocistas
# -----------------------------------------------------------------------------
# Fuente exacta enviada por el usuario. Se guarda embebida para que Streamlit
# Community Cloud pueda generar los iconos físicos en cada arranque sin depender
# de archivos externos.
_ICON_SOURCE_WEBP_B64 = "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"

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)
_ICON_192 = _STATIC_DIR / "cteib-icon-192.png"
_ICON_512 = _STATIC_DIR / "cteib-icon-512.png"
_MANIFEST = _STATIC_DIR / "manifest.json"


def _prepare_install_assets():
    source = Image.open(io.BytesIO(base64.b64decode(_ICON_SOURCE_WEBP_B64))).convert("RGB")
    for size, target in ((192, _ICON_192), (512, _ICON_512)):
        icon = ImageOps.fit(source, (size, size), method=Image.Resampling.LANCZOS)
        icon.save(target, "PNG", optimize=True)
    manifest = {
        "id": "/",
        "name": "CTEIB Velocistas",
        "short_name": "CTEIB",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#5a12c6",
        "icons": [
            {"src": "/app/static/cteib-icon-192.png?v=4", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/app/static/cteib-icon-512.png?v=4", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    _MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


_prepare_install_assets()

# Interceptamos la configuración que hace legacy_app.py. De este modo el favicon
# también usa CTEIB y, justo después de set_page_config, añadimos al <head> real
# las etiquetas que Android/iPhone consultan al crear el acceso de inicio.
_original_set_page_config = st.set_page_config


def _set_page_config_cteib(*args, **kwargs):
    kwargs["page_title"] = "CTEIB Velocistas"
    kwargs["page_icon"] = str(_ICON_192)
    result = _original_set_page_config(*args, **kwargs)
    components.html(
        r'''
<script>
(function () {
  const d = window.parent.document;
  const head = d.head;
  function link(rel, href, sizes) {
    let el = head.querySelector('link[rel="' + rel + '"]');
    if (!el) { el = d.createElement('link'); el.rel = rel; head.appendChild(el); }
    el.href = href;
    if (sizes) el.sizes = sizes;
    return el;
  }
  head.querySelectorAll('link[rel="manifest"]').forEach(el => el.remove());
  const manifest = d.createElement('link');
  manifest.rel = 'manifest';
  manifest.href = '/app/static/manifest.json?v=4';
  head.appendChild(manifest);
  link('apple-touch-icon', '/app/static/cteib-icon-192.png?v=4', '192x192');
  link('icon', '/app/static/cteib-icon-192.png?v=4', '192x192');
  let theme = head.querySelector('meta[name="theme-color"]');
  if (!theme) { theme = d.createElement('meta'); theme.name = 'theme-color'; head.appendChild(theme); }
  theme.content = '#5a12c6';
  let capable = head.querySelector('meta[name="apple-mobile-web-app-capable"]');
  if (!capable) { capable = d.createElement('meta'); capable.name = 'apple-mobile-web-app-capable'; head.appendChild(capable); }
  capable.content = 'yes';
  let status = head.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]');
  if (!status) { status = d.createElement('meta'); status.name = 'apple-mobile-web-app-status-bar-style'; head.appendChild(status); }
  status.content = 'default';
  let title = head.querySelector('meta[name="apple-mobile-web-app-title"]');
  if (!title) { title = d.createElement('meta'); title.name = 'apple-mobile-web-app-title'; head.appendChild(title); }
  title.content = 'CTEIB Velocistas';
})();
</script>
''',
        height=0,
        width=0,
    )
    return result


st.set_page_config = _set_page_config_cteib

# -----------------------------------------------------------------------------
# Login moderno
# -----------------------------------------------------------------------------
_original_markdown = st.markdown
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
@media(max-width:640px){.block-container:has(.cteib-login){max-width:480px!important;padding-top:4.8rem!important;padding-left:1rem!important;padding-right:1rem!important}.cteib-login-logo{width:min(330px,86vw)}}
</style>
<div class="cteib-login">
  <div class="cteib-login-logo">
    <svg viewBox="0 0 520 140" role="img" aria-label="CTEIB Velocistas">
      <defs><linearGradient id="p" x1="0" x2="1"><stop offset="0" stop-color="#4d0798"/><stop offset="1" stop-color="#7a2bd5"/></linearGradient><linearGradient id="r" x1="0" x2="1"><stop offset="0" stop-color="#ff176f"/><stop offset="1" stop-color="#ef005a"/></linearGradient></defs>
      <g transform="translate(8 8) skewX(-9)"><text x="55" y="58" fill="url(#p)" font-family="Arial Black,Arial,sans-serif" font-size="64" font-weight="900" letter-spacing="-4">CTEIB</text><polygon points="10,79 84,79 84,86 10,86" fill="#f60962"/><polygon points="27,92 84,92 84,99 27,99" fill="#f60962"/><polygon points="44,105 84,105 84,112 44,112" fill="#f60962"/><text x="94" y="113" fill="url(#r)" font-family="Arial Black,Arial,sans-serif" font-size="55" font-weight="900" letter-spacing="-4">VELOCISTAS</text></g>
    </svg>
  </div>
  <div class="cteib-login-copy">Entrenamiento, bienestar, competición y evolución.</div>
</div>
'''


def _markdown_with_direct_login(body, *args, **kwargs):
    if isinstance(body, str) and body == _LOGIN_OLD:
        body = _LOGIN_NEW
        kwargs["unsafe_allow_html"] = True
    return _original_markdown(body, *args, **kwargs)


st.markdown = _markdown_with_direct_login

# Ejecuta la aplicación original completa.
import legacy_app  # noqa: E402,F401
