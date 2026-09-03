"""Identidad visual CTEIB Velocistas sin alterar la estructura funcional de la app."""

import streamlit as st


_BRAND_CSS = r"""
<style>
/* Logo vectorial ligero: no depende de imágenes pesadas y responde bien en móvil. */
.cteib-brand-lockup{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  width:100%;
  margin:.15rem auto 1rem;
  line-height:.82;
  user-select:none;
}
.cteib-brand-top,
.cteib-brand-bottom{
  font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-style:italic;
  font-weight:950;
  letter-spacing:-.055em;
  transform:skew(-8deg);
  text-transform:uppercase;
  white-space:nowrap;
}
.cteib-brand-top{
  color:#4d0798;
  font-size:clamp(2.35rem,7vw,4.35rem);
  margin-left:-1.4em;
}
.cteib-brand-bottom{
  position:relative;
  color:#f4055d;
  font-size:clamp(2rem,6vw,3.75rem);
  margin-top:.12em;
  margin-left:1.25em;
}
.cteib-brand-bottom:before{
  content:"";
  position:absolute;
  right:100%;
  top:52%;
  width:1.7em;
  height:.54em;
  transform:translateY(-50%) skew(8deg);
  background:
    linear-gradient(#f4055d,#f4055d) 100% 0/100% 16% no-repeat,
    linear-gradient(#f4055d,#f4055d) 100% 42%/78% 16% no-repeat,
    linear-gradient(#f4055d,#f4055d) 100% 84%/58% 16% no-repeat;
}

/* El pequeño texto antiguo deja paso al nuevo identificador visual. */
.hero .brand{display:none}

/* Mejora exclusivamente gráfica de los iconos existentes de las tarjetas. */
.menu-icon{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:54px;
  height:54px;
  border-radius:17px;
  font-size:1.7rem !important;
  background:linear-gradient(145deg,rgba(77,7,152,.13),rgba(244,5,93,.10));
  border:1px solid rgba(77,7,152,.10);
  box-shadow:0 8px 20px rgba(77,7,152,.09);
}

@media(max-width:640px){
  .cteib-brand-lockup{margin:.05rem auto .75rem}
  .cteib-brand-top{font-size:2.65rem;margin-left:-1.05em}
  .cteib-brand-bottom{font-size:2.25rem;margin-left:.9em}
  .menu-icon{width:48px;height:48px;border-radius:15px;font-size:1.5rem !important}
}
</style>
"""

_LOGO_HTML = r"""
<div class="cteib-brand-lockup" aria-label="CTEIB Velocistas">
  <div class="cteib-brand-top">CTEIB</div>
  <div class="cteib-brand-bottom">VELOCISTAS</div>
</div>
"""


def install_visual_branding():
    if getattr(st, "_cteib_visual_branding_installed", False):
        return

    original_markdown = st.markdown
    original_markdown(_BRAND_CSS, unsafe_allow_html=True)

    def markdown_with_brand(body, *args, **kwargs):
        if isinstance(body, str) and '<div class="hero">' in body:
            original_markdown(_LOGO_HTML, unsafe_allow_html=True)
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_brand
    st._cteib_visual_branding_installed = True
