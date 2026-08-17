from datetime import date
import pandas as pd
import streamlit as st
from db.client import get_supabase

st.set_page_config(
    page_title="Sprint Monitor 100/200",
    page_icon="🏃",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1rem;padding-bottom:3rem}
section[data-testid="stSidebar"]{display:none}
.hero{margin:.2rem 0 1rem}
.brand{font-size:.9rem;font-weight:800;letter-spacing:.14em;opacity:.65}
.hello{font-size:2rem;font-weight:850;line-height:1.05;margin-top:.3rem}
.sub{opacity:.6;margin-top:.25rem}
.menu-card{
  border:1px solid rgba(0,0,0,.08);
  border-radius:24px;
  padding:1.05rem;
  min-height:145px;
  box-shadow:0 8px 24px rgba(0,0,0,.08);
  background:linear-gradient(180deg,#fff,#f7f8fa);
  margin-bottom:.45rem
}
.menu-icon{font-size:2rem}
.menu-title{font-size:1.15rem;font-weight:800;margin-top:.35rem}
.menu-sub{font-size:.9rem;opacity:.65;margin-top:.2rem}
.menu-num{
  display:inline-flex;width:34px;height:34px;border-radius:50%;
  align-items:center;justify-content:center;background:#111827;color:white;
  font-weight:800;margin-top:.75rem
}
.stButton>button{border-radius:16px;min-height:46px;font-weight:700;width:100%}
div[data-testid="stForm"]{border-radius:22px;padding:1rem}
@media(max-width:640px){
 .block-container{padding-left:.85rem;padding-right:.85rem}
 .hello{font-size:1.7rem}
 .menu-card{min-height:132px}
}
</style>
""", unsafe_allow_html=True)

supabase = get_supabase()

def get_profile(uid):
    return supabase.table("profiles").select("*").eq("id", uid).single().execute().data

def sign_out():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for k in ["user","profile","view","blocks"]:
        st.session_state.pop(k, None)
    st.rerun()

def login():
    if "user" in st.session_state:
        return st.session_state.user

    st.markdown('<div class="brand">SPRINT MONITOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="hello">100 / 200 m</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Entrenamiento, bienestar, competición y evolución.</div>', unsafe_allow_html=True)

    a,b = st.tabs(["Entrar","Crear cuenta"])
    with a:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            go = st.form_submit_button("Entrar", use_container_width=True)
        if go:
            try:
                r = supabase.auth.sign_in_with_password({"email":email,"password":password})
                st.session_state.user = r.user
                st.session_state.profile = get_profile(r.user.id)
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo iniciar sesión: {e}")
    with b:
        with st.form("signup"):
            name = st.text_input("Nombre y apellidos")
            email2 = st.text_input("Email", key="signup_email")
            password2 = st.text_input("Contraseña", type="password", key="signup_pw")
            go2 = st.form_submit_button("Crear cuenta", use_container_width=True)
        if go2:
            try:
                supabase.auth.sign_up({
                    "email":email2,"password":password2,
                    "options":{"data":{"full_name":name}}
                })
                st.success("Cuenta creada. Confirma el email si Supabase te lo pide.")
            except Exception as e:
                st.error(f"No se pudo crear la cuenta: {e}")
    st.stop()

def header(profile, label):
    name=(profile.get("full_name") or "Atleta").split()[0]
    st.markdown('<div class="hero"><div class="brand">SPRINT MONITOR</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hello">Hola, {name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub">{profile.get("specialty") or "100 / 200 m"} · {label}</div></div>', unsafe_allow_html=True)

def card(col, icon, title, subtitle, number, target, key):
    with col:
        st.markdown(f"""
        <div class="menu-card">
          <div class="menu-icon">{icon}</div>
          <div class="menu-title">{title}</div>
          <div class="menu-sub">{subtitle}</div>
          <div class="menu-num">{number}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Abrir {title}", key=key):
            st.session_state.view = target
            st.rerun()

def back():
    if st.button("← Volver al inicio"):
        st.session_state.view="home"
        st.rerun()

def athlete_home(user, profile):
    header(profile,"ATLETA")
    c1,c2=st.columns(2)
    card(c1,"🏃","Entrenamiento","Series, tiempos y RPE",1,"training","m1")
    card(c2,"❤️","Wellness","Cómo te encuentras hoy",2,"wellness","m2")

    if profile.get("sex")=="female":
        c3,c4=st.columns(2)
        card(c3,"🌸","Ciclo menstrual","Registro privado",3,"cycle","m3")
        card(c4,"🏆","Competición","100 m y 200 m",4,"competition","m4")
        st.markdown("""
        <div class="menu-card">
          <div class="menu-icon">📈</div>
          <div class="menu-title">Mi evolución</div>
          <div class="menu-sub">Tiempos, carga y competiciones</div>
          <div class="menu-num">5</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Abrir Mi evolución", key="m5"):
            st.session_state.view="evolution"; st.rerun()
    else:
        c3,c4=st.columns(2)
        card(c3,"🏆","Competición","100 m y 200 m",3,"competition","m3m")
        card(c4,"📈","Mi evolución","Tiempos, carga y competiciones",4,"evolution","m4m")

    st.divider()
    if st.button("👤 Mi perfil"):
        st.session_state.view="profile"; st.rerun()
    if st.button("Cerrar sesión"):
        sign_out()

def training(user):
    back(); st.title("🏃 Entrenamiento")
    st.caption("RPE única para toda la sesión.")
    if "blocks" not in st.session_state:
        st.session_state.blocks=[{"d":60.0,"r":3,"rec":6.0,"t":[0.0,0.0,0.0]}]

    day=st.date_input("Fecha",date.today())
    duration=st.number_input("Duración total (min)",1,300,75)
    rpe=st.slider("RPE global",0.0,10.0,5.0,0.5)
    notes=st.text_area("Comentarios generales")

    updated=[]
    for i,b in enumerate(st.session_state.blocks):
        with st.container(border=True):
            st.markdown(f"**Bloque {i+1}**")
            x,y,z=st.columns(3)
            d=x.number_input("Metros",1.0,500.0,float(b["d"]),5.0,key=f"d{i}")
            reps=y.number_input("Veces",1,20,int(b["r"]),key=f"r{i}")
            rec=z.number_input("Recuperación (min)",0.0,30.0,float(b["rec"]),0.5,key=f"rec{i}")
            old=(list(b["t"])+[0.0]*reps)[:reps]
            times=[]
            for n in range(reps):
                times.append(st.number_input(
                    f"Tiempo rep. {n+1} (s)",0.0,120.0,float(old[n]),0.01,
                    format="%.3f",key=f"t{i}_{n}"
                ))
            valid=[x for x in times if x>0]
            st.caption(f"Volumen: {d*reps:.0f} m" + (f" · Mejor: {min(valid):.3f} s" if valid else ""))
            if st.button("Eliminar bloque",key=f"del{i}",disabled=len(st.session_state.blocks)==1):
                st.session_state.blocks.pop(i); st.rerun()
            updated.append({"d":d,"r":int(reps),"rec":rec,"t":times})
    st.session_state.blocks=updated

    if st.button("➕ Añadir bloque"):
        st.session_state.blocks.append({"d":60.0,"r":1,"rec":5.0,"t":[0.0]}); st.rerun()

    total=sum(b["d"]*b["r"] for b in st.session_state.blocks)
    st.info(f"Volumen total: **{total:.0f} m** · sRPE: **{duration*rpe:.0f} UA**")

    if st.button("💾 Guardar entrenamiento",type="primary"):
        try:
            s=supabase.table("training_sessions").insert({
                "athlete_id":user.id,"session_date":str(day),
                "duration_minutes":int(duration),"rpe":float(rpe),"notes":notes or None
            }).execute().data[0]
            for order,b in enumerate(st.session_state.blocks,1):
                ss=supabase.table("sprint_sets").insert({
                    "session_id":s["id"],"set_order":order,"distance_m":float(b["d"]),
                    "repetitions":b["r"],"recovery_seconds":int(round(b["rec"]*60))
                }).execute().data[0]
                rows=[{"sprint_set_id":ss["id"],"rep_number":n,
                       "time_seconds":float(t) if t>0 else None}
                      for n,t in enumerate(b["t"],1)]
                supabase.table("sprint_reps").insert(rows).execute()
            st.success("Entrenamiento guardado.")
        except Exception as e:
            st.error(f"No se pudo guardar: {e}")

def wellness(user):
    back(); st.title("❤️ Wellness")
    with st.form("wellness_form"):
        day=st.date_input("Fecha",date.today())
        sleep=st.slider("Sueño",1,5,3)
        fatigue=st.slider("Fatiga",1,5,3)
        soreness=st.slider("Dolor muscular",1,5,3)
        stress=st.slider("Estrés",1,5,3)
        readiness=st.slider("Disposición para entrenar",1,5,3)
        notes=st.text_area("Comentarios")
        save=st.form_submit_button("Guardar wellness",use_container_width=True)
    if save:
        try:
            supabase.table("wellness_entries").upsert({
                "athlete_id":user.id,"entry_date":str(day),"sleep":sleep,
                "fatigue":fatigue,"muscle_soreness":soreness,"stress":stress,
                "readiness":readiness,"notes":notes or None
            }, on_conflict="athlete_id,entry_date").execute()
            st.success("Wellness guardado.")
        except Exception:
            st.error("Primero ejecuta db/002_add_wellness.sql en Supabase.")

def competition(user):
    back(); st.title("🏆 Competición")
    with st.form("comp"):
        day=st.date_input("Fecha",date.today())
        name=st.text_input("Competición")
        venue=st.text_input("Lugar")
        a,b=st.columns(2)
        event=a.selectbox("Prueba",["100m","200m","4x100","other"])
        rnd=b.selectbox("Ronda",["Serie","Semifinal","Final","Otra"])
        a,b=st.columns(2)
        result=a.number_input("Marca (s)",0.0,60.0,0.0,0.01,format="%.3f")
        wind=b.number_input("Viento (m/s)",-10.0,10.0,0.0,0.1,format="%.1f")
        lane=st.number_input("Calle",1,9,4)
        reaction=st.number_input("Reacción (s, opcional)",0.0,2.0,0.0,0.001,format="%.3f")
        position=st.number_input("Posición",1,99,1)
        notes=st.text_area("Comentarios")
        save=st.form_submit_button("Guardar competición")
    if save:
        if not name or result<=0:
            st.warning("Introduce nombre y marca.")
        else:
            supabase.table("competitions").insert({
                "athlete_id":user.id,"competition_date":str(day),"competition_name":name,
                "venue":venue or None,"event":event,"round":rnd,"lane":int(lane),
                "reaction_time":float(reaction) if reaction>0 else None,
                "result_seconds":float(result),"wind":float(wind),"position":int(position),
                "notes":notes or None
            }).execute()
            st.success("Competición guardada.")

def cycle(user,profile):
    back(); st.title("🌸 Ciclo menstrual")
    if profile.get("sex")!="female":
        st.info("Este módulo solo aparece para perfiles configurados como mujer."); return
    st.caption("Cada registro puede mantenerse privado o compartirse con el entrenador.")
    with st.form("cycle"):
        start=st.date_input("Inicio de la menstruación",date.today())
        ended=st.checkbox("Ya ha finalizado")
        end=st.date_input("Fin de la menstruación",date.today(),disabled=not ended)
        share=st.checkbox("Compartir este registro con mi entrenador",False)
        notes=st.text_area("Notas")
        save=st.form_submit_button("Guardar ciclo")
    if save:
        supabase.table("menstrual_cycles").insert({
            "athlete_id":user.id,"start_date":str(start),
            "end_date":str(end) if ended else None,
            "share_with_coach":share,"notes":notes or None
        }).execute()
        st.success("Registro guardado.")

def evolution(user):
    back(); st.title("📈 Mi evolución")
    sessions=supabase.table("training_sessions").select("session_date,rpe,srpe_load").eq("athlete_id",user.id).order("session_date").limit(60).execute().data
    comps=supabase.table("competitions").select("competition_date,event,result_seconds,wind,competition_name").eq("athlete_id",user.id).order("competition_date").limit(40).execute().data
    if sessions:
        df=pd.DataFrame(sessions)
        df["session_date"]=pd.to_datetime(df["session_date"])
        st.subheader("Carga interna")
        st.line_chart(df.set_index("session_date")[["srpe_load"]])
    else:
        st.info("Todavía no hay entrenamientos.")
    if comps:
        st.subheader("Competiciones")
        st.dataframe(pd.DataFrame(comps),use_container_width=True,hide_index=True)

def profile_page(user,profile):
    back(); st.title("👤 Mi perfil")
    opts=["100 m","200 m","100/200 m"]
    with st.form("profile"):
        name=st.text_input("Nombre y apellidos",profile.get("full_name") or "")
        sex=st.selectbox("Sexo",["male","female"],
            index=1 if profile.get("sex")=="female" else 0,
            format_func=lambda x:"Mujer" if x=="female" else "Hombre")
        current=profile.get("specialty") if profile.get("specialty") in opts else "100/200 m"
        spec=st.selectbox("Especialidad",opts,index=opts.index(current))
        save=st.form_submit_button("Guardar perfil")
    if save:
        supabase.table("profiles").update({
            "full_name":name,"sex":sex,"specialty":spec
        }).eq("id",user.id).execute()
        st.session_state.profile=get_profile(user.id)
        st.success("Perfil actualizado."); st.rerun()

def coach_home(user,profile):
    header(profile,"ENTRENADOR")
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="menu-card"><div class="menu-icon">👥</div><div class="menu-title">Mis atletas</div><div class="menu-sub">Consulta el grupo</div><div class="menu-num">1</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="menu-card"><div class="menu-icon">📊</div><div class="menu-title">Carga del grupo</div><div class="menu-sub">Sesiones y sRPE</div><div class="menu-num">2</div></div>',unsafe_allow_html=True)
    athletes=supabase.table("profiles").select("id,full_name,email,specialty").eq("coach_id",user.id).execute().data
    if not athletes:
        st.info("Todavía no tienes atletas asignados.")
    else:
        st.subheader("Mis atletas")
        for a in athletes:
            st.write(f"**{a.get('full_name') or a.get('email')}** · {a.get('specialty') or '100 / 200 m'}")
    st.divider()
    if st.button("Cerrar sesión"): sign_out()

user=login()
if "profile" not in st.session_state:
    st.session_state.profile=get_profile(user.id)
profile=st.session_state.profile

if profile.get("role")=="coach":
    coach_home(user,profile)
else:
    view=st.session_state.get("view","home")
    {
      "home": lambda: athlete_home(user,profile),
      "training": lambda: training(user),
      "wellness": lambda: wellness(user),
      "cycle": lambda: cycle(user,profile),
      "competition": lambda: competition(user),
      "evolution": lambda: evolution(user),
      "profile": lambda: profile_page(user,profile),
    }.get(view, lambda: athlete_home(user,profile))()
