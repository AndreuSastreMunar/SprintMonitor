"""Identidad visual CTEIB Velocistas y UX moderna, responsive y sin cambiar la lógica."""

import streamlit as st


_BRAND_CSS = r"""
<style>
:root{--cteib-purple:#4d0798;--cteib-pink:#f4055d;--cteib-ink:#171b2d;--cteib-muted:#737887}

/* Cabecera de marca compacta, pensada también para móvil. */
.cteib-brand-lockup{display:flex;align-items:flex-end;gap:.45rem;width:100%;margin:.1rem 0 1.2rem;line-height:.8;user-select:none}
.cteib-brand-top,.cteib-brand-bottom{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-style:italic;font-weight:950;letter-spacing:-.055em;transform:skew(-8deg);text-transform:uppercase;white-space:nowrap}
.cteib-brand-top{color:var(--cteib-purple);font-size:clamp(2rem,5vw,3.15rem)}
.cteib-brand-bottom{position:relative;color:var(--cteib-pink);font-size:clamp(1.65rem,4.3vw,2.65rem)}
.cteib-brand-bottom:before{content:"";position:absolute;right:100%;top:52%;width:1.35em;height:.5em;transform:translateY(-50%) skew(8deg);background:linear-gradient(var(--cteib-pink),var(--cteib-pink)) 100% 0/100% 16% no-repeat,linear-gradient(var(--cteib-pink),var(--cteib-pink)) 100% 42%/75% 16% no-repeat,linear-gradient(var(--cteib-pink),var(--cteib-pink)) 100% 84%/52% 16% no-repeat}
.hero .brand{display:none}

/* Inicio: más aire, jerarquía y aspecto de app. */
.hero{position:relative;margin:.15rem 0 1.35rem!important;padding:.15rem 0 .25rem}
.hero:after{content:"";position:absolute;right:-7%;top:-1rem;width:42%;height:4px;border-radius:999px;background:linear-gradient(90deg,transparent,rgba(244,5,93,.24),rgba(77,7,152,.16));transform:rotate(-7deg)}
.hello{font-size:clamp(2rem,5vw,2.65rem)!important;font-weight:900!important;letter-spacing:-.035em;color:var(--cteib-ink)}
.sub{font-size:1rem!important;color:var(--cteib-muted)!important;opacity:1!important;font-weight:550}

/* Tarjetas: superficie moderna, icono propio y pie visual. */
.menu-card{position:relative;overflow:hidden;border:1px solid rgba(77,7,152,.09)!important;border-radius:26px!important;padding:1.35rem 1.35rem 1.25rem!important;min-height:184px!important;background:linear-gradient(145deg,#fff 0%,#fff 66%,#faf7ff 100%)!important;box-shadow:0 14px 38px rgba(32,22,65,.08)!important;margin-bottom:.55rem!important;transition:transform .18s ease,box-shadow .18s ease}
.menu-card:after{content:"→";position:absolute;right:1.25rem;bottom:1.15rem;font-size:1.65rem;font-weight:800;color:var(--cteib-purple)}
.menu-card:hover{transform:translateY(-2px);box-shadow:0 18px 44px rgba(32,22,65,.12)!important}
.menu-icon{display:flex!important;align-items:center;justify-content:center;width:64px!important;height:64px!important;border-radius:19px!important;font-size:2rem!important;background:linear-gradient(145deg,#eee3ff,#f9e3ed)!important;border:0!important;box-shadow:none!important;margin-bottom:.8rem}
.menu-title{font-size:1.3rem!important;font-weight:850!important;letter-spacing:-.02em;color:var(--cteib-ink)}
.menu-sub{font-size:.96rem!important;color:var(--cteib-muted)!important;opacity:1!important;margin-top:.32rem!important}
.menu-num{width:36px!important;height:36px!important;margin-top:.85rem!important;background:linear-gradient(135deg,var(--cteib-purple),#6c18bd)!important;box-shadow:0 7px 16px rgba(77,7,152,.2)}

/* Los botones inmediatamente posteriores a una tarjeta pasan a ser su pie de acción. */
div[data-testid="stVerticalBlock"]:has(> div .menu-card) div[data-testid="stButton"] button{border:1px solid rgba(77,7,152,.16);color:var(--cteib-purple);background:linear-gradient(90deg,rgba(77,7,152,.055),rgba(244,5,93,.045));font-weight:800;min-height:48px;box-shadow:none}
div[data-testid="stVerticalBlock"]:has(> div .menu-card) div[data-testid="stButton"] button:hover{border-color:rgba(77,7,152,.35);background:linear-gradient(90deg,rgba(77,7,152,.10),rgba(244,5,93,.08))}

/* Botones generales más refinados sin cambiar su comportamiento. */
.stButton>button{border-radius:15px!important;transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease}
.stButton>button:hover{transform:translateY(-1px)}
hr{border-color:rgba(23,27,45,.08)!important;margin:1.6rem 0!important}

@media(max-width:640px){
  .cteib-brand-lockup{margin:.05rem 0 .9rem;gap:.35rem}.cteib-brand-top{font-size:2.1rem}.cteib-brand-bottom{font-size:1.72rem}
  .hero{margin-bottom:1rem!important}.hero:after{display:none}.hello{font-size:2rem!important}.sub{font-size:.92rem!important}
  .menu-card{min-height:158px!important;border-radius:22px!important;padding:1rem!important}.menu-icon{width:52px!important;height:52px!important;border-radius:16px!important;font-size:1.65rem!important;margin-bottom:.55rem}.menu-title{font-size:1.08rem!important}.menu-sub{font-size:.84rem!important}.menu-num{width:31px!important;height:31px!important;margin-top:.65rem!important}.menu-card:after{right:.95rem;bottom:.82rem;font-size:1.35rem}
  div[data-testid="stVerticalBlock"]:has(> div .menu-card) div[data-testid="stButton"] button{font-size:.88rem;min-height:44px}
}
@media(max-width:390px){.menu-card{min-height:150px!important;padding:.9rem!important}.menu-icon{width:46px!important;height:46px!important}.menu-sub{line-height:1.25}.cteib-brand-bottom:before{display:none}}
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
