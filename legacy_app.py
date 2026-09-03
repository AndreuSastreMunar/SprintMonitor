from datetime import date
import pandas as pd
import streamlit as st
from db.client import get_supabase

st.set_page_config(page_title="Sprint Monitor 100/200", page_icon="🏃", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1rem;padding-bottom:3rem} section[data-testid="stSidebar"]{display:none}
.hero{margin:.2rem 0 1rem}.brand{font-size:.9rem;font-weight:800;letter-spacing:.14em;opacity:.65}.hello{font-size:2rem;font-weight:850;line-height:1.05;margin-top:.3rem}.sub{opacity:.6;margin-top:.25rem}
.menu-card{border:1px solid rgba(0,0,0,.08);border-radius:24px;padding:1.05rem;min-height:145px;box-shadow:0 8px 24px rgba(0,0,0,.08);background:linear-gradient(180deg,#fff,#f7f8fa);margin-bottom:.45rem}
.menu-icon{font-size:2rem}.menu-title{font-size:1.15rem;font-weight:800;margin-top:.35rem}.menu-sub{font-size:.9rem;opacity:.65;margin-top:.2rem}.menu-num{display:inline-flex;width:34px;height:34px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:800;margin-top:.75rem}
.stButton>button{border-radius:16px;min-height:46px;font-weight:700;width:100%} div[data-testid="stForm"]{border-radius:22px;padding:1rem}
@media(max-width:640px){.block-container{padding-left:.85rem;padding-right:.85rem}.hello{font-size:1.7rem}.menu-card{min-height:132px}}
</style>""", unsafe_allow_html=True)

supabase=get_supabase()
WELLNESS_LABELS={"sleep":"Sueño","fatigue":"Fatiga","muscle_soreness":"Dolor muscular","stress":"Estrés","readiness":"Disposición para entrenar"}
HEALTH_LABELS={
    "completed_no_problem":"Completado sin problemas de salud",
    "completed_with_health_problem":"Completado con algún problema de salud",
    "adapted_due_health_problem":"Adaptado por problemas de salud",
    "not_completed_due_health_problem":"No completado por problemas de salud",
}
MARK_EVENTS=["60m","100m","200m","400m"]
SEASON_START_MONTH=8

def get_profile(uid):
    return supabase.table("profiles").select("*").eq("id",uid).single().execute().data

def sign_out():
    try: supabase.auth.sign_out()
    except Exception: pass
    for k in ["user","profile","view","blocks","selected_athlete","training_did_gym","training_did_plyo","health_completed_ok","health_reason"]:
        st.session_state.pop(k,None)
    st.rerun()

def go_home_with_message(message):
    st.session_state.flash_message=message
    st.session_state.view="home"
    st.rerun()

def login():
    if "user" in st.session_state: return st.session_state.user
    st.markdown('<div class="brand">SPRINT MONITOR</div><div class="hello">100 / 200 m</div><div class="sub">Entrenamiento, bienestar, competición y evolución.</div>',unsafe_allow_html=True)
    a,b=st.tabs(["Entrar","Crear cuenta"])
    with a:
        with st.form("login"):
            email=st.text_input("Email"); password=st.text_input("Contraseña",type="password"); go=st.form_submit_button("Entrar",use_container_width=True)
        if go:
            try:
                r=supabase.auth.sign_in_with_password({"email":email,"password":password}); st.session_state.user=r.user; st.session_state.profile=get_profile(r.user.id); st.rerun()
            except Exception as e: st.error(f"No se pudo iniciar sesión: {e}")
    with b:
        with st.form("signup"):
            name=st.text_input("Nombre y apellidos"); email2=st.text_input("Email",key="signup_email"); password2=st.text_input("Contraseña",type="password",key="signup_pw"); go2=st.form_submit_button("Crear cuenta",use_container_width=True)
        if go2:
            try: supabase.auth.sign_up({"email":email2,"password":password2,"options":{"data":{"full_name":name}}}); st.success("Cuenta creada. Confirma el email si Supabase te lo pide.")
            except Exception as e: st.error(f"No se pudo crear la cuenta: {e}")
    st.stop()

def header(profile,label):
    name=(profile.get("full_name") or "Atleta").split()[0]
    st.markdown(f'<div class="hero"><div class="brand">SPRINT MONITOR</div><div class="hello">Hola, {name}</div><div class="sub">{profile.get("specialty") or "100 / 200 m"} · {label}</div></div>',unsafe_allow_html=True)

def card(col,icon,title,subtitle,number,target,key):
    with col:
        st.markdown(f'<div class="menu-card"><div class="menu-icon">{icon}</div><div class="menu-title">{title}</div><div class="menu-sub">{subtitle}</div><div class="menu-num">{number}</div></div>',unsafe_allow_html=True)
        if st.button(f"Abrir {title}",key=key): st.session_state.view=target; st.rerun()

def back(target="home",label="Volver al inicio"):
    if st.button(f"← {label}"): st.session_state.view=target; st.rerun()

def _fixed_axis_chart(df,x_col,value_col,series_col=None,ymin=0,ymax=10,mark="line"):
    data=df.copy(); data[x_col]=pd.to_datetime(data[x_col]).dt.strftime("%Y-%m-%d") if pd.api.types.is_datetime64_any_dtype(data[x_col]) else data[x_col]
    enc={"x":{"field":x_col,"type":"temporal" if x_col in ["periodo","session_date","entry_date"] else "nominal","title":None},"y":{"field":value_col,"type":"quantitative","scale":{"domain":[ymin,ymax]},"title":None}}
    if series_col: enc["color"]={"field":series_col,"type":"nominal","title":None}
    st.vega_lite_chart({"mark":{"type":mark,"point":True if mark=="line" else False},"encoding":enc,"data":{"values":data.to_dict("records")}},use_container_width=True)

def _zero_floor_chart(df,x_col,value_col,series_col=None,mark="line"):
    data=df.copy(); data[x_col]=pd.to_datetime(data[x_col]).dt.strftime("%Y-%m-%d") if pd.api.types.is_datetime64_any_dtype(data[x_col]) else data[x_col]
    enc={"x":{"field":x_col,"type":"temporal" if x_col in ["periodo","session_date","entry_date"] else "nominal","title":None},"y":{"field":value_col,"type":"quantitative","scale":{"domainMin":0},"title":None}}
    if series_col: enc["color"]={"field":series_col,"type":"nominal","title":None}
    st.vega_lite_chart({"mark":{"type":mark,"point":True if mark=="line" else False},"encoding":enc,"data":{"values":data.to_dict("records")}},use_container_width=True)

def _period_label(df,date_col,period):
    x=df.copy(); x[date_col]=pd.to_datetime(x[date_col])
    if period=="Día": x["periodo"]=x[date_col].dt.floor("D")
    elif period=="Semana": x["periodo"]=x[date_col].dt.to_period("W").apply(lambda p:p.start_time)
    else: x["periodo"]=x[date_col].dt.to_period("M").apply(lambda p:p.start_time)
    return x

def _season_start_for_date(value):
    ts=pd.Timestamp(value)
    return int(ts.year if ts.month>=SEASON_START_MONTH else ts.year-1)

def _season_label(start_year):
    return f"Temporada {start_year}/{start_year+1}"

def _load_marks(uid):
    rows=[]
    try:
        comps=(supabase.table("competitions").select("competition_date,competition_name,event,result_seconds,wind").eq("athlete_id",uid).in_("event",MARK_EVENTS).order("competition_date").limit(500).execute().data or [])
        for r in comps:
            rows.append({"id":None,"event":r.get("event"),"mark_seconds":r.get("result_seconds"),"mark_date":r.get("competition_date"),"source":r.get("competition_name") or "Competición","wind":r.get("wind"),"manual":False,"notes":None})
    except Exception:
        pass
    manual_available=True
    manual_rows=[]
    try:
        manual_rows=(supabase.table("athlete_marks").select("id,event,mark_seconds,mark_date,notes").eq("athlete_id",uid).order("mark_date").limit(500).execute().data or [])
        for r in manual_rows:
            rows.append({"id":r.get("id"),"event":r.get("event"),"mark_seconds":r.get("mark_seconds"),"mark_date":r.get("mark_date"),"source":"Marca añadida por el atleta","wind":None,"manual":True,"notes":r.get("notes")})
    except Exception:
        manual_available=False
    return rows,manual_rows,manual_available

def _best_mark(df):
    if df.empty: return None
    valid=df[pd.to_numeric(df["mark_seconds"],errors="coerce")>0].copy()
    if valid.empty: return None
    valid["mark_seconds"]=pd.to_numeric(valid["mark_seconds"],errors="coerce")
    return valid.loc[valid["mark_seconds"].idxmin()]

def _mark_caption(row):
    if row is None: return "Sin marca registrada"
    parsed=pd.to_datetime(row.get("mark_date"),errors="coerce")
    when=parsed.strftime("%d/%m/%Y") if not pd.isna(parsed) else ""
    extras=[x for x in [when,row.get("source") or ""] if x]
    wind=row.get("wind")
    if wind is not None:
        try: extras.append(f"viento {float(wind):+.1f} m/s")
        except Exception: pass
    if row.get("notes"): extras.append(str(row.get("notes")))
    return " · ".join(extras) if extras else "Marca registrada"

def _render_marks(uid,key_prefix,editable=False):
    rows,manual_rows,manual_available=_load_marks(uid)
    df=pd.DataFrame(rows)
    now=pd.Timestamp.today(); current_start=_season_start_for_date(now)
    season_starts=[]
    if not df.empty:
        df["mark_date"]=pd.to_datetime(df["mark_date"],errors="coerce")
        df["mark_seconds"]=pd.to_numeric(df["mark_seconds"],errors="coerce")
        season_starts=sorted({_season_start_for_date(d) for d in df["mark_date"].dropna()},reverse=True)
    if current_start not in season_starts: season_starts=[current_start]+season_starts
    labels=[_season_label(y) for y in season_starts]
    selected_label=st.selectbox("Temporada",labels,index=0,key=f"marks_season_{key_prefix}")
    selected_start=season_starts[labels.index(selected_label)]
    season_from=pd.Timestamp(year=selected_start,month=SEASON_START_MONTH,day=1)
    season_to=pd.Timestamp(year=selected_start+1,month=SEASON_START_MONTH,day=1)
    st.caption("La marca personal usa todos los registros. La marca de la temporada usa la temporada seleccionada.")
    cols=st.columns(2)
    for index,event in enumerate(MARK_EVENTS):
        event_df=df[df["event"]==event].copy() if not df.empty else pd.DataFrame()
        pb=_best_mark(event_df)
        season_df=event_df[(event_df["mark_date"]>=season_from)&(event_df["mark_date"]<season_to)].copy() if not event_df.empty else pd.DataFrame()
        sb=_best_mark(season_df)
        with cols[index%2]:
            with st.container(border=True):
                st.markdown(f"### {event.replace('m',' m')}")
                c1,c2=st.columns(2)
                c1.metric("Marca personal",f"{float(pb['mark_seconds']):.3f} s" if pb is not None else "—")
                c2.metric(selected_label,f"{float(sb['mark_seconds']):.3f} s" if sb is not None else "—")
                st.caption(f"MP: {_mark_caption(pb)}")
                st.caption(f"MT: {_mark_caption(sb)}")
    if editable:
        st.divider(); st.markdown("### ➕ Añadir marca")
        if not manual_available:
            st.warning("Para añadir marcas manualmente, ejecuta primero db/007_athlete_marks.sql en Supabase.")
        with st.form(f"add_mark_{key_prefix}"):
            c1,c2=st.columns(2)
            event=c1.selectbox("Prueba",MARK_EVENTS,key=f"mark_event_{key_prefix}")
            mark_date=c2.date_input("Fecha de la marca",date.today(),key=f"mark_date_{key_prefix}")
            mark=st.number_input("Marca (s)",min_value=0.0,max_value=120.0,value=0.0,step=0.01,format="%.3f",key=f"mark_seconds_{key_prefix}")
            notes=st.text_input("Comentario (opcional)",key=f"mark_notes_{key_prefix}")
            save=st.form_submit_button("Guardar marca",use_container_width=True)
        if save:
            if mark<=0: st.warning("Introduce una marca válida.")
            elif not manual_available: st.error("Primero ejecuta db/007_athlete_marks.sql en Supabase.")
            else:
                try:
                    supabase.table("athlete_marks").insert({"athlete_id":uid,"event":event,"mark_seconds":float(mark),"mark_date":str(mark_date),"notes":notes or None}).execute()
                    st.success("Marca guardada. Tu entrenador podrá verla automáticamente."); st.rerun()
                except Exception as e: st.error(f"No se pudo guardar la marca: {e}")
        if manual_rows:
            st.markdown("### Mis marcas añadidas")
            manual_df=pd.DataFrame(manual_rows).rename(columns={"mark_date":"Fecha","event":"Prueba","mark_seconds":"Marca (s)","notes":"Comentario"})
            st.dataframe(manual_df[["Fecha","Prueba","Marca (s)","Comentario"]],use_container_width=True,hide_index=True)

def athlete_home(user,profile):
    if st.session_state.get("flash_message"): st.success(st.session_state.pop("flash_message"))
    header(profile,"ATLETA"); c1,c2=st.columns(2); card(c1,"🏃","Entrenamiento","Series, metros y RPE",1,"training","m1"); card(c2,"❤️","Wellness","Cómo te encuentras hoy",2,"wellness","m2")
    if profile.get("sex")=="female":
        c3,c4=st.columns(2); card(c3,"🌸","Ciclo menstrual","Registro privado",3,"cycle","m3"); card(c4,"🏆","Competición","60, 100, 200 y 400 m",4,"competition","m4")
        st.markdown('<div class="menu-card"><div class="menu-icon">📈</div><div class="menu-title">Mi evolución</div><div class="menu-sub">Marcas, carga y bienestar</div><div class="menu-num">5</div></div>',unsafe_allow_html=True)
        if st.button("Abrir Mi evolución",key="m5"): st.session_state.view="evolution"; st.rerun()
    else:
        c3,c4=st.columns(2); card(c3,"🏆","Competición","60, 100, 200 y 400 m",3,"competition","m3m"); card(c4,"📈","Mi evolución","Marcas, carga y bienestar",4,"evolution","m4m")
    st.divider()
    if st.button("👤 Mi perfil"): st.session_state.view="profile"; st.rerun()
    if st.button("Cerrar sesión"): sign_out()

def _parse_optional_time(value):
    value=(value or "").strip().replace(",",".")
    if not value: return None
    try:
        number=float(value); return number if number>0 else "invalid"
    except ValueError: return "invalid"

def _new_series():
    return {"distance":60.0,"time":"","recovery":5.0}

def training(user):
    back(); st.title("🏃 Entrenamiento"); st.caption("RPE única para toda la sesión. El tiempo de cada serie es opcional.")
    if "blocks" not in st.session_state: st.session_state.blocks=[{"series":[_new_series()]}]
    day=st.date_input("Fecha",date.today()); rpe=st.slider("RPE global",0.0,10.0,5.0,0.5); notes=st.text_area("Comentarios generales")
    st.markdown("### Trabajo complementario")
    did_gym_answer=st.radio("¿Has hecho gimnasio?",["Sí","No"],horizontal=True,index=None,key="training_did_gym")
    did_plyo_answer=st.radio("¿Has hecho pliometría?",["Sí","No"],horizontal=True,index=None,key="training_did_plyo")
    updated_blocks=[]
    for i,b in enumerate(st.session_state.blocks):
        with st.container(border=True):
            st.markdown(f"### Bloque {i+1}")
            st.caption("Cada serie puede tener una distancia, un tiempo y una recuperación diferentes.")
            current_series=list(b.get("series") or [_new_series()]); shown=[]
            for n,s in enumerate(current_series,1):
                st.markdown(f"**Serie {n}**")
                c1,c2,c3,c4=st.columns([2,2,2,1])
                distance=c1.number_input("Metros",1.0,1000.0,float(s.get("distance",60.0)),1.0,key=f"series_distance_{i}_{n}")
                time_value=c2.text_input("Tiempo serie (s)",value=str(s.get("time") or ""),placeholder="Opcional",key=f"series_time_{i}_{n}")
                recovery=c3.number_input("Recuperación después de la serie (min)",0.0,60.0,float(s.get("recovery",5.0)),0.5,key=f"series_recovery_{i}_{n}")
                shown.append({"distance":distance,"time":time_value,"recovery":recovery})
                if c4.button("✕",key=f"remove_series_{i}_{n}",disabled=len(current_series)==1): st.session_state.blocks[i]["series"].pop(n-1); st.rerun()
            if st.button("➕ Añadir serie",key=f"add_series_{i}"): st.session_state.blocks[i].setdefault("series",[]).append(_new_series()); st.rerun()
            st.caption(f"Volumen del bloque: {sum(float(s['distance']) for s in shown):.0f} m")
            if st.button("Eliminar bloque",key=f"del_block_{i}",disabled=len(st.session_state.blocks)==1): st.session_state.blocks.pop(i); st.rerun()
            updated_blocks.append({"series":shown})
    st.session_state.blocks=updated_blocks
    if st.button("➕ Añadir bloque"): st.session_state.blocks.append({"series":[_new_series()]}); st.rerun()
    total=sum(float(s["distance"]) for b in st.session_state.blocks for s in b["series"])
    st.info(f"Volumen total: **{total:.0f} m** · RPE: **{rpe:g}** · Carga: **{total*rpe:.0f} UA**")
    st.markdown("### Finalización de entreno")
    completed_ok=st.radio("¿Has podido completar todo el entrenamiento sin ningún problema de salud?",["Sí","No"],horizontal=True,index=None,key="health_completed_ok")
    health_status=None; reason=None
    if completed_ok=="Sí": health_status="completed_no_problem"
    elif completed_ok=="No":
        reason=st.radio("Indica el motivo",["He completado el entrenamiento con algún problema de salud.","He adaptado el entrenamiento debido a problemas de salud.","No he podido completar el entrenamiento debido a problemas de salud."],index=None,key="health_reason")
        if reason: health_status={"He completado el entrenamiento con algún problema de salud.":"completed_with_health_problem","He adaptado el entrenamiento debido a problemas de salud.":"adapted_due_health_problem","No he podido completar el entrenamiento debido a problemas de salud.":"not_completed_due_health_problem"}[reason]
    if st.button("💾 Guardar entrenamiento",type="primary"):
        parsed=[]; invalid_time=False
        for block_index,b in enumerate(st.session_state.blocks,1):
            for series_index,s in enumerate(b["series"],1):
                t=_parse_optional_time(s["time"])
                if t=="invalid": invalid_time=True
                parsed.append({"block":block_index,"series":series_index,"distance":float(s["distance"]),"time":None if t=="invalid" else t,"recovery":float(s["recovery"])})
        if did_gym_answer is None: st.warning("Debes responder si has hecho gimnasio antes de guardar.")
        elif did_plyo_answer is None: st.warning("Debes responder si has hecho pliometría antes de guardar.")
        elif completed_ok is None: st.warning("Debes responder la pregunta de Finalización de entreno antes de guardar.")
        elif completed_ok=="No" and reason is None: st.warning("Debes indicar el motivo antes de guardar.")
        elif invalid_time: st.warning("Revisa los tiempos: deben ser números positivos o dejarse en blanco.")
        else:
            try:
                session=supabase.table("training_sessions").insert({"athlete_id":user.id,"session_date":str(day),"rpe":float(rpe),"did_gym":did_gym_answer=="Sí","did_plyometrics":did_plyo_answer=="Sí","health_status":health_status,"notes":notes or None}).execute().data[0]
                for order,s in enumerate(parsed,1):
                    sprint_set=supabase.table("sprint_sets").insert({"session_id":session["id"],"set_order":order,"distance_m":s["distance"],"repetitions":1,"recovery_seconds":int(round(s["recovery"]*60))}).execute().data[0]
                    supabase.table("sprint_reps").insert({"sprint_set_id":sprint_set["id"],"rep_number":1,"time_seconds":s["time"]}).execute()
                for k in ["blocks","training_did_gym","training_did_plyo","health_completed_ok","health_reason"]: st.session_state.pop(k,None)
                go_home_with_message("Entrenamiento guardado correctamente.")
            except Exception as e: st.error(f"No se pudo guardar: {e}")

def wellness(user):
    back(); st.title("❤️ Wellness")
    with st.form("wellness_form"):
        day=st.date_input("Fecha",date.today()); sleep=st.slider("Sueño",1,5,3); fatigue=st.slider("Fatiga",1,5,3); soreness=st.slider("Dolor muscular",1,5,3); stress=st.slider("Estrés",1,5,3); readiness=st.slider("Disposición para entrenar",1,5,3); notes=st.text_area("Comentarios"); save=st.form_submit_button("Guardar wellness",use_container_width=True)
    if save:
        try: supabase.table("wellness_entries").upsert({"athlete_id":user.id,"entry_date":str(day),"sleep":sleep,"fatigue":fatigue,"muscle_soreness":soreness,"stress":stress,"readiness":readiness,"notes":notes or None},on_conflict="athlete_id,entry_date").execute(); go_home_with_message("Wellness guardado correctamente.")
        except Exception: st.error("Primero ejecuta db/002_add_wellness.sql en Supabase.")

def competition(user):
    back(); st.title("🏆 Competición")
    with st.form("comp"):
        day=st.date_input("Fecha",date.today()); name=st.text_input("Competición"); venue=st.text_input("Lugar"); a,b=st.columns(2); event=a.selectbox("Prueba",["60m","100m","200m","400m","4x100","other"]); rnd=b.selectbox("Ronda",["Serie","Semifinal","Final","Otra"]); a,b=st.columns(2); result=a.number_input("Marca (s)",0.0,120.0,0.0,0.01,format="%.3f"); wind=b.number_input("Viento (m/s)",-10.0,10.0,0.0,0.1,format="%.1f"); lane=st.number_input("Calle",1,9,4); reaction=st.number_input("Reacción (s, opcional)",0.0,2.0,0.0,0.001,format="%.3f"); position=st.number_input("Posición",1,99,1); notes=st.text_area("Comentarios"); save=st.form_submit_button("Guardar competición")
    if save:
        if not name or result<=0: st.warning("Introduce nombre y marca.")
        else:
            try: supabase.table("competitions").insert({"athlete_id":user.id,"competition_date":str(day),"competition_name":name,"venue":venue or None,"event":event,"round":rnd,"lane":int(lane),"reaction_time":float(reaction) if reaction>0 else None,"result_seconds":float(result),"wind":float(wind),"position":int(position),"notes":notes or None}).execute(); go_home_with_message("Competición guardada correctamente.")
            except Exception as e: st.error(f"No se pudo guardar: {e}")

def cycle(user,profile):
    back(); st.title("🌸 Ciclo menstrual")
    if profile.get("sex")!="female": st.info("Este módulo solo aparece para perfiles configurados como mujer."); return
    st.caption("Cada registro puede mantenerse privado o compartirse con el entrenador.")
    with st.form("cycle"):
        start=st.date_input("Inicio de la menstruación",date.today()); ended=st.checkbox("Ya ha finalizado"); end=st.date_input("Fin de la menstruación",date.today(),disabled=not ended); share=st.checkbox("Compartir este registro con mi entrenador",False); notes=st.text_area("Notas"); save=st.form_submit_button("Guardar ciclo")
    if save: supabase.table("menstrual_cycles").insert({"athlete_id":user.id,"start_date":str(start),"end_date":str(end) if ended else None,"share_with_coach":share,"notes":notes or None}).execute(); st.success("Registro guardado.")

def _render_athlete_load(df,title,value_col,unit,aggregation,key,fixed_rpe=False):
    st.subheader(title); period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"athlete_period_{key}"); x=_period_label(df,"session_date",period); agg=x.groupby("periodo",as_index=False)[value_col].agg(aggregation).sort_values("periodo")
    if fixed_rpe: _fixed_axis_chart(agg,"periodo",value_col,ymin=0,ymax=10)
    else: _zero_floor_chart(agg,"periodo",value_col)
    st.dataframe(agg.rename(columns={"periodo":period,value_col:title}),use_container_width=True,hide_index=True); st.caption(f"{period}: {'media' if aggregation=='mean' else 'suma'} · Unidad: {unit}")

def _render_single_wellness(df,metric,label,key_prefix="athlete"):
    period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"{key_prefix}_wellness_period_{metric}"); x=_period_label(df,"entry_date",period); agg=x.groupby("periodo",as_index=False)[metric].mean().sort_values("periodo"); _fixed_axis_chart(agg,"periodo",metric,ymin=1,ymax=5); st.dataframe(agg.rename(columns={"periodo":period,metric:label}),use_container_width=True,hide_index=True); st.caption(f"Media de {label.lower()} por {period.lower()} · Escala 1–5.")

def _render_wellness_summary(rows):
    if not rows: st.info("Todavía no hay registros de wellness."); return
    df=pd.DataFrame(rows); df["entry_date"]=pd.to_datetime(df["entry_date"])
    for metric in WELLNESS_LABELS: df[metric]=pd.to_numeric(df[metric],errors="coerce")
    tabs=st.tabs([f"{icon} {WELLNESS_LABELS[m]}" for icon,m in zip(["😴","🔋","💪","🧠","✅"],WELLNESS_LABELS)])
    for tab,metric in zip(tabs,WELLNESS_LABELS):
        with tab: _render_single_wellness(df,metric,WELLNESS_LABELS[metric],"athlete")

def evolution(user):
    back(); st.title("📈 Mi evolución")
    sessions=supabase.table("training_sessions").select("session_date,volume_m,rpe,srpe_load").eq("athlete_id",user.id).order("session_date").limit(500).execute().data or []
    try: wellness_rows=supabase.table("wellness_entries").select("entry_date,sleep,fatigue,muscle_soreness,stress,readiness").eq("athlete_id",user.id).order("entry_date").limit(500).execute().data or []
    except Exception: wellness_rows=[]
    t1,t2,t3=st.tabs(["🏅 Marcas","📊 Carga","❤️ Bienestar"])
    with t1: _render_marks(user.id,"athlete_evolution",editable=True)
    with t2:
        if not sessions: st.info("Todavía no hay entrenamientos.")
        else:
            df=pd.DataFrame(sessions); df["session_date"]=pd.to_datetime(df["session_date"])
            for c in ["volume_m","rpe","srpe_load"]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
            a,b,c=st.tabs(["📏 Metros","🎯 RPE","⚡ Metros × RPE"])
            with a: _render_athlete_load(df,"Metros","volume_m","m","sum","meters")
            with b: _render_athlete_load(df,"RPE","rpe","0–10","mean","rpe",True)
            with c: _render_athlete_load(df,"Metros × RPE","srpe_load","UA","sum","load")
    with t3: _render_wellness_summary(wellness_rows)

def profile_page(user,profile):
    back(); st.title("👤 Mi perfil"); opts=["100 m","200 m","100/200 m"]
    with st.form("profile"):
        name=st.text_input("Nombre y apellidos",profile.get("full_name") or ""); sex=st.selectbox("Sexo",["male","female"],index=1 if profile.get("sex")=="female" else 0,format_func=lambda x:"Mujer" if x=="female" else "Hombre"); current=profile.get("specialty") if profile.get("specialty") in opts else "100/200 m"; spec=st.selectbox("Especialidad",opts,index=opts.index(current)); save=st.form_submit_button("Guardar perfil")
    if save: supabase.table("profiles").update({"full_name":name,"sex":sex,"specialty":spec}).eq("id",user.id).execute(); st.session_state.profile=get_profile(user.id); st.success("Perfil actualizado."); st.rerun()

def coach_athletes(user):
    back("home"); st.title("👥 Mis atletas"); st.caption("Selecciona un atleta para abrir su ficha completa."); athletes=supabase.table("profiles").select("id,full_name,email,specialty,sex").eq("coach_id",user.id).order("full_name").execute().data
    if not athletes: st.info("Todavía no tienes atletas asignados."); return
    for a in athletes:
        with st.container(border=True):
            st.markdown(f"### {a.get('full_name') or a.get('email')}"); st.caption(a.get("specialty") or "100 / 200 m")
            if st.button("Ver ficha del atleta",key=f"athlete_{a['id']}"): st.session_state.selected_athlete=a; st.session_state.view="coach_athlete_detail"; st.rerun()

def safe_query(table,select,athlete_id,order=None,limit=100,extra=None):
    try:
        q=supabase.table(table).select(select).eq("athlete_id",athlete_id)
        if extra: q=extra(q)
        if order: q=q.order(order)
        return q.limit(limit).execute().data or []
    except Exception: return []

def _render_health_summary(sessions):
    if not sessions: st.info("Todavía no hay entrenamientos registrados."); return
    df=pd.DataFrame(sessions)
    if "health_status" not in df.columns: st.info("Todavía no hay registros de finalización de entreno."); return
    health=df[df["health_status"].notna()].copy()
    if health.empty: st.info("Los entrenamientos anteriores todavía no tienen registro de finalización."); return
    health["estado"]=health["health_status"].map(HEALTH_LABELS); counts=health["estado"].value_counts().rename_axis("estado").reset_index(name="entrenamientos"); st.subheader("Entrenamientos completados"); c1,c2,c3=st.columns(3); c1.metric("Sin problemas",int((health["health_status"]=="completed_no_problem").sum())); c2.metric("Con problema o adaptado",int(health["health_status"].isin(["completed_with_health_problem","adapted_due_health_problem"]).sum())); c3.metric("No completados",int((health["health_status"]=="not_completed_due_health_problem").sum())); _zero_floor_chart(counts,"estado","entrenamientos",mark="bar"); cols=[c for c in ["session_date","volume_m","rpe","estado","notes"] if c in health.columns]; st.dataframe(health[cols].sort_values("session_date",ascending=False),use_container_width=True,hide_index=True)

def _render_activity_days(sessions,column,title,icon):
    st.subheader(f"{icon} {title}")
    if not sessions: st.info("Todavía no hay entrenamientos registrados."); return
    df=pd.DataFrame(sessions)
    if column not in df.columns: st.info("Todavía no hay datos registrados."); return
    yes=df[df[column]==True].copy(); st.metric(f"Días con {title.lower()}",len(yes))
    if yes.empty: st.info(f"Todavía no hay días registrados con {title.lower()}.")
    else: st.dataframe(yes[[c for c in ["session_date","volume_m","rpe","notes"] if c in yes.columns]].sort_values("session_date",ascending=False),use_container_width=True,hide_index=True)

def coach_athlete_detail(user):
    back("coach_athletes","Volver a Mis atletas"); a=st.session_state.get("selected_athlete")
    if not a: st.session_state.view="coach_athletes"; st.rerun()
    st.title(f"👤 {a.get('full_name') or a.get('email')}"); st.caption(a.get("specialty") or "100 / 200 m"); aid=a["id"]
    sessions=safe_query("training_sessions","id,session_date,volume_m,rpe,srpe_load,did_gym,did_plyometrics,health_status,notes",aid,"session_date",120); wellness_rows=safe_query("wellness_entries","entry_date,sleep,fatigue,muscle_soreness,stress,readiness,notes",aid,"entry_date",120); comps=safe_query("competitions","competition_date,competition_name,event,round,result_seconds,wind,position",aid,"competition_date",100); cycles=safe_query("menstrual_cycles","start_date,end_date,notes,share_with_coach",aid,"start_date",50,lambda q:q.eq("share_with_coach",True))
    tabs=st.tabs(["Entrenamientos","Entrenamientos completados","Series","Gimnasio","Pliometría","RPE","Wellness","Competiciones","Ciclo compartido","Carga","Marcas"])
    with tabs[0]:
        if sessions:
            df=pd.DataFrame(sessions); df["estado_salud"]=df["health_status"].map(HEALTH_LABELS); st.dataframe(df[[c for c in ["session_date","volume_m","rpe","srpe_load","estado_salud","notes"] if c in df.columns]],use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay entrenamientos registrados.")
    with tabs[1]: _render_health_summary(sessions)
    with tabs[2]:
        if not sessions: st.info("Todavía no hay series registradas.")
        else:
            session_ids=[x["id"] for x in sessions]
            try:
                sets=supabase.table("sprint_sets").select("id,session_id,set_order,distance_m,repetitions,recovery_seconds").in_("session_id",session_ids).order("set_order").execute().data or []; set_ids=[s["id"] for s in sets]; reps=supabase.table("sprint_reps").select("sprint_set_id,rep_number,time_seconds").in_("sprint_set_id",set_ids).order("rep_number").execute().data if set_ids else []; date_by_session={x["id"]:x["session_date"] for x in sessions}; reps_by_set={}
                for r in reps or []: reps_by_set.setdefault(r["sprint_set_id"],[]).append(r)
                rows=[]; counters={}
                for s in sets:
                    sid=s.get("session_id"); counters[sid]=counters.get(sid,0); set_reps=sorted(reps_by_set.get(s["id"],[]),key=lambda r:r.get("rep_number",0))
                    if not set_reps: set_reps=[{"rep_number":n,"time_seconds":None} for n in range(1,int(s.get("repetitions") or 1)+1)]
                    for r in set_reps:
                        counters[sid]+=1; rows.append({"fecha":date_by_session.get(sid),"serie":counters[sid],"metros":s.get("distance_m"),"tiempo_s":r.get("time_seconds"),"recuperación_min":round((s.get("recovery_seconds") or 0)/60,2)})
                if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                else: st.info("No hay series registradas.")
            except Exception as e: st.warning(f"No se pudieron cargar las series: {e}")
    with tabs[3]: _render_activity_days(sessions,"did_gym","Gimnasio","🏋️")
    with tabs[4]: _render_activity_days(sessions,"did_plyometrics","Pliometría","🦘")
    with tabs[5]:
        if sessions:
            df=pd.DataFrame(sessions); df["session_date"]=pd.to_datetime(df["session_date"]); _fixed_axis_chart(df,"session_date","rpe",ymin=0,ymax=10); st.dataframe(df[["session_date","volume_m","rpe","srpe_load"]],use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay datos de RPE.")
    with tabs[6]: _render_wellness_summary(wellness_rows)
    with tabs[7]:
        if comps: st.dataframe(pd.DataFrame(comps),use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay competiciones registradas.")
    with tabs[8]:
        if a.get("sex")!="female": st.info("Este atleta no tiene activo el módulo de ciclo menstrual.")
        elif cycles: st.dataframe(pd.DataFrame(cycles)[["start_date","end_date","notes"]],use_container_width=True,hide_index=True)
        else: st.info("No hay registros del ciclo compartidos con el entrenador.")
    with tabs[9]:
        if not sessions: st.info("Todavía no hay entrenamientos registrados.")
        else:
            df=pd.DataFrame(sessions); df["session_date"]=pd.to_datetime(df["session_date"])
            for col in ["volume_m","rpe","srpe_load"]: df[col]=pd.to_numeric(df[col],errors="coerce").fillna(0)
            m_tab,r_tab,l_tab=st.tabs(["📏 Metros","🎯 RPE","⚡ Metros × RPE"])
            with m_tab: _render_athlete_load(df,"Metros","volume_m","m","sum","coach_detail_meters")
            with r_tab: _render_athlete_load(df,"RPE","rpe","0–10","mean","coach_detail_rpe",True)
            with l_tab: _render_athlete_load(df,"Metros × RPE","srpe_load","UA","sum","coach_detail_load")
    with tabs[10]: _render_marks(aid,"coach_athlete",editable=False)

def _period_series(df,value_col,period,aggregation):
    x=_period_label(df,"session_date",period); return x.pivot_table(index="periodo",columns="atleta",values=value_col,aggfunc=aggregation,fill_value=0).sort_index()

def _render_group_metric(df,title,value_col,unit,aggregation,key):
    st.subheader(title); period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"period_{key}"); series=_period_series(df,value_col,period,aggregation)
    if series.empty: st.info("No hay datos para este periodo."); return
    long=series.reset_index().melt(id_vars="periodo",var_name="atleta",value_name="valor")
    if value_col=="rpe": _fixed_axis_chart(long,"periodo","valor","atleta",0,10)
    else: _zero_floor_chart(long,"periodo","valor","atleta")
    st.dataframe(series.reset_index().rename(columns={"periodo":period}),use_container_width=True,hide_index=True); st.caption(f"{period}: {'media' if aggregation=='mean' else 'suma'} · Unidad: {unit}")
    comparison=df.groupby("atleta",as_index=False)[value_col].mean().rename(columns={value_col:"valor"}) if aggregation=="mean" else df.groupby("atleta",as_index=False)[value_col].sum().rename(columns={value_col:"valor"}); comparison=comparison.sort_values("valor",ascending=False); st.markdown("**Comparativa del grupo**")
    if value_col=="rpe": _fixed_axis_chart(comparison,"atleta","valor",ymin=0,ymax=10,mark="bar")
    else: _zero_floor_chart(comparison,"atleta","valor",mark="bar")
    st.dataframe(comparison.rename(columns={"valor":title}),use_container_width=True,hide_index=True)

def _render_group_wellness_metric(df,metric,label):
    period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"coach_wellness_period_{metric}"); x=_period_label(df,"entry_date",period); series=x.pivot_table(index="periodo",columns="atleta",values=metric,aggfunc="mean").sort_index()
    if series.empty: st.info("No hay datos para este periodo."); return
    long=series.reset_index().melt(id_vars="periodo",var_name="atleta",value_name="valor").dropna(subset=["valor"]); _fixed_axis_chart(long,"periodo","valor","atleta",1,5); st.dataframe(series.reset_index().rename(columns={"periodo":period}),use_container_width=True,hide_index=True); comparison=df.groupby("atleta",as_index=False)[metric].mean().rename(columns={metric:"valor"}).dropna(subset=["valor"]).sort_values("valor",ascending=False); st.markdown("**Comparativa del grupo**"); _fixed_axis_chart(comparison,"atleta","valor",ymin=1,ymax=5,mark="bar"); st.dataframe(comparison.rename(columns={"valor":label}),use_container_width=True,hide_index=True); st.caption(f"Media de {label.lower()} · Escala 1–5.")

def _render_group_wellness(rows,names):
    if not rows: st.info("Todavía no hay registros de bienestar del grupo."); return
    df=pd.DataFrame(rows); df["entry_date"]=pd.to_datetime(df["entry_date"]); df["atleta"]=df["athlete_id"].map(names)
    for metric in WELLNESS_LABELS: df[metric]=pd.to_numeric(df[metric],errors="coerce")
    tabs=st.tabs([f"{icon} {WELLNESS_LABELS[m]}" for icon,m in zip(["😴","🔋","💪","🧠","✅"],WELLNESS_LABELS)])
    for tab,metric in zip(tabs,WELLNESS_LABELS):
        with tab: _render_group_wellness_metric(df,metric,WELLNESS_LABELS[metric])

def coach_group_load(user):
    back("home"); st.title("📊 Carga y bienestar del grupo"); st.caption("Analiza carga y bienestar por día, semana o mes y compara a los atletas del grupo."); athletes=supabase.table("profiles").select("id,full_name,email").eq("coach_id",user.id).execute().data
    if not athletes: st.info("Todavía no tienes atletas asignados."); return
    names={a["id"]:(a.get("full_name") or a.get("email")) for a in athletes}; ids=list(names)
    try: rows=supabase.table("training_sessions").select("athlete_id,session_date,volume_m,rpe,srpe_load").in_("athlete_id",ids).order("session_date").limit(1000).execute().data or []
    except Exception as e: st.warning(f"No se pudo cargar la carga del grupo: {e}"); rows=[]
    try: wellness_rows=supabase.table("wellness_entries").select("athlete_id,entry_date,sleep,fatigue,muscle_soreness,stress,readiness").in_("athlete_id",ids).order("entry_date").limit(2000).execute().data or []
    except Exception as e: st.warning(f"No se pudo cargar el bienestar del grupo: {e}"); wellness_rows=[]
    t1,t2,t3,t4=st.tabs(["📏 Metros","🎯 RPE","⚡ Metros × RPE","❤️ Bienestar"])
    if rows:
        df=pd.DataFrame(rows); df["session_date"]=pd.to_datetime(df["session_date"]); df["atleta"]=df["athlete_id"].map(names)
        for c in ["volume_m","rpe","srpe_load"]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
        with t1: _render_group_metric(df,"Metros","volume_m","m","sum","meters")
        with t2: _render_group_metric(df,"RPE","rpe","0–10","mean","rpe")
        with t3: _render_group_metric(df,"Metros × RPE","srpe_load","UA","sum","load")
    else:
        with t1: st.info("Todavía no hay entrenamientos del grupo.")
        with t2: st.info("Todavía no hay entrenamientos del grupo.")
        with t3: st.info("Todavía no hay entrenamientos del grupo.")
    with t4: _render_group_wellness(wellness_rows,names)

def coach_home(user,profile):
    header(profile,"ENTRENADOR"); c1,c2=st.columns(2); card(c1,"👥","Mis atletas","Consulta el grupo",1,"coach_athletes","coach_m1"); card(c2,"📊","Carga del grupo","Carga y bienestar",2,"coach_group_load","coach_m2"); st.divider()
    if st.button("Cerrar sesión"): sign_out()

user=login()
if "profile" not in st.session_state: st.session_state.profile=get_profile(user.id)
profile=st.session_state.profile; view=st.session_state.get("view","home")
if profile.get("role")=="coach":
    {"home":lambda:coach_home(user,profile),"coach_athletes":lambda:coach_athletes(user),"coach_athlete_detail":lambda:coach_athlete_detail(user),"coach_group_load":lambda:coach_group_load(user)}.get(view,lambda:coach_home(user,profile))()
else:
    {"home":lambda:athlete_home(user,profile),"training":lambda:training(user),"wellness":lambda:wellness(user),"cycle":lambda:cycle(user,profile),"competition":lambda:competition(user),"evolution":lambda:evolution(user),"profile":lambda:profile_page(user,profile)}.get(view,lambda:athlete_home(user,profile))()
