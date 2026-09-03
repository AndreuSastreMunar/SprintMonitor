"""Identidad visual CTEIB Velocistas aplicada directamente al HTML generado."""

import re
import streamlit as st

_LOGO_HTML = '''
<div style="display:flex;align-items:flex-end;gap:.45rem;margin:.1rem 0 1.15rem;line-height:.82;">
  <div style="font-family:Inter,system-ui,sans-serif;font-style:italic;font-weight:950;letter-spacing:-.06em;transform:skew(-8deg);font-size:2.5rem;color:#4d0798;">CTEIB</div>
  <div style="font-family:Inter,system-ui,sans-serif;font-style:italic;font-weight:950;letter-spacing:-.06em;transform:skew(-8deg);font-size:2.05rem;color:#f4055d;">VELOCISTAS</div>
</div>
'''

_EXTRA_CSS = '''
<style>
.stButton>button{border-radius:15px!important;min-height:46px!important;font-weight:750!important;width:100%!important;transition:.15s ease}
.stButton>button:hover{transform:translateY(-1px);border-color:rgba(77,7,152,.35)!important}
@media(max-width:640px){
  .block-container{padding-left:.8rem!important;padding-right:.8rem!important}
  div[data-testid="stHorizontalBlock"]{gap:.7rem!important}
}
</style>
'''


def _modernize_card(body):
    if '<div class="menu-card">' not in body:
        return body
    body=body.replace('<div class="menu-card">','<div class="menu-card" style="position:relative;overflow:hidden;border:1px solid rgba(77,7,152,.10);border-radius:26px;padding:1.25rem;min-height:180px;background:linear-gradient(145deg,#ffffff 0%,#ffffff 67%,#faf7ff 100%);box-shadow:0 14px 34px rgba(31,22,64,.09);margin-bottom:.5rem;">',1)
    body=body.replace('<div class="menu-icon">','<div class="menu-icon" style="display:flex;align-items:center;justify-content:center;width:62px;height:62px;border-radius:19px;font-size:2rem;background:linear-gradient(145deg,#eee3ff,#ffe5ef);margin-bottom:.8rem;">',1)
    body=body.replace('<div class="menu-title">','<div class="menu-title" style="font-size:1.28rem;font-weight:850;letter-spacing:-.02em;color:#171b2d;margin-top:.15rem;">',1)
    body=body.replace('<div class="menu-sub">','<div class="menu-sub" style="font-size:.96rem;color:#737887;margin-top:.32rem;">',1)
    body=body.replace('<div class="menu-num">','<div class="menu-num" style="display:inline-flex;width:36px;height:36px;border-radius:50%;align-items:center;justify-content:center;background:linear-gradient(135deg,#4d0798,#6c18bd);color:#fff;font-weight:850;margin-top:.85rem;box-shadow:0 7px 16px rgba(77,7,152,.20);">',1)
    body=body.replace('</div>','<span style="position:absolute;right:1.2rem;bottom:1rem;color:#4d0798;font-size:1.55rem;font-weight:900;">→</span></div>',1) if False else body
    return body


def _modernize_hero(body):
    if '<div class="hero">' not in body:
        return body
    name_match=re.search(r'<div class="hello">(.*?)</div>',body)
    sub_match=re.search(r'<div class="sub">(.*?)</div>',body)
    hello=name_match.group(1) if name_match else ''
    sub=sub_match.group(1) if sub_match else ''
    return _LOGO_HTML + f'''<div style="margin:.1rem 0 1.35rem;position:relative;">
      <div style="font-size:clamp(2rem,5vw,2.65rem);font-weight:900;letter-spacing:-.035em;line-height:1.05;color:#171b2d;">{hello}</div>
      <div style="font-size:1rem;color:#737887;margin-top:.35rem;font-weight:550;">{sub}</div>
    </div>'''


def install_visual_branding():
    if getattr(st,"_cteib_visual_branding_installed",False):
        return
    original_markdown=st.markdown
    injected={"done":False}
    def markdown_with_brand(body,*args,**kwargs):
        if not injected["done"]:
            original_markdown(_EXTRA_CSS,unsafe_allow_html=True)
            injected["done"]=True
        if isinstance(body,str):
            if '<div class="hero">' in body:
                body=_modernize_hero(body)
                kwargs["unsafe_allow_html"]=True
            elif '<div class="menu-card">' in body:
                body=_modernize_card(body)
                kwargs["unsafe_allow_html"]=True
        return original_markdown(body,*args,**kwargs)
    st.markdown=markdown_with_brand
    st._cteib_visual_branding_installed=True
