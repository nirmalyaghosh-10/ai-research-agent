import os
import time
import random
import streamlit as st

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from tavily import TavilyClient
from google import genai
from google.genai import types

# Tried in order. If one is busy or out of quota, the next one is used automatically.
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-2.5-flash"]


def get_key(name):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)


TAVILY_KEY = get_key("TAVILY_API_KEY")
GEMINI_KEY = get_key("GEMINI_API_KEY")
if not TAVILY_KEY or not GEMINI_KEY:
    st.error("API keys missing. Put TAVILY_API_KEY and GEMINI_API_KEY in your .env file (local) or in Streamlit Cloud > Settings > Secrets.")
    st.stop()


@st.cache_resource
def get_tavily():
    return TavilyClient(api_key=TAVILY_KEY)


@st.cache_resource
def get_gemini():
    return genai.Client(api_key=GEMINI_KEY, http_options=types.HttpOptions(timeout=20000))


@st.cache_data(ttl=3600, show_spinner=False)
def search_web(q):
    res = get_tavily().search(query=q, max_results=5, search_depth="basic", timeout=15)
    return res.get("results", [])


def stream_ai(prompt, box, t0):
    errors = []
    for m in MODELS:
        if time.time() - t0 > 40:
            break
        text = ""
        try:
            cfg = types.GenerateContentConfig(max_output_tokens=2000, temperature=0.4)
            for ch in get_gemini().models.generate_content_stream(model=m, contents=prompt, config=cfg):
                if ch.text:
                    text += ch.text
                    box.markdown(text + " ▌")
            if text:
                box.markdown(text)
                return text, errors
        except Exception as e:
            errors.append("%s: %s" % (m, str(e)[:180]))
            if text:
                box.markdown(text)
                return text, errors
    return "", errors


# ---------- scenery ----------
def sc(cls, inner=""):
    return '<div class="sc ' + cls + '">' + inner + "</div>"


ROCKET = ('<svg viewBox="0 0 60 130" width="60" height="130"><defs><linearGradient id="rg" x1="0" x2="1"><stop offset="0" stop-color="#cbd5e1"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#94a3b8"/></linearGradient></defs>'
          '<path class="flame" d="M21 82 Q30 130 39 82Z" fill="#fb923c"/><path class="flame" d="M25 82 Q30 112 35 82Z" fill="#fde047"/>'
          '<path d="M30 2 Q50 25 46 82 L14 82 Q10 25 30 2Z" fill="url(#rg)"/><path d="M30 2 Q40 14 44 26 L16 26 Q20 14 30 2Z" fill="#ef4444"/>'
          '<circle cx="30" cy="42" r="8" fill="#38bdf8" stroke="#334155" stroke-width="3"/><path d="M14 60 L2 86 L16 78Z M46 60 L58 86 L44 78Z" fill="#ef4444"/></svg>')

ASTRO = ('<svg viewBox="0 0 80 100" width="80" height="100"><rect x="16" y="38" width="48" height="40" rx="16" fill="#cbd5e1"/><rect x="22" y="44" width="36" height="28" rx="10" fill="#f8fafc"/>'
         '<rect x="34" y="52" width="12" height="8" rx="2" fill="#38bdf8"/><rect x="2" y="42" width="22" height="10" rx="5" fill="#f1f5f9" transform="rotate(-30 12 47)"/>'
         '<rect x="56" y="42" width="22" height="10" rx="5" fill="#f1f5f9" transform="rotate(30 68 47)"/><rect x="22" y="74" width="12" height="22" rx="6" fill="#f1f5f9"/>'
         '<rect x="46" y="74" width="12" height="22" rx="6" fill="#f1f5f9"/><rect x="22" y="90" width="12" height="8" rx="4" fill="#f97316"/><rect x="46" y="90" width="12" height="8" rx="4" fill="#f97316"/>'
         '<circle cx="40" cy="26" r="20" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/><rect x="26" y="16" width="28" height="20" rx="10" fill="#1e293b"/><ellipse cx="34" cy="22" rx="6" ry="3" fill="#7dd3fc" opacity=".85"/></svg>')

SATURN = ('<svg viewBox="0 0 100 60" width="100" height="60"><defs><radialGradient id="sg" cx=".35" cy=".3"><stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#d97706"/></radialGradient></defs>'
          '<ellipse cx="50" cy="32" rx="46" ry="9" fill="none" stroke="#fcd34d" stroke-width="4" opacity=".7" transform="rotate(-18 50 32)"/>'
          '<circle cx="50" cy="30" r="17" fill="url(#sg)"/><path d="M8 44 Q50 52 92 20" fill="none" stroke="#fcd34d" stroke-width="4" transform="rotate(-18 50 32)" opacity=".9"/></svg>')

NETWORK = ('<svg viewBox="0 0 110 90" width="110" height="90"><g stroke="#67e8f9" stroke-width="1.5" opacity=".8"><line x1="15" y1="20" x2="55" y2="45"/><line x1="55" y1="45" x2="95" y2="15"/><line x1="55" y1="45" x2="30" y2="78"/><line x1="55" y1="45" x2="92" y2="72"/><line x1="15" y1="20" x2="95" y2="15"/></g>'
           '<g fill="#22d3ee"><circle class="np" cx="15" cy="20" r="6"/><circle class="np np2" cx="95" cy="15" r="6"/><circle class="np np3" cx="30" cy="78" r="6"/><circle class="np" cx="92" cy="72" r="6"/></g><circle class="np np2" cx="55" cy="45" r="9" fill="#f0abfc"/></svg>')

FOOTBALL = ('<svg viewBox="0 0 140 110" width="140" height="110"><ellipse cx="60" cy="106" rx="42" ry="4" fill="rgba(0,0,0,.28)"/>'
            '<line x1="46" y1="66" x2="42" y2="100" stroke="#f1c27d" stroke-width="8" stroke-linecap="round"/><rect x="34" y="97" width="17" height="8" rx="4" fill="#111827"/>'
            '<g class="kick"><line x1="52" y1="66" x2="54" y2="100" stroke="#f1c27d" stroke-width="8" stroke-linecap="round"/><rect x="48" y="97" width="19" height="8" rx="4" fill="#111827"/></g>'
            '<path d="M36 60 L64 60 L60 74 L40 74Z" fill="#f8fafc"/><path d="M38 32 Q50 26 62 32 L64 62 L36 62Z" fill="#ef4444"/>'
            '<line x1="40" y1="38" x2="26" y2="56" stroke="#f1c27d" stroke-width="6" stroke-linecap="round"/><line x1="60" y1="38" x2="76" y2="50" stroke="#f1c27d" stroke-width="6" stroke-linecap="round"/>'
            '<circle cx="50" cy="20" r="10" fill="#f1c27d"/><path d="M39 19 Q50 4 61 19 Q50 12 39 19Z" fill="#1f2937"/>'
            '<g class="ball"><circle cx="90" cy="98" r="8" fill="#fff" stroke="#111827" stroke-width="1.5"/><path d="M90 92 l5 3.5 -2 6 h-6 l-2 -6z" fill="#111827"/></g></svg>')

CRICKET = ('<svg viewBox="0 0 150 110" width="150" height="110"><ellipse cx="64" cy="106" rx="40" ry="4" fill="rgba(0,0,0,.28)"/>'
           '<g stroke="#fde68a" stroke-width="3"><line x1="14" y1="64" x2="14" y2="104"/><line x1="22" y1="64" x2="22" y2="104"/><line x1="30" y1="64" x2="30" y2="104"/></g>'
           '<line x1="52" y1="68" x2="46" y2="102" stroke="#f1f5f9" stroke-width="9" stroke-linecap="round"/><line x1="64" y1="68" x2="72" y2="102" stroke="#f1f5f9" stroke-width="9" stroke-linecap="round"/>'
           '<rect x="40" y="99" width="16" height="7" rx="3" fill="#fff"/><rect x="66" y="99" width="16" height="7" rx="3" fill="#fff"/>'
           '<path d="M46 34 Q58 28 70 34 L70 72 L46 72Z" fill="#2563eb"/><circle cx="58" cy="22" r="10" fill="#f1c27d"/><path d="M47 22 Q58 4 69 22Z" fill="#1e3a8a"/>'
           '<g class="bat"><line x1="66" y1="48" x2="72" y2="52" stroke="#f1c27d" stroke-width="6" stroke-linecap="round"/><rect x="68" y="48" width="8" height="46" rx="3" fill="#d6a05b"/></g>'
           '<g class="ball2"><circle cx="128" cy="40" r="5" fill="#dc2626"/></g></svg>')

HIGHJUMP = ('<svg viewBox="0 0 170 110" width="170" height="110"><rect x="104" y="94" width="64" height="12" rx="4" fill="#3b82f6"/>'
            '<line x1="118" y1="30" x2="118" y2="96" stroke="#e2e8f0" stroke-width="3"/><line x1="158" y1="30" x2="158" y2="96" stroke="#e2e8f0" stroke-width="3"/>'
            '<line x1="118" y1="58" x2="158" y2="58" stroke="#facc15" stroke-width="3"/>'
            '<g class="hj"><circle cx="22" cy="48" r="8" fill="#f1c27d"/><path d="M14 56 L30 56 L28 80 L16 80Z" fill="#a855f7"/>'
            '<line x1="18" y1="80" x2="14" y2="104" stroke="#f1c27d" stroke-width="6" stroke-linecap="round"/><line x1="26" y1="80" x2="32" y2="102" stroke="#f1c27d" stroke-width="6" stroke-linecap="round"/>'
            '<line x1="14" y1="60" x2="6" y2="74" stroke="#f1c27d" stroke-width="5" stroke-linecap="round"/><line x1="30" y1="60" x2="38" y2="48" stroke="#f1c27d" stroke-width="5" stroke-linecap="round"/></g></svg>')

LAPTOPMAN = ('<svg viewBox="0 0 140 110" width="140" height="110"><ellipse cx="70" cy="106" rx="56" ry="4" fill="rgba(0,0,0,.28)"/>'
             '<rect x="14" y="76" width="112" height="7" rx="2" fill="#92400e"/><rect x="20" y="83" width="5" height="22" fill="#78350f"/><rect x="115" y="83" width="5" height="22" fill="#78350f"/>'
             '<rect x="4" y="52" width="5" height="50" rx="2" fill="#475569"/><rect x="4" y="70" width="30" height="5" rx="2" fill="#475569"/>'
             '<rect x="26" y="46" width="18" height="30" rx="7" fill="#8b5cf6"/><g class="headbob"><circle cx="35" cy="34" r="9" fill="#f1c27d"/><path d="M26 33 Q35 20 44 33Z" fill="#111827"/></g>'
             '<line x1="40" y1="56" x2="74" y2="68" stroke="#f1c27d" stroke-width="5" stroke-linecap="round"/><line x1="36" y1="76" x2="56" y2="76" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>'
             '<line x1="56" y1="76" x2="56" y2="102" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/>'
             '<rect x="72" y="70" width="46" height="6" rx="2" fill="#94a3b8"/><path d="M86 38 L116 36 L118 70 L88 70Z" fill="#0f172a" stroke="#94a3b8" stroke-width="2"/>'
             '<g class="screen"><path d="M89 41 L113 40 L115 67 L91 67Z" fill="#0ea5e9"/><circle cx="100" cy="50" r="6" fill="none" stroke="#fff" stroke-width="2"/><line x1="104" y1="54" x2="109" y2="60" stroke="#fff" stroke-width="2"/>'
             '<line x1="93" y1="62" x2="111" y2="61" stroke="#e0f2fe" stroke-width="2"/></g></svg>')

SWIMMER = ('<svg viewBox="0 0 130 50" width="130" height="50"><g class="swim"><circle cx="48" cy="20" r="7" fill="#f1c27d"/><path d="M41 18 Q48 8 55 18Z" fill="#ef4444"/>'
           '<g class="arm"><line x1="52" y1="24" x2="76" y2="14" stroke="#f1c27d" stroke-width="5" stroke-linecap="round"/></g></g>'
           '<path d="M0 28 Q10 20 20 28 T40 28 T60 28 T80 28 T100 28 T120 28 L130 50 L0 50Z" fill="#0ea5e9" opacity=".85"/></svg>')

PALM = ('<svg viewBox="0 0 100 170" width="100" height="170"><g class="sway"><path d="M48 168 Q56 110 44 54" stroke="#8b5a2b" stroke-width="9" fill="none" stroke-linecap="round"/>'
        '<path d="M44 54 Q12 28 0 54 Q24 42 44 54Z" fill="#15803d"/><path d="M44 54 Q76 24 100 50 Q70 42 44 54Z" fill="#16a34a"/>'
        '<path d="M44 54 Q30 14 8 14 Q30 24 44 54Z" fill="#22c55e"/><path d="M44 54 Q62 10 88 16 Q64 26 44 54Z" fill="#15803d"/><path d="M44 54 Q44 22 52 6 Q50 28 44 54Z" fill="#4ade80"/>'
        '<circle cx="42" cy="58" r="4" fill="#78350f"/><circle cx="50" cy="60" r="4" fill="#78350f"/></g></svg>')

BOAT = ('<svg viewBox="0 0 80 70" width="80" height="70"><path d="M38 4 L38 48 L8 48Z" fill="#f8fafc"/><path d="M42 14 L42 48 L70 48Z" fill="#fbbf24"/><line x1="40" y1="2" x2="40" y2="54" stroke="#475569" stroke-width="2"/>'
        '<path d="M4 50 L76 50 L64 64 L16 64Z" fill="#b91c1c"/></svg>')

CRAB = ('<svg viewBox="0 0 44 26" width="44" height="26"><g stroke="#dc2626" stroke-width="2.5" stroke-linecap="round"><line x1="8" y1="16" x2="2" y2="24"/><line x1="12" y1="18" x2="8" y2="25"/><line x1="36" y1="16" x2="42" y2="24"/><line x1="32" y1="18" x2="36" y2="25"/></g>'
        '<circle cx="8" cy="8" r="6" fill="#ef4444"/><circle cx="36" cy="8" r="6" fill="#ef4444"/><ellipse cx="22" cy="16" rx="12" ry="8" fill="#ef4444"/><circle cx="18" cy="9" r="2" fill="#fff"/><circle cx="26" cy="9" r="2" fill="#fff"/></svg>')

rnd = random.Random(11)
STARS = "".join(
    '<i class="star" style="left:%d%%;top:%d%%;width:%dpx;height:%dpx;animation-delay:%.1fs"></i>'
    % (rnd.randint(0, 100), rnd.randint(0, 50), s, s, rnd.random() * 4)
    for s in [rnd.choice([2, 2, 3]) for _ in range(70)]
)
RAIN = "".join(
    '<i class="drop" style="left:%d%%;animation-duration:%.2fs;animation-delay:-%.2fs"></i>'
    % (rnd.randint(0, 100), 0.6 + rnd.random() * 0.5, rnd.random() * 2)
    for _ in range(45)
)
SNOW = "".join(
    '<i class="flake" style="left:%d%%;width:%dpx;height:%dpx;animation-duration:%.1fs;animation-delay:-%.1fs"></i>'
    % (rnd.randint(0, 100), s, s, 6 + rnd.random() * 6, rnd.random() * 8)
    for s in [rnd.choice([4, 5, 6]) for _ in range(45)]
)

SCENE = "".join([
    sc("sky s0"), sc("sky s1"), sc("sky s2"), sc("sky s3"), sc("sky s4"),
    sc("starwrap", STARS),
    sc("sun"), sc("moon"),
    sc("earth", '<div class="orbit"><span></span></div>'),
    sc("comet"),
    sc("cloud c1"), sc("cloud c2"), sc("cloud c3"),
    sc("pc saturn", SATURN), sc("pc network", NETWORK),
    sc("pc astro1", ASTRO), sc("pc astro2", ASTRO), sc("pc rocket", ROCKET),
    sc("mtn m1"), sc("mtn m2"), sc("mtn m3"), sc("river"),
    sc("sea"), sc("pc boat", BOAT), sc("sand"),
    sc("pc palm1", PALM), sc("pc palm2", PALM),
    sc("pc laptopman", LAPTOPMAN), sc("pc football", FOOTBALL), sc("pc highjump", HIGHJUMP),
    sc("pc cricket", CRICKET), sc("pc swimmer", SWIMMER), sc("pc crab", CRAB),
    sc("rainwrap", RAIN), sc("snowwrap", SNOW), sc("shade"),
])

CHIP = ('<div class="todchip"><span class="tod t0">🌅 Sunrise</span><span class="tod t1">🌤️ Morning</span>'
        '<span class="tod t2">☀️ Afternoon</span><span class="tod t3">🌇 Evening</span><span class="tod t4">🌙 Night</span></div>')

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, .stApp {font-family: 'Inter', sans-serif;}
.stApp {background: #2b1055;}

/* ---- scenery ---- */
.sc {position: fixed; z-index: -1; pointer-events: none;}
@keyframes phase {0%{opacity:0} 10%{opacity:1} 20%{opacity:1} 30%{opacity:0} 100%{opacity:0}}
.sky {inset: 0; opacity: 0; animation: phase 30s linear infinite;}
.s0 {background: linear-gradient(#2b1055,#7b3f98 35%,#f2709c 65%,#ffb36b); animation-delay: 0s;}
.s1 {background: linear-gradient(#4f9fe0,#8fd0ff 55%,#e0f4ff); animation-delay: 6s;}
.s2 {background: linear-gradient(#1673d9,#3fa0ee 55%,#a8dcff); animation-delay: 12s;}
.s3 {background: linear-gradient(#2c1a5c,#8e3b7a 40%,#ff6b4a 75%,#ffb347); animation-delay: 18s;}
.s4 {background: linear-gradient(#020617,#0b1240 55%,#1e1b4b); animation-delay: 24s;}

.todchip {position: fixed; z-index: 6; top: 12px; left: 14px;}
.tod {position: absolute; left: 0; top: 0; white-space: nowrap; padding: 6px 14px; border-radius: 999px; font-weight: 700; font-size: .85rem;
  color: #fff; background: rgba(8,10,30,.7); border: 1px solid rgba(255,255,255,.35); opacity: 0; animation: phase 30s linear infinite;}
.t1 {animation-delay: 6s;} .t2 {animation-delay: 12s;} .t3 {animation-delay: 18s;} .t4 {animation-delay: 24s;}

.starwrap {inset: 0; opacity: 0; animation: nightonly 30s linear infinite;}
@keyframes nightonly {0%{opacity:.9} 8%{opacity:.2} 12%{opacity:0} 66%{opacity:0} 80%{opacity:1} 100%{opacity:1}}
.star {position: absolute; background: #fff; border-radius: 50%; box-shadow: 0 0 8px 2px rgba(255,255,255,.8); animation: twinkle 3s ease-in-out infinite;}
@keyframes twinkle {0%,100%{opacity:.3; transform:scale(.8)} 50%{opacity:1; transform:scale(1.4)}}

.sun {width: 110px; height: 110px; border-radius: 50%; background: radial-gradient(circle,#fff9c4,#ffd54f 55%,#ff9800);
  box-shadow: 0 0 70px 28px rgba(255,190,70,.6); left: 6%; bottom: 20vh; opacity: 0; animation: sunarc 30s linear infinite;}
@keyframes sunarc {0%{left:6%;bottom:16vh;opacity:0} 4%{opacity:1} 20%{left:27%;bottom:50vh} 40%{left:48%;bottom:66vh} 60%{left:70%;bottom:50vh} 78%{left:92%;bottom:18vh;opacity:1} 81%{left:93%;bottom:12vh;opacity:0} 100%{opacity:0}}
.moon {width: 84px; height: 84px; border-radius: 50%; background: radial-gradient(circle at 35% 35%,#fff,#dbe4ff 60%,#a5b4fc);
  box-shadow: 0 0 55px 18px rgba(200,210,255,.5); left: 8%; bottom: 30vh; opacity: 0; animation: moonarc 30s linear infinite;}
@keyframes moonarc {0%{opacity:0} 78%{left:8%;bottom:26vh;opacity:0} 82%{left:12%;bottom:42vh;opacity:1} 91%{left:50%;bottom:64vh} 99%{left:88%;bottom:38vh;opacity:1} 100%{left:90%;bottom:30vh;opacity:0}}

.earth {left: 12%; top: 9%; width: 74px; height: 74px; border-radius: 50%;
  background: radial-gradient(circle at 30% 28%, rgba(255,255,255,.55), transparent 35%),
   radial-gradient(circle at 60% 55%, #22c55e 0 18%, transparent 19%), radial-gradient(circle at 28% 62%, #16a34a 0 14%, transparent 15%),
   radial-gradient(circle at 72% 28%, #4ade80 0 10%, transparent 11%), radial-gradient(circle,#38bdf8,#1d4ed8 80%);
  box-shadow: 0 0 22px 6px rgba(56,189,248,.5); animation: bob 6s ease-in-out infinite;}
.orbit {position: absolute; inset: -22px; border-radius: 50%; border: 1px dashed rgba(255,255,255,.4); animation: spin 9s linear infinite;}
.orbit span {position: absolute; top: -6px; left: calc(50% - 6px); width: 12px; height: 12px; border-radius: 50%; background: #e5e7eb; box-shadow: 0 0 8px #fff;}
@keyframes spin {to {transform: rotate(360deg);}}
@keyframes bob {0%,100%{transform: translateY(0)} 50%{transform: translateY(-12px)}}

.comet {top: 6%; left: -10%; width: 140px; height: 3px; border-radius: 3px; background: linear-gradient(90deg,transparent,#fff);
  box-shadow: 0 0 12px 3px rgba(255,255,255,.7); transform: rotate(22deg); opacity: 0; animation: comet 11s linear infinite;}
@keyframes comet {0%{left:-12%;top:4%;opacity:0} 4%{opacity:1} 20%{left:105%;top:34%;opacity:0} 100%{left:105%;opacity:0}}

.cloud {left: -260px; width: 190px; height: 48px; border-radius: 50px; background: rgba(255,255,255,.75); filter: blur(3px); animation: drift 70s linear infinite;}
.cloud::before, .cloud::after {content: ""; position: absolute; background: inherit; border-radius: 50%;}
.cloud::before {width: 76px; height: 76px; top: -34px; left: 28px;}
.cloud::after {width: 96px; height: 96px; top: -48px; left: 78px;}
.c1 {top: 12%;} .c2 {top: 26%; animation-duration: 95s; animation-delay: -45s;} .c3 {top: 38%; animation-duration: 80s; animation-delay: -62s;}
@keyframes drift {to {left: 112vw;}}

.mtn {left: 0; width: 100%;}
.m1 {bottom: 15vh; height: 25vh; clip-path: polygon(0 100%,0 55%,8% 35%,16% 60%,26% 15%,36% 55%,46% 30%,58% 62%,68% 10%,78% 50%,88% 28%,100% 58%,100% 100%);
  background: linear-gradient(#fff 0,#eef2ff 12%,#7c6fd6 26%,#3b2f86 100%);}
.m2 {bottom: 15vh; height: 18vh; clip-path: polygon(0 100%,0 62%,10% 40%,20% 66%,32% 34%,44% 68%,55% 42%,66% 70%,78% 38%,90% 66%,100% 48%,100% 100%);
  background: linear-gradient(#f1f5ff 0,#a99bea 10%,#34247a 28%,#1d1459 100%);}
.m3 {bottom: 13vh; height: 11vh; clip-path: polygon(0 100%,0 70%,12% 45%,24% 72%,38% 50%,52% 76%,66% 48%,80% 74%,92% 52%,100% 70%,100% 100%);
  background: linear-gradient(#2f7a5c,#0e2f33);}
.river {left: 45%; bottom: 12vh; width: 12vw; height: 15vh; clip-path: polygon(46% 0,54% 0,60% 35%,54% 60%,70% 100%,26% 100%,44% 60%,38% 35%);
  background: repeating-linear-gradient(180deg,#bae6fd 0 10px,#0ea5e9 10px 22px); background-size: 100% 44px; animation: flow 1.4s linear infinite;}
@keyframes flow {to {background-position: 0 44px;}}
.sea {left: 0; width: 100%; bottom: 5vh; height: 9vh;
  background: linear-gradient(rgba(14,116,144,.2),rgba(3,30,80,.7)), repeating-linear-gradient(100deg,#22d3ee 0 34px,#0284c7 34px 68px);
  background-size: 100% 100%, 136px 100%; animation: waves 4s linear infinite;}
@keyframes waves {to {background-position: 0 0, 136px 0;}}
.sand {left: 0; width: 100%; bottom: 0; height: 6vh; background: linear-gradient(#f6d58e,#d9a850);}

.shade {inset: 0; background: linear-gradient(transparent 20%, rgba(2,6,23,.6)); opacity: .5; animation: shade 30s linear infinite;}
@keyframes shade {0%{opacity:.5} 10%{opacity:.08} 20%{opacity:0} 56%{opacity:0} 70%{opacity:.25} 80%{opacity:.5} 100%{opacity:.55}}

/* rain + snow */
.rainwrap {inset: 0; opacity: 0; animation: rainvis 30s linear infinite;}
@keyframes rainvis {0%{opacity:0} 36%{opacity:0} 42%{opacity:.9} 56%{opacity:.9} 62%{opacity:0} 100%{opacity:0}}
.drop {position: absolute; top: -6vh; width: 2px; height: 18px; background: linear-gradient(transparent,#bfe3ff); animation: fall linear infinite;}
@keyframes fall {to {transform: translateY(110vh);}}
.snowwrap {inset: 0; animation: snowvis 30s linear infinite;}
@keyframes snowvis {0%{opacity:1} 14%{opacity:1} 18%{opacity:0} 80%{opacity:0} 85%{opacity:1} 100%{opacity:1}}
.flake {position: absolute; top: -4vh; background: #fff; border-radius: 50%; opacity: .85; animation: snowfall linear infinite;}
@keyframes snowfall {0%{transform: translate(0,0)} 50%{transform: translate(24px,55vh)} 100%{transform: translate(-10px,110vh)}}

/* characters */
.pc svg {display: block; width: 100%; height: auto;}
.astro1 {left: 3%; top: 24%; width: 76px; animation: floatup 8s ease-in-out infinite;}
@keyframes floatup {0%,100%{transform: translateY(0) rotate(-12deg)} 50%{transform: translateY(-46px) rotate(14deg)}}
.astro2 {right: 4%; top: 6%; width: 64px; animation: fallingastro 16s linear infinite;}
@keyframes fallingastro {0%{transform: translateY(-14vh) rotate(0)} 100%{transform: translateY(70vh) rotate(300deg)}}
.rocket {right: 14%; bottom: 14vh; width: 44px; animation: launch 11s ease-in infinite;}
@keyframes launch {0%,8%{transform: translateY(0) translateX(0)} 12%{transform: translateY(0) translateX(2px)} 16%{transform: translateY(0) translateX(-2px)} 100%{transform: translateY(-120vh) translateX(40px)}}
.flame {transform-origin: 30px 82px; animation: flick .2s ease-in-out infinite alternate;}
@keyframes flick {from{transform: scaleY(.8)} to{transform: scaleY(1.2)}}
.saturn {right: 30%; top: 5%; width: 88px; animation: bob 7s ease-in-out infinite;}
.network {left: 1.5%; top: 46%; width: 96px; opacity: .9;}
.np {animation: pulse 2s ease-in-out infinite; transform-box: fill-box; transform-origin: center;}
.np2 {animation-delay: .6s;} .np3 {animation-delay: 1.2s;}
@keyframes pulse {0%,100%{transform: scale(1)} 50%{transform: scale(1.5)}}

.palm1 {left: 0.5%; bottom: 3vh; width: 70px;} .palm2 {right: 0.5%; bottom: 3vh; width: 64px;}
.sway {transform-origin: 48px 168px; animation: sway 4s ease-in-out infinite;}
@keyframes sway {0%,100%{transform: rotate(-3deg)} 50%{transform: rotate(3deg)}}
.laptopman {left: 7%; bottom: 1vh; width: 120px;}
.headbob {animation: headbob 1.2s ease-in-out infinite;} @keyframes headbob {0%,100%{transform: translateY(0)} 50%{transform: translateY(2px)}}
.screen {animation: blink 1.6s ease-in-out infinite;} @keyframes blink {0%,100%{opacity:1} 50%{opacity:.6}}
.football {left: 22%; bottom: 1vh; width: 120px;}
.kick {transform-origin: 52px 66px; animation: kick 1.6s ease-in-out infinite;}
@keyframes kick {0%,100%{transform: rotate(-35deg)} 50%{transform: rotate(32deg)}}
.ball {animation: ball 1.6s ease-in-out infinite;} @keyframes ball {0%,100%{transform: translate(0,0)} 50%{transform: translate(26px,-30px)}}
.highjump {left: 36%; bottom: 1vh; width: 150px;}
.hj {transform-origin: 22px 70px; animation: hj 4.5s ease-in-out infinite;}
@keyframes hj {0%{transform: translate(0,0) rotate(0); opacity:1} 30%{transform: translate(40px,-8px) rotate(-18deg)} 55%{transform: translate(92px,-32px) rotate(-90deg)} 80%{transform: translate(120px,4px) rotate(-100deg)} 92%{opacity:1} 100%{transform: translate(120px,4px) rotate(-100deg); opacity:0}}
.cricket {right: 12%; bottom: 1vh; width: 130px;}
.bat {transform-origin: 68px 50px; animation: bat 2.4s ease-in-out infinite;}
@keyframes bat {0%,40%{transform: rotate(-50deg)} 50%{transform: rotate(40deg)} 100%{transform: rotate(-50deg)}}
.ball2 {animation: ball2 2.4s linear infinite;}
@keyframes ball2 {0%{transform: translate(0,0)} 45%{transform: translate(-52px,40px)} 52%{transform: translate(-60px,36px)} 100%{transform: translate(-130px,-70px)}}
.swimmer {left: 52%; bottom: 7vh; width: 120px; animation: swimx 18s ease-in-out infinite alternate;}
@keyframes swimx {from{transform: translateX(-120px)} to{transform: translateX(120px)}}
.swim {animation: bob 1.5s ease-in-out infinite;}
.arm {transform-origin: 52px 24px; animation: armrot 1.2s linear infinite;} @keyframes armrot {to{transform: rotate(360deg)}}
.boat {bottom: 9vh; left: -100px; width: 70px; animation: sail 42s linear infinite;}
@keyframes sail {to {left: 105vw;}}
.crab {right: 36%; bottom: 0.5vh; width: 40px; animation: scuttle 6s ease-in-out infinite alternate;}
@keyframes scuttle {from{transform: translateX(-40px)} to{transform: translateX(40px)}}
@media (max-width: 700px) {.pc {display: none;}}

/* ---- foreground ---- */
.block-container {position: relative; z-index: 2; padding-top: 3rem; padding-bottom: 34vh; max-width: 860px;}
header[data-testid="stHeader"] {background: transparent;}
footer {visibility: hidden;}
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown span {color: #fff;}
.stMarkdown a {color: #67e8f9 !important;}

.herobox {text-align: center; padding: 22px 18px 16px; border-radius: 24px; margin-bottom: 18px;
  background: linear-gradient(135deg, rgba(8,10,34,.82), rgba(40,12,80,.78)); border: 1px solid rgba(255,255,255,.25);
  backdrop-filter: blur(10px); box-shadow: 0 12px 40px rgba(0,0,0,.45);}
.hero {font-size: 3rem; font-weight: 800; margin: 0; letter-spacing: -1px; line-height: 1.1;
  background: linear-gradient(90deg,#67e8f9,#f0abfc,#fde68a,#67e8f9); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; animation: shine 6s linear infinite;}
@keyframes shine {to {background-position: 300% 0;}}
.tagline {font-size: 1.05rem; font-weight: 600; margin: 10px 0 14px; color: #f5e9ff !important;}
.badge {display: inline-block; margin: 4px; padding: 6px 16px; border-radius: 999px; font-weight: 700; font-size: .85rem; color: #0b1020 !important;}
.b1 {background: linear-gradient(90deg,#22d3ee,#38bdf8);} .b2 {background: linear-gradient(90deg,#f0abfc,#c084fc);} .b3 {background: linear-gradient(90deg,#fde68a,#fb923c);}
.pipeline {display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 10px;}
.step {padding: 7px 15px; border-radius: 10px; font-size: .9rem; font-weight: 700; color: #fff !important; box-shadow: 0 4px 14px rgba(0,0,0,.35);}
.p1 {background: linear-gradient(135deg,#0ea5e9,#2563eb);} .p2 {background: linear-gradient(135deg,#8b5cf6,#6d28d9);}
.p3 {background: linear-gradient(135deg,#ec4899,#be185d);} .p4 {background: linear-gradient(135deg,#f59e0b,#d97706);}
.arrow {color: #67e8f9 !important; font-weight: 800;}

.stTextInput input {border-radius: 16px; padding: 16px 18px; font-size: 1.05rem; background: #fff; color: #111 !important;
  border: 3px solid transparent; background-image: linear-gradient(#fff,#fff), linear-gradient(90deg,#22d3ee,#a855f7,#f43f5e,#facc15);
  background-origin: border-box; background-clip: padding-box, border-box; box-shadow: 0 0 18px rgba(34,211,238,.55); transition: all .25s;}
.stTextInput input:focus {box-shadow: 0 0 30px rgba(244,63,94,.7), 0 0 60px rgba(168,85,247,.45); transform: scale(1.01);}
.stButton button {background: linear-gradient(90deg,#00c6ff,#7b2ff7,#f107a3); color: #fff !important; border: none; border-radius: 14px;
  padding: 12px 40px; font-weight: 800; font-size: 1.1rem; transition: all .25s; box-shadow: 0 6px 22px rgba(123,47,247,.55);}
.stButton button:hover {transform: translateY(-3px) scale(1.04); box-shadow: 0 10px 34px rgba(241,7,163,.7);}

[data-testid="stVerticalBlockBorderWrapper"] {background: rgba(10,14,40,.94); border: 1px solid rgba(103,232,249,.55) !important; border-radius: 18px; padding: 8px 10px;
  box-shadow: 0 10px 36px rgba(0,0,0,.5);}
[data-testid="stExpander"] details {background: rgba(10,14,40,.96); border: 1px solid #67e8f9 !important; border-radius: 14px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {color: #fff !important; font-weight: 700;}
[data-testid="stExpander"] * {color: #f1f5f9;}
[data-testid="stExpander"] a {color: #67e8f9 !important;}
[data-testid="stSpinner"] {background: rgba(10,14,40,.94); padding: 10px 16px; border-radius: 12px; border: 1px solid #67e8f9;}
[data-testid="stSpinner"] * {color: #fff !important;}
[data-testid="stAlert"] {background: rgba(10,14,40,.95); border: 1px solid #fbbf24; border-radius: 14px;}
[data-testid="stAlert"] * {color: #fff !important;}

.stats {display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin: 14px 0 6px;}
.stat {padding: 7px 18px; border-radius: 10px; font-weight: 700; color: #0b1020 !important;}
.st1 {background: #67e8f9;} .st2 {background: #f0abfc;} .st3 {background: #fde68a;}
.done {text-align: center; margin: 10px 0 14px; padding: 12px 18px; border-radius: 14px; font-weight: 800; color: #1a1033 !important; background: linear-gradient(90deg,#facc15,#86efac,#67e8f9);}
.footer {text-align: center; margin-top: 30px; font-size: .85rem; font-weight: 700; color: #fff !important;}

/* flash on click */
.flash {position: fixed; inset: 0; z-index: 9999; pointer-events: none; opacity: 0; background: radial-gradient(circle at 50% 40%,#fff,#a5f3fc 40%,rgba(168,85,247,.4) 75%);
  animation: flash 2.4s ease-out forwards;}
@keyframes flash {0%{opacity:0} 6%{opacity:.95} 14%{opacity:.25} 22%{opacity:.85} 45%{opacity:0} 100%{opacity:0}}
.bolt {position: fixed; z-index: 10000; left: calc(50% - 60px); top: 20vh; width: 120px; pointer-events: none; opacity: 0; animation: boltanim 2.4s ease-out forwards; filter: drop-shadow(0 0 20px #facc15);}
@keyframes boltanim {0%{opacity:0; transform: scale(.4)} 8%{opacity:1; transform: scale(1.2)} 40%{opacity:1} 55%{opacity:0; transform: scale(1)} 100%{opacity:0}}
</style>
"""

FLASH = ('<div class="flash"></div><svg class="bolt" viewBox="0 0 60 100"><path d="M36 0 L6 56 H28 L20 100 L56 38 H34Z" fill="#fde047" stroke="#f59e0b" stroke-width="3"/></svg>')

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(SCENE + CHIP, unsafe_allow_html=True)

st.markdown(
    '<div class="herobox"><h1 class="hero">🔎 AI Research Agent 🚀</h1>'
    '<p class="tagline">✨ Search the web. Read the sources. Get a clear answer in seconds. ✨</p>'
    '<span class="badge b1">⚡ Tavily Search</span><span class="badge b2">🧠 Gemini AI</span><span class="badge b3">🎈 Streamlit</span>'
    '<div class="pipeline"><span class="step p1">❓ Question</span><span class="arrow">➜</span><span class="step p2">🌐 Web Search</span>'
    '<span class="arrow">➜</span><span class="step p3">🤖 AI Analysis</span><span class="arrow">➜</span><span class="step p4">📄 Report</span></div></div>',
    unsafe_allow_html=True,
)

query = st.text_input("Research topic", placeholder="💡 Ask anything, e.g. Latest trends in renewable energy", label_visibility="collapsed")
go = st.button("🚀 Research 🔎")

if go:
    if not query.strip():
        st.warning("⚠️ Please type a topic first.")
    else:
        st.markdown(FLASH, unsafe_allow_html=True)
        t0 = time.time()
        results = []
        with st.spinner("🔎 Searching the web..."):
            try:
                results = search_web(query.strip())
            except Exception as e:
                st.error("Search failed: %s" % str(e)[:300])

        if results:
            sources = "\n\n".join(
                "[%d] %s\n%s" % (i + 1, r.get("title", ""), (r.get("content") or "")[:600])
                for i, r in enumerate(results)
            )
            prompt = (
                "You are a research assistant. Using only the sources below, answer the question clearly in under 250 words. "
                "Use short headings and bullet points, and cite sources like [1].\n\n"
                "Question: %s\n\nSources:\n%s" % (query.strip(), sources)
            )
            text, errors = "", []
            with st.container(border=True):
                box = st.empty()
                with st.spinner("🤖 Gemini is writing your report..."):
                    text, errors = stream_ai(prompt, box, t0)

            secs = time.time() - t0
            if text:
                st.markdown(
                    '<div class="stats"><span class="stat st1">📚 %d sources</span><span class="stat st2">📝 %d words</span>'
                    '<span class="stat st3">⏱️ %.1f seconds</span></div><div class="done">✅ Research complete</div>'
                    % (len(results), len(text.split()), secs),
                    unsafe_allow_html=True,
                )
            else:
                st.error("The AI could not answer. Details: " + " | ".join(errors) if errors else "The AI returned an empty answer.")
                st.info("Common causes: invalid or expired Gemini key, free quota used up (429), or the key has no access to the model. The sources below are still valid.")

            with st.expander("📚 Sources", expanded=not text):
                for i, r in enumerate(results):
                    st.markdown("**[%d]** [%s](%s)" % (i + 1, r.get("title", "Source"), r.get("url", "")))
                    if not text:
                        st.caption((r.get("content") or "")[:220])

