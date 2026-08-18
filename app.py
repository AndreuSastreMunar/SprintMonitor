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

supabase = get_supabase()
WELLNESS_LABELS={"sleep":"Sueño","fatigue":"Fatiga","muscle_soreness":"Dolor muscular","stress":"Estrés","readiness":"Disposición para entrenar"}
HEALTH_LABELS={
    "completed_no_problem":"Completado sin problemas de salud",
    "completed_with_health_problem":"Completado con algún problema de salud",
    "adapted_due_health_problem":"Adaptado por problemas de salud",
    "not_completed_due_health_problem":"No completado por problemas de salud",
}


def get_profile(uid): return supabase.table("profiles").select("*").eq("id", uid).single().execute().data


def sign_out():
    try: supabase.auth.sign_out()
    except Exception: pass
    for k in ["user","profile","view","blocks","selected_athlete"]: st.session_state.pop(k, None)
    st.rerun()


def login():
    if "user" in st.session_state: return st.session_state.user
    st.markdown('<div class="brand">SPRINT MONITOR</div><div class="hello">100 / 200 m</div><div class="sub">Entrenamiento, bienestar, competición y evolución.</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="hero"><div class="brand">SPRINT MONITOR</div><div class="hello">Hola, {name}</div><div class="sub">{profile.get("specialty") or "100 / 200 m"} · {label}</div></div>', unsafe_allow_html=True)


def card(col,icon,title,subtitle,number,target,key):
    with col:
        st.markdown(f'<div class="menu-card"><div class="menu-icon">{icon}</div><div class="menu-title">{title}</div><div class="menu-sub">{subtitle}</div><div class="menu-num">{number}</div></div>',unsafe_allow_html=True)
        if st.button(f"Abrir {title}",key=key): st.session_state.view=target; st.rerun()


def back(target="home",label="Volver al inicio"):
    if st.button(f"← {label}"): st.session_state.view=target; st.rerun()


def _fixed_axis_chart(df, x_col, value_col, series_col=None, ymin=0, ymax=10, mark="line"):
    data=df.copy()
    data[x_col]=pd.to_datetime(data[x_col]).dt.strftime("%Y-%m-%d") if pd.api.types.is_datetime64_any_dtype(data[x_col]) else data[x_col]
    enc={"x":{"field":x_col,"type":"temporal" if x_col in ["periodo","session_date","entry_date"] else "nominal","title":None},"y":{"field":value_col,"type":"quantitative","scale":{"domain":[ymin,ymax]},"title":None}}
    if series_col: enc["color"]={"field":series_col,"type":"nominal","title":None}
    spec={"mark":{"type":mark,"point":True if mark=="line" else False},"encoding":enc,"data":{"values":data.to_dict("records")}}
    st.vega_lite_chart(spec,use_container_width=True)


def _zero_floor_chart(df, x_col, value_col, series_col=None, mark="line"):
    data=df.copy()
    data[x_col]=pd.to_datetime(data[x_col]).dt.strftime("%Y-%m-%d") if pd.api.types.is_datetime64_any_dtype(data[x_col]) else data[x_col]
    enc={"x":{"field":x_col,"type":"temporal" if x_col in ["periodo","session_date","entry_date"] else "nominal","title":None},"y":{"field":value_col,"type":"quantitative","scale":{"domainMin":0},"title":None}}
    if series_col: enc["color"]={"field":series_col,"type":"nominal","title":None}
    spec={"mark":{"type":mark,"point":True if mark=="line" else False},"encoding":enc,"data":{"values":data.to_dict("records")}}
    st.vega_lite_chart(spec,use_container_width=True)


def _period_label(df,date_col,period):
    x=df.copy(); x[date_col]=pd.to_datetime(x[date_col])
    if period=="Día": x["periodo"]=x[date_col].dt.floor("D")
    elif period=="Semana": x["periodo"]=x[date_col].dt.to_period("W").apply(lambda p:p.start_time)
    else: x["periodo"]=x[date_col].dt.to_period("M").apply(lambda p:p.start_time)
    return x


def athlete_home(user,profile):
    header(profile,"ATLETA"); c1,c2=st.columns(2); card(c1,"🏃","Entrenamiento","Series, tiempos y RPE",1,"training","m1"); card(c2,"❤️","Wellness","Cómo te encuentras hoy",2,"wellness","m2")
    if profile.get("sex")=="female":
        c3,c4=st.columns(2); card(c3,"🌸","Ciclo menstrual","Registro privado",3,"cycle","m3"); card(c4,"🏆","Competición","60, 100, 200 y 400 m",4,"competition","m4")
        st.markdown('<div class="menu-card"><div class="menu-icon">📈</div><div class="menu-title">Mi evolución</div><div class="menu-sub">Marcas, carga y bienestar</div><div class="menu-num">5</div></div>',unsafe_allow_html=True)
        if st.button("Abrir Mi evolución",key="m5"): st.session_state.view="evolution"; st.rerun()
    else:
        c3,c4=st.columns(2); card(c3,"🏆","Competición","60, 100, 200 y 400 m",3,"competition","m3m"); card(c4,"📈","Mi evolución","Marcas, carga y bienestar",4,"evolution","m4m")
    st.divider()
    if st.button("👤 Mi perfil"): st.session_state.view="profile"; st.rerun()
    if st.button("Cerrar sesión"): sign_out()


def training(user):
    back(); st.title("🏃 Entrenamiento"); st.caption("RPE única para toda la sesión.")
    if "blocks" not in st.session_state: st.session_state.blocks=[{"d":60.0,"r":3,"rec":6.0,"t":[0.0,0.0,0.0]}]
    day=st.date_input("Fecha",date.today()); duration=st.number_input("Duración total (min)",1,300,75); rpe=st.slider("RPE global",0.0,10.0,5.0,0.5); notes=st.text_area("Comentarios generales"); updated=[]
    for i,b in enumerate(st.session_state.blocks):
        with st.container(border=True):
            st.markdown(f"**Bloque {i+1}**"); x,y,z=st.columns(3); d=x.number_input("Metros",1.0,500.0,float(b["d"]),5.0,key=f"d{i}"); reps=y.number_input("Veces",1,20,int(b["r"]),key=f"r{i}"); rec=z.number_input("Recuperación (min)",0.0,30.0,float(b["rec"]),0.5,key=f"rec{i}"); old=(list(b["t"])+[0.0]*reps)[:reps]; times=[]
            for n in range(reps): times.append(st.number_input(f"Tiempo rep. {n+1} (s)",0.0,120.0,float(old[n]),0.01,format="%.3f",key=f"t{i}_{n}"))
            valid=[x for x in times if x>0]; st.caption(f"Volumen: {d*reps:.0f} m"+(f" · Mejor: {min(valid):.3f} s" if valid else ""))
            if st.button("Eliminar bloque",key=f"del{i}",disabled=len(st.session_state.blocks)==1): st.session_state.blocks.pop(i); st.rerun()
            updated.append({"d":d,"r":int(reps),"rec":rec,"t":times})
    st.session_state.blocks=updated
    if st.button("➕ Añadir bloque"): st.session_state.blocks.append({"d":60.0,"r":1,"rec":5.0,"t":[0.0]}); st.rerun()
    total=sum(b["d"]*b["r"] for b in st.session_state.blocks); st.info(f"Volumen total: **{total:.0f} m** · RPE: **{rpe:g}** · Carga: **{total*rpe:.0f} UA**")

    st.markdown("### Estado de salud al finalizar")
    completed_ok=st.radio("¿Has podido completar todo el entrenamiento sin ningún problema de salud?",["Sí","No"],horizontal=True,key="health_completed_ok")
    health_status="completed_no_problem"
    if completed_ok=="No":
        reason=st.radio("Indica el motivo",[
            "He completado el entrenamiento con algún problema de salud.",
            "He adaptado el entrenamiento debido a problemas de salud.",
            "No he podido completar el entrenamiento debido a problemas de salud.",
        ],key="health_reason")
        health_status={
            "He completado el entrenamiento con algún problema de salud.":"completed_with_health_problem",
            "He adaptado el entrenamiento debido a problemas de salud.":"adapted_due_health_problem",
            "No he podido completar el entrenamiento debido a problemas de salud.":"not_completed_due_health_problem",
        }[reason]

    if st.button("💾 Guardar entrenamiento",type="primary"):
        try:
            s=supabase.table("training_sessions").insert({"athlete_id":user.id,"session_date":str(day),"duration_minutes":int(duration),"rpe":float(rpe),"health_status":health_status,"notes":notes or None}).execute().data[0]
            for order,b in enumerate(st.session_state.blocks,1):
                ss=supabase.table("sprint_sets").insert({"session_id":s["id"],"set_order":order,"distance_m":float(b["d"]),"repetitions":b["r"],"recovery_seconds":int(round(b["rec"]*60))}).execute().data[0]
                rows=[{"sprint_set_id":ss["id"],"rep_number":n,"time_seconds":float(t) if t>0 else None} for n,t in enumerate(b["t"],1)]; supabase.table("sprint_reps").insert(rows).execute()
            st.success("Entrenamiento guardado.")
        except Exception as e: st.error(f"No se pudo guardar: {e}")


def wellness(user):
    back(); st.title("❤️ Wellness")
    with st.form("wellness_form"):
        day=st.date_input("Fecha",date.today()); sleep=st.slider("Sueño",1,5,3); fatigue=st.slider("Fatiga",1,5,3); soreness=st.slider("Dolor muscular",1,5,3); stress=st.slider("Estrés",1,5,3); readiness=st.slider("Disposición para entrenar",1,5,3); notes=st.text_area("Comentarios"); save=st.form_submit_button("Guardar wellness",use_container_width=True)
    if save:
        try: supabase.table("wellness_entries").upsert({"athlete_id":user.id,"entry_date":str(day),"sleep":sleep,"fatigue":fatigue,"muscle_soreness":soreness,"stress":stress,"readiness":readiness,"notes":notes or None},on_conflict="athlete_id,entry_date").execute(); st.success("Wellness guardado.")
        except Exception: st.error("Primero ejecuta db/002_add_wellness.sql en Supabase.")


def competition(user):
    back(); st.title("🏆 Competición")
    with st.form("comp"):
        day=st.date_input("Fecha",date.today()); name=st.text_input("Competición"); venue=st.text_input("Lugar"); a,b=st.columns(2); event=a.selectbox("Prueba",["60m","100m","200m","400m","4x100","other"]); rnd=b.selectbox("Ronda",["Serie","Semifinal","Final","Otra"]); a,b=st.columns(2); result=a.number_input("Marca (s)",0.0,120.0,0.0,0.01,format="%.3f"); wind=b.number_input("Viento (m/s)",-10.0,10.0,0.0,0.1,format="%.1f"); lane=st.number_input("Calle",1,9,4); reaction=st.number_input("Reacción (s, opcional)",0.0,2.0,0.0,0.001,format="%.3f"); position=st.number_input("Posición",1,99,1); notes=st.text_area("Comentarios"); save=st.form_submit_button("Guardar competición")
    if save:
        if not name or result<=0: st.warning("Introduce nombre y marca.")
        else: supabase.table("competitions").insert({"athlete_id":user.id,"competition_date":str(day),"competition_name":name,"venue":venue or None,"event":event,"round":rnd,"lane":int(lane),"reaction_time":float(reaction) if reaction>0 else None,"result_seconds":float(result),"wind":float(wind),"position":int(position),"notes":notes or None}).execute(); st.success("Competición guardada.")


def cycle(user,profile):
    back(); st.title("🌸 Ciclo menstrual")
    if profile.get("sex")!="female": st.info("Este módulo solo aparece para perfiles configurados como mujer."); return
    st.caption("Cada registro puede mantenerse privado o compartirse con el entrenador.")
    with st.form("cycle"):
        start=st.date_input("Inicio de la menstruación",date.today()); ended=st.checkbox("Ya ha finalizado"); end=st.date_input("Fin de la menstruación",date.today(),disabled=not ended); share=st.checkbox("Compartir este registro con mi entrenador",False); notes=st.text_area("Notas"); save=st.form_submit_button("Guardar ciclo")
    if save: supabase.table("menstrual_cycles").insert({"athlete_id":user.id,"start_date":str(start),"end_date":str(end) if ended else None,"share_with_coach":share,"notes":notes or None}).execute(); st.success("Registro guardado.")


def _render_athlete_load(df,title,value_col,unit,aggregation,key,fixed_rpe=False):
    st.subheader(title); period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"athlete_period_{key}")
    x=_period_label(df,"session_date",period); agg=x.groupby("periodo",as_index=False)[value_col].agg(aggregation).sort_values("periodo")
    if fixed_rpe: _fixed_axis_chart(agg,"periodo",value_col,ymin=0,ymax=10)
    elif value_col=="volume_m": _zero_floor_chart(agg,"periodo",value_col)
    else: st.line_chart(agg.set_index("periodo")[[value_col]])
    st.dataframe(agg.rename(columns={"periodo":period,value_col:title}),use_container_width=True,hide_index=True)
    st.caption(f"{period}: {'media' if aggregation=='mean' else 'suma'} · Unidad: {unit}")


def _render_single_wellness(df, metric, label, key_prefix="athlete"):
    period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"{key_prefix}_wellness_period_{metric}")
    x=_period_label(df,"entry_date",period); agg=x.groupby("periodo",as_index=False)[metric].mean().sort_values("periodo")
    _fixed_axis_chart(agg,"periodo",metric,ymin=1,ymax=5)
    st.dataframe(agg.rename(columns={"periodo":period,metric:label}),use_container_width=True,hide_index=True)
    st.caption(f"Media de {label.lower()} por {period.lower()} · Escala 1–5.")


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
    comps=supabase.table("competitions").select("competition_date,event,result_seconds,wind,competition_name").eq("athlete_id",user.id).order("competition_date").limit(200).execute().data or []
    try: wellness_rows=supabase.table("wellness_entries").select("entry_date,sleep,fatigue,muscle_soreness,stress,readiness").eq("athlete_id",user.id).order("entry_date").limit(500).execute().data or []
    except Exception: wellness_rows=[]
    t1,t2,t3=st.tabs(["🏅 Mejor marca","📊 Carga","❤️ Bienestar"])
    with t1:
        st.subheader("Mejor marca de la temporada")
        if not comps: st.info("Todavía no hay competiciones registradas.")
        else:
            cdf=pd.DataFrame(comps); cdf["competition_date"]=pd.to_datetime(cdf["competition_date"]); years=sorted(cdf["competition_date"].dt.year.dropna().unique().tolist(),reverse=True); season=st.selectbox("Temporada",years,index=0)
            season_df=cdf[cdf["competition_date"].dt.year==season]; cols=st.columns(2); events=["60m","100m","200m","400m"]
            for i,event in enumerate(events):
                edf=season_df[(season_df["event"]==event)&(pd.to_numeric(season_df["result_seconds"],errors="coerce")>0)].copy()
                with cols[i%2]:
                    with st.container(border=True):
                        st.markdown(f"### {event.replace('m',' m')}")
                        if edf.empty: st.caption("Sin marca registrada")
                        else:
                            best=edf.loc[pd.to_numeric(edf["result_seconds"],errors="coerce").idxmin()]; st.metric("Mejor marca",f"{float(best['result_seconds']):.3f} s"); st.caption(f"{best['competition_date'].date()} · {best.get('competition_name') or ''}")
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
    back("home"); st.title("👥 Mis atletas"); st.caption("Selecciona un atleta para abrir su ficha completa.")
    athletes=supabase.table("profiles").select("id,full_name,email,specialty,sex").eq("coach_id",user.id).order("full_name").execute().data
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
    if "health_status" not in df.columns: st.info("Todavía no hay registros de salud en los entrenamientos."); return
    health=df[df["health_status"].notna()].copy()
    if health.empty: st.info("Los entrenamientos anteriores todavía no tienen registro de salud."); return
    health["estado"]=health["health_status"].map(HEALTH_LABELS)
    counts=health["estado"].value_counts().rename_axis("estado").reset_index(name="entrenamientos")
    st.subheader("Registro de salud en entrenamientos")
    c1,c2,c3=st.columns(3)
    c1.metric("Sin problemas",int((health["health_status"]=="completed_no_problem").sum()))
    c2.metric("Con problema o adaptado",int(health["health_status"].isin(["completed_with_health_problem","adapted_due_health_problem"]).sum()))
    c3.metric("No completados",int((health["health_status"]=="not_completed_due_health_problem").sum()))
    st.bar_chart(counts.set_index("estado")[["entrenamientos"]])
    cols=[c for c in ["session_date","volume_m","rpe","estado","notes"] if c in health.columns]
    st.dataframe(health[cols].sort_values("session_date",ascending=False),use_container_width=True,hide_index=True)


def coach_athlete_detail(user):
    back("coach_athletes","Volver a Mis atletas"); a=st.session_state.get("selected_athlete")
    if not a: st.session_state.view="coach_athletes"; st.rerun()
    st.title(f"👤 {a.get('full_name') or a.get('email')}"); st.caption(a.get("specialty") or "100 / 200 m"); aid=a["id"]
    sessions=safe_query("training_sessions","id,session_date,duration_minutes,volume_m,rpe,srpe_load,health_status,notes",aid,"session_date",120)
    wellness_rows=safe_query("wellness_entries","entry_date,sleep,fatigue,muscle_soreness,stress,readiness,notes",aid,"entry_date",120)
    comps=safe_query("competitions","competition_date,competition_name,event,round,result_seconds,wind,position",aid,"competition_date",100)
    cycles=safe_query("menstrual_cycles","start_date,end_date,notes,share_with_coach",aid,"start_date",50,lambda q:q.eq("share_with_coach",True))
    tabs=st.tabs(["Entrenamientos","Salud en entrenamientos","Series y tiempos","RPE","Wellness","Competiciones","Ciclo compartido","Evolución"])
    with tabs[0]:
        if sessions:
            df=pd.DataFrame(sessions); df["estado_salud"]=df["health_status"].map(HEALTH_LABELS)
            st.dataframe(df[[c for c in ["session_date","volume_m","duration_minutes","rpe","srpe_load","estado_salud","notes"] if c in df.columns]],use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay entrenamientos registrados.")
    with tabs[1]: _render_health_summary(sessions)
    with tabs[2]:
        if not sessions: st.info("Todavía no hay series registradas.")
        else:
            session_ids=[x["id"] for x in sessions]
            try:
                sets=supabase.table("sprint_sets").select("id,session_id,set_order,distance_m,repetitions,recovery_seconds").in_("session_id",session_ids).order("set_order").execute().data or []; set_ids=[x["id"] for x in sets]
                reps=supabase.table("sprint_reps").select("sprint_set_id,rep_number,time_seconds").in_("sprint_set_id",set_ids).order("rep_number").execute().data if set_ids else []
                date_by_session={x["id"]:x["session_date"] for x in sessions}; set_by_id={x["id"]:x for x in sets}; rows=[]
                for r in reps or []:
                    s=set_by_id.get(r["sprint_set_id"],{}); rows.append({"fecha":date_by_session.get(s.get("session_id")),"distancia_m":s.get("distance_m"),"serie":s.get("set_order"),"repetición":r.get("rep_number"),"tiempo_s":r.get("time_seconds"),"recuperación_s":s.get("recovery_seconds")})
                if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                else: st.info("No hay tiempos de repeticiones registrados.")
            except Exception as e: st.warning(f"No se pudieron cargar las series: {e}")
    with tabs[3]:
        if sessions:
            df=pd.DataFrame(sessions); df["session_date"]=pd.to_datetime(df["session_date"]); _fixed_axis_chart(df,"session_date","rpe",ymin=0,ymax=10); st.dataframe(df[["session_date","volume_m","rpe","srpe_load"]],use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay datos de RPE.")
    with tabs[4]: _render_wellness_summary(wellness_rows)
    with tabs[5]:
        if comps: st.dataframe(pd.DataFrame(comps),use_container_width=True,hide_index=True)
        else: st.info("Todavía no hay competiciones registradas.")
    with tabs[6]:
        if a.get("sex")!="female": st.info("Este atleta no tiene activo el módulo de ciclo menstrual.")
        elif cycles: st.dataframe(pd.DataFrame(cycles)[["start_date","end_date","notes"]],use_container_width=True,hide_index=True)
        else: st.info("No hay registros del ciclo compartidos con el entrenador.")
    with tabs[7]:
        if sessions:
            df=pd.DataFrame(sessions); df["session_date"]=pd.to_datetime(df["session_date"]); st.subheader("Carga interna (metros × RPE)"); st.line_chart(df.set_index("session_date")[["srpe_load"]])
        if comps:
            cdf=pd.DataFrame(comps); cdf["competition_date"]=pd.to_datetime(cdf["competition_date"]); st.subheader("Marcas de competición")
            for event in cdf["event"].dropna().unique():
                edf=cdf[cdf["event"]==event].set_index("competition_date"); st.caption(str(event)); st.line_chart(edf[["result_seconds"]])
        if not sessions and not comps: st.info("Todavía no hay datos suficientes para mostrar evolución.")


def _period_series(df, value_col, period, aggregation):
    x=_period_label(df,"session_date",period)
    return x.pivot_table(index="periodo",columns="atleta",values=value_col,aggfunc=aggregation,fill_value=0).sort_index()


def _render_group_metric(df,title,value_col,unit,aggregation,key):
    st.subheader(title); period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"period_{key}")
    series=_period_series(df,value_col,period,aggregation)
    if series.empty: st.info("No hay datos para este periodo."); return
    long=series.reset_index().melt(id_vars="periodo",var_name="atleta",value_name="valor")
    if value_col=="rpe": _fixed_axis_chart(long,"periodo","valor","atleta",0,10)
    elif value_col=="volume_m": _zero_floor_chart(long,"periodo","valor","atleta")
    else: st.line_chart(series)
    table=series.reset_index().rename(columns={"periodo":period}); st.dataframe(table,use_container_width=True,hide_index=True)
    st.caption(f"{period}: {'media' if aggregation=='mean' else 'suma'} · Unidad: {unit}")
    if aggregation=="mean": comparison=df.groupby("atleta",as_index=False)[value_col].mean().rename(columns={value_col:"valor"})
    else: comparison=df.groupby("atleta",as_index=False)[value_col].sum().rename(columns={value_col:"valor"})
    comparison=comparison.sort_values("valor",ascending=False); st.markdown("**Comparativa del grupo**")
    if value_col=="rpe": _fixed_axis_chart(comparison,"atleta","valor",ymin=0,ymax=10,mark="bar")
    elif value_col=="volume_m": _zero_floor_chart(comparison,"atleta","valor",mark="bar")
    else: st.bar_chart(comparison.set_index("atleta")[["valor"]])
    st.dataframe(comparison.rename(columns={"valor":title}),use_container_width=True,hide_index=True)


def _render_group_wellness_metric(df,metric,label):
    period=st.radio("Ver por",["Día","Semana","Mes"],horizontal=True,key=f"coach_wellness_period_{metric}")
    x=_period_label(df,"entry_date",period)
    series=x.pivot_table(index="periodo",columns="atleta",values=metric,aggfunc="mean").sort_index()
    if series.empty: st.info("No hay datos para este periodo."); return
    long=series.reset_index().melt(id_vars="periodo",var_name="atleta",value_name="valor").dropna(subset=["valor"])
    _fixed_axis_chart(long,"periodo","valor","atleta",1,5)
    st.dataframe(series.reset_index().rename(columns={"periodo":period}),use_container_width=True,hide_index=True)
    comparison=df.groupby("atleta",as_index=False)[metric].mean().rename(columns={metric:"valor"}).dropna(subset=["valor"]).sort_values("valor",ascending=False)
    st.markdown("**Comparativa del grupo**")
    _fixed_axis_chart(comparison,"atleta","valor",ymin=1,ymax=5,mark="bar")
    st.dataframe(comparison.rename(columns={"valor":label}),use_container_width=True,hide_index=True)
    st.caption(f"Media de {label.lower()} · Escala 1–5.")


def _render_group_wellness(rows,names):
    if not rows: st.info("Todavía no hay registros de bienestar del grupo."); return
    df=pd.DataFrame(rows); df["entry_date"]=pd.to_datetime(df["entry_date"]); df["atleta"]=df["athlete_id"].map(names)
    for metric in WELLNESS_LABELS: df[metric]=pd.to_numeric(df[metric],errors="coerce")
    tabs=st.tabs([f"{icon} {WELLNESS_LABELS[m]}" for icon,m in zip(["😴","🔋","💪","🧠","✅"],WELLNESS_LABELS)])
    for tab,metric in zip(tabs,WELLNESS_LABELS):
        with tab: _render_group_wellness_metric(df,metric,WELLNESS_LABELS[metric])


def coach_group_load(user):
    back("home"); st.title("📊 Carga y bienestar del grupo"); st.caption("Analiza carga y bienestar por día, semana o mes y compara a los atletas del grupo.")
    athletes=supabase.table("profiles").select("id,full_name,email").eq("coach_id",user.id).execute().data
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
