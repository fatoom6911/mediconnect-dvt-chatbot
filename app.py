"""MediConnect — fictional-patient educational prototype. Not for clinical use."""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="MediConnect | Healthcare Assistant", page_icon="💙", layout="wide", initial_sidebar_state="expanded")

NAV = ["Welcome", "Patient Education", "AI-style Chat", "Fictional DVT Case", "Healthcare Professional", "Safety & Privacy"]
if "page" not in st.session_state:
    st.session_state.page = "Welcome"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "consent" not in st.session_state:
    st.session_state.consent = False
if "language" not in st.session_state:
    st.session_state.language = "English"

# Styling inspired by Hessa's teal mobile interface; uses native Streamlit widgets for real navigation.
st.markdown("""
<style>
:root {color-scheme: light;}
html, body, [data-testid="stApp"], .stApp {background:#f5f9fa; color:#153e49;}
[data-testid="stHeader"] {background:#f5f9fa !important; border-bottom:1px solid #e2edef;}
[data-testid="stToolbar"] {background:transparent !important;}
[data-testid="stSidebar"] {background:linear-gradient(175deg,#093946,#126474) !important;}
[data-testid="stSidebar"] * {color:#fff !important;}
[data-testid="stSidebar"] button {border:1px solid #5c929a !important; background:#ffffff15 !important;}
[data-testid="stSidebar"] button:hover {background:#ffffff2c !important;}
.block-container {max-width:1120px; padding-top:2.0rem; padding-bottom:3rem;}
h1,h2,h3,p,label {color:#153e49;}
.hero {background:linear-gradient(125deg,#083d4b,#126f79); border-radius:27px; padding:48px 46px; color:white; margin-bottom:25px; box-shadow:0 14px 30px #093e4b18;}
.hero * {color:white !important;}
.hero .eyebrow {font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:800; opacity:.83;}
.hero h1 {font-size:clamp(35px,4.5vw,62px); line-height:1.08; margin:20px 0 18px; letter-spacing:-2px; font-weight:800;}
.hero p {font-size:17px; max-width:600px; line-height:1.7;}
.tile {background:white; border:1px solid #dbe9eb; border-radius:21px; padding:24px; min-height:160px; box-shadow:0 6px 20px #173d4810; margin-bottom:12px;}
.tile h3 {font-size:21px; margin:4px 0 13px;}
.tile p {color:#56747b; font-size:15px; line-height:1.6;}
.kicker {text-transform:uppercase; letter-spacing:1.5px; color:#4a8590; font-weight:800; font-size:12px; margin:14px 0;}
[data-testid="stButton"] button[kind="primary"], [data-testid="stFormSubmitButton"] button {background:#116675; color:white; border:0; border-radius:12px; min-height:46px; font-weight:700;}
[data-testid="stButton"] button {border-radius:12px; min-height:44px;}
[data-testid="stChatMessage"] {background:white; border:1px solid #dce9eb; border-radius:16px; padding:13px; margin:10px 0;}
[data-testid="stChatInput"] {border-radius:16px;}
[data-testid="stAlert"] {border-radius:13px;}
hr {border-color:#d9e7e9;}
.smallnote {font-size:13px;color:#607e86;line-height:1.7;}
@media(max-width:700px){.hero{padding:28px 23px;}.hero h1{letter-spacing:-1px;}.block-container{padding-top:1rem;}}
</style>
""", unsafe_allow_html=True)

BANK = [{'number': 1,
  'question': 'What is the clot in my leg?',
  'answer': 'It is a clot in the left popliteal deep vein behind your knee, confirmed on your '
            'ultrasound.',
  'category': 'education'},
 {'number': 2,
  'question': 'Does a blood thinner dissolve it immediately?',
  'answer': 'Apixaban reduces further clotting. Your body may gradually clear the clot; recovery '
            'is not immediate.',
  'category': 'education'},
 {'number': 3,
  'question': 'Did my flight definitely cause this?',
  'answer': 'Long sitting and obesity may contribute, but your history cannot prove one cause.',
  'category': 'education'},
 {'number': 4,
  'question': 'What is the name of my medicine?',
  'answer': 'It is apixaban, sold as Eliquis. It is an oral anticoagulant that blocks clotting '
            'factor Xa.',
  'category': 'education'},
 {'number': 5,
  'question': 'How many tablets do I take during the first week?',
  'answer': 'Your prescription uses 5 mg tablets: take two per dose, twice daily for seven days. '
            'Check that your pack really contains 5 mg tablets.',
  'category': 'education'},
 {'number': 6,
  'question': 'What changes on day 8?',
  'answer': 'Take one 5 mg tablet per dose, twice daily, according to your written switch date. If '
            'the date is unclear, ask the pharmacist before changing it.',
  'category': 'education'},
 {'number': 7,
  'question': 'Do I take it with breakfast?',
  'answer': 'You may take apixaban with or without food. Keep to the twice-daily schedule your '
            'team gave you.',
  'category': 'education'},
 {'number': 8,
  'question': 'I forgot one dose today and know which one it was. What does the leaflet say?',
  'answer': 'Take the missed dose as soon as possible on the same day and resume twice-daily '
            'dosing. Never double a dose to make up for one. If timing is unclear, ask your '
            'pharmacist.',
  'category': 'education'},
 {'number': 9,
  'question': 'If the swelling settles, can I stop early?',
  'answer': 'Feeling better does not mean treatment is complete. Keep to your prescription and '
            'speak with your clinician before any change. Stopping early can increase clot risk.',
  'category': 'education'},
 {'number': 10,
  'question': 'Why do I have a review at three months?',
  'answer': 'That is when your clinician reviews whether you should continue treatment. It is not '
            'an automatic stop date.',
  'category': 'education'},
 {'number': 11,
  'question': 'What side effect should I know about?',
  'answer': 'Bleeding is the main concern. New unusual bleeding needs clinical advice; severe '
            'bleeding needs emergency help.',
  'category': 'education'},
 {'number': 12,
  'question': 'Should I tell my dentist?',
  'answer': 'Yes. Tell every clinician and dentist that you take apixaban, and carry your medicine '
            'list. Do not stop it for a procedure unless the responsible clinician gives a plan.',
  'category': 'education'},
 {'number': 13,
  'question': 'How should I store these tablets?',
  'answer': 'Keep them at room temperature, 20–25°C, in a safe place out of children’s reach. '
            'Follow the storage directions on your dispensed pack.',
  'category': 'education'},
 {'number': 14,
  'question': 'Can I give spare tablets to my husband?',
  'answer': 'No. Apixaban is prescribed for your own condition and can cause serious bleeding. He '
            'needs his own clinical advice.',
  'category': 'education'},
 {'number': 15,
  'question': 'What is the difference between DVT and PE?',
  'answer': 'DVT is a deep-vein clot. PE is a clot in a lung blood vessel and can be '
            'life-threatening.',
  'category': 'education'},
 {'number': 16,
  'question': 'What does twice daily mean in my discharge plan?',
  'answer': 'It means two separate doses each day, using the times written by your team. Do not '
            'take the whole day’s tablets together.',
  'category': 'education'},
 {'number': 17,
  'question': 'Why is my nose operation postponed?',
  'answer': 'Your recent DVT makes interrupting treatment risky. The plan is to wait at least '
            'three months after diagnosis and then reassess with your surgical team.',
  'category': 'education'},
 {'number': 18,
  'question': 'Will the chatbot change my dose if I send a blood result?',
  'answer': 'No. Your clinical team must interpret results and decide treatment changes. I can '
            'explain the written plan and help identify when you need medical attention.',
  'category': 'education'},
 {'number': 19,
  'question': 'My leg is more swollen today. Should I wait for next week?',
  'answer': 'Contact your team for assessment today; in hospital, tell the nurse now. New '
            'breathlessness, chest pain or fainting means emergency help immediately.',
  'category': 'review'},
 {'number': 20,
  'question': 'My other calf has started hurting and swelling. Is it another clot?',
  'answer': 'Arrange assessment today. An online conversation cannot diagnose or exclude another '
            'DVT. Escalate immediately if PE symptoms appear.',
  'category': 'review'},
 {'number': 21,
  'question': 'My gums bleed a little when brushing, but it stops. Is that okay?',
  'answer': 'Report new bleeding to your team today, even if it stopped. If bleeding becomes heavy '
            'or will not stop, seek emergency help.',
  'category': 'review'},
 {'number': 22,
  'question': 'I keep getting short nosebleeds that stop. Should I skip a tablet?',
  'answer': 'Speak to your team today; do not decide to skip doses yourself. Persistent or heavy '
            'bleeding, weakness or faintness needs immediate assessment.',
  'category': 'review'},
 {'number': 23,
  'question': 'My period is heavier than usual but I feel well. What should I do?',
  'answer': 'Contact your team today and describe the amount and duration. Rapid heavy bleeding, '
            'dizziness, fainting or marked weakness requires emergency help.',
  'category': 'review'},
 {'number': 24,
  'question': 'There is a pink tinge in my urine. Can it wait?',
  'answer': 'Get medical advice today, even without pain. Heavy blood loss, clots preventing '
            'urination, faintness or severe pain requires immediate assessment.',
  'category': 'review'},
 {'number': 25,
  'question': 'A large bruise appeared without an injury. Is this normal?',
  'answer': 'Report it today, especially if enlarging. Rapid expansion, severe pain, weakness or '
            'fainting requires immediate assessment.',
  'category': 'review'},
 {'number': 26,
  'question': 'Can I take ibuprofen, naproxen or aspirin for pain?',
  'answer': 'Check with your pharmacist or prescriber before taking them. They can increase '
            'bleeding risk with apixaban. Ask for an appropriate pain plan.',
  'category': 'review'},
 {'number': 27,
  'question': 'Another doctor prescribed an antibiotic. Can I start it?',
  'answer': 'Have the pharmacist check its exact name, dose and your medicines before the first '
            'dose; if treatment is urgent, contact the prescribing service promptly.',
  'category': 'review'},
 {'number': 28,
  'question': 'Can I use St John’s wort or a herbal supplement?',
  'answer': 'Ask a pharmacist before use. St John’s wort can reduce apixaban exposure and should '
            'be avoided with it; other products need individual review.',
  'category': 'review'},
 {'number': 29,
  'question': 'I accidentally took an extra dose. What now?',
  'answer': 'Contact your prescriber or urgent medical advice service now, even if you feel well. '
            'Tell them the strength, amount and time. Any major bleeding or collapse requires '
            'emergency help.',
  'category': 'review'},
 {'number': 30,
  'question': 'I missed yesterday’s doses and cannot remember today’s. Should I catch up?',
  'answer': 'Do not take extra tablets to catch up. Contact your pharmacist or prescriber now to '
            'establish a safe schedule.',
  'category': 'review'},
 {'number': 31,
  'question': 'I vomited after my tablet. Should I take another?',
  'answer': 'Contact your pharmacist or clinician now for advice based on timing and whether the '
            'tablet was retained. Do not automatically repeat it. Blood in vomit requires '
            'emergency help.',
  'category': 'review'},
 {'number': 32,
  'question': 'I am running out of tablets tonight. Can I take half doses?',
  'answer': 'Contact your pharmacy or prescribing service now to arrange supply. Do not ration or '
            'halve the prescribed dose yourself.',
  'category': 'review'},
 {'number': 33,
  'question': 'I might be pregnant. Should I stop apixaban?',
  'answer': 'Contact your prescribing team today for a safe treatment plan. Do not leave a DVT '
            'untreated by stopping on your own. Tell them if you are breastfeeding or planning to '
            'do so.',
  'category': 'review'},
 {'number': 34,
  'question': 'Can I have a dental extraction or reschedule septoplasty now?',
  'answer': 'Ask the procedural clinician and anticoagulation prescriber to agree a plan before '
            'booking or changing tablets. Your postponed septoplasty still needs reassessment '
            'after the minimum delay.',
  'category': 'review'},
 {'number': 35,
  'question': 'Can I fly next week or begin strenuous exercise?',
  'answer': 'Discuss the timing and activity with your treating team before making plans. Your '
            'recent DVT, symptoms, medication and injury risk need individual consideration.',
  'category': 'review'},
 {'number': 36,
  'question': 'My father had a clot. Do I need genetic tests or lifelong tablets?',
  'answer': 'Tell your clinician about his postoperative clot. It does not establish an inherited '
            'disorder in you. Testing and treatment duration need a clinical review.',
  'category': 'review'},
 {'number': 37,
  'question': 'I suddenly cannot catch my breath. Could this be anxiety?',
  'answer': 'This could be a serious emergency. In hospital, alert staff now. At home, call 998 in '
            'the UAE or your local ambulance number. Do not drive yourself.',
  'category': 'urgent'},
 {'number': 38,
  'question': 'My chest hurts sharply when I breathe. Can I wait?',
  'answer': 'Get emergency help now: alert hospital staff immediately, or call an ambulance at '
            'home. Do not wait to see whether it passes.',
  'category': 'urgent'},
 {'number': 39,
  'question': 'I coughed up blood, even though I took my tablets. What should I do?',
  'answer': 'Seek emergency assessment now. Alert staff in hospital or call an ambulance at home. '
            'Taking apixaban does not make this safe to ignore.',
  'category': 'urgent'},
 {'number': 40,
  'question': 'I fainted and now my heart is racing and I feel breathless. Is that a side effect?',
  'answer': 'Call for emergency help now. In hospital, use the call bell or alert staff; at home, '
            'call an ambulance and do not drive.',
  'category': 'urgent'},
 {'number': 41,
  'question': 'My cut is bleeding heavily and pressure is not stopping it. What now?',
  'answer': 'Keep firm direct pressure with a clean cloth while help is arranged. Alert staff '
            'immediately or call an ambulance at home. Tell responders you take apixaban.',
  'category': 'urgent'},
 {'number': 42,
  'question': 'I vomited blood or material like coffee grounds. Can I take an antacid?',
  'answer': 'Get emergency help now. Alert hospital staff or call an ambulance at home. Do not '
            'delay for a home remedy; the emergency team must direct treatment and further dosing.',
  'category': 'urgent'},
 {'number': 43,
  'question': 'My stool is black and sticky like tar. Is that from the medicine?',
  'answer': 'Seek immediate emergency assessment. In hospital, tell staff now; at home, call an '
            'ambulance, especially with weakness or dizziness. Do not dismiss this as an expected '
            'effect.',
  'category': 'urgent'},
 {'number': 44,
  'question': 'I suddenly have an extremely severe headache and feel confused. Should I rest?',
  'answer': 'Get emergency help immediately. Alert staff or call an ambulance at home; do not '
            'drive or wait for a routine appointment.',
  'category': 'urgent'},
 {'number': 45,
  'question': 'My face is drooping and I cannot speak clearly. What should I do?',
  'answer': 'Alert staff immediately or call an ambulance now. If possible, note when symptoms '
            'began without delaying help. Do not take extra apixaban or aspirin.',
  'category': 'urgent'},
 {'number': 46,
  'question': 'I fell and hit my head but feel fine. Can I stay home?',
  'answer': 'You need immediate medical assessment because you take apixaban. Tell staff now if in '
            'hospital. At home, arrange immediate emergency assessment; call an ambulance for '
            'significant injury, symptoms or unsafe transport. Do not drive yourself.',
  'category': 'urgent'},
 {'number': 47,
  'question': 'My period is suddenly very heavy and I feel faint. Should I just call tomorrow?',
  'answer': 'Get emergency help now. Alert hospital staff or call an ambulance at home. Do not '
            'wait until tomorrow; tell responders about the bleeding and last apixaban dose.',
  'category': 'urgent'},
 {'number': 48,
  'question': 'My lips and tongue are swelling and breathing is difficult. What should I do?',
  'answer': 'Alert hospital staff immediately or call an ambulance at home. This may be a severe '
            'allergic reaction and needs emergency treatment now.',
  'category': 'urgent'}]

# Deliberately limited approved-style educational material; no open-ended model or clinical decisions.
TOPICS = {
    "DVT": ("Deep vein thrombosis (DVT)", "DVT is a blood clot that forms in a deep vein, commonly in a leg. Symptoms can include swelling, pain, warmth or tenderness. A healthcare professional must assess possible symptoms; a chatbot cannot diagnose a clot."),
    "PE": ("Pulmonary embolism (PE)", "PE occurs when a blood clot blocks a blood vessel in the lungs. Sudden breathlessness, chest pain, coughing blood or collapse requires emergency help immediately."),
    "Anticoagulants": ("Anticoagulant medicines", "Anticoagulants reduce the blood's ability to clot. They can help prevent existing clots growing and new clots forming. Bleeding is an important risk. Only your prescriber can determine which medicine or dose is right for you."),
    "Blood pressure": ("Blood pressure", "Blood pressure measures the force of blood against artery walls. Measurements are interpreted in context by healthcare professionals. This prototype cannot interpret your personal readings."),
    "Diabetes": ("Diabetes", "Diabetes is a condition involving elevated blood glucose. Management varies and may involve food choices, activity, monitoring and prescribed medicines. Ask your care team for individual advice."),
    "Asthma": ("Asthma", "Asthma is a long-term condition that can cause airway inflammation and episodes of wheezing, coughing or breathlessness. Treatment plans are individual. Severe breathing difficulty requires emergency help."),
    "Cholesterol": ("Cholesterol", "Cholesterol is a fatty substance in blood. Some forms of high cholesterol increase cardiovascular risk. A clinician can discuss testing and management appropriate to the person."),
    "Infection": ("Infections", "Infections can be caused by bacteria, viruses or other organisms. Symptoms and treatments vary widely. New, severe or worsening symptoms need assessment by a healthcare professional."),
    "Ultrasound": ("Ultrasound", "Ultrasound uses sound waves to create images inside the body. Compression ultrasound is commonly used when clinicians investigate suspected DVT. Only a clinician should interpret individual findings."),
    "Medication safety": ("Medication safety", "Use medicines only as prescribed, check the label, and ask a pharmacist about interactions or uncertainty. Never change a dose based on this demo chatbot."),
}

URGENT_PATTERNS = [
    r"chest pain|chest hurts|pain in (my |the )?chest|heart attack", r"can't breathe|cannot breathe|can.t catch my breath|difficulty breathing|shortness of breath|breathless|struggling to breathe",
    r"cough(?:ing|ed)? up blood|blood in (my )?cough", r"faint(?:ed|ing)?|passed out|unconscious|loss of consciousness|collapse(?:d)?",
    r"face (?:is )?droop|slurred speech|cannot speak|can't speak|one.side weakness|stroke symptoms",
    r"severe bleeding|bleeding heavily|heavy bleeding|won.t stop bleeding|vomit(?:ed|ing)? blood|coffee.ground|black (?:tarry|sticky) stool",
    r"seizure|convulsion", r"lips? (?:and tongue )?(?:are )?swelling|tongue (?:is )?swelling|severe allergic",
    r"suicid|kill myself|hurt myself|self.harm", r"hit my head|head injury|fell and hit", r"sudden severe headache|worst headache",
    r"ألم الصدر|وجع الصدر|ضيق التنفس|صعوبة التنفس|نزيف شديد|فقدان الوعي|جلطة دماغية|انتحار|اختناق|سعال.*دم"
]
REVIEW_PATTERNS = [
    r"my (?:leg|calf) (?:is |has )?(?:more )?swoll|new swelling|worsening|getting worse|new symptom|severe pain",
    r"nosebleed|bleeding gums|blood in (?:my )?urine|heavy period|large bruise|unexpected bleeding",
    r"missed (?:my |a )?dose|extra dose|overdose|change (?:my |the )?dose|stop (?:my |the )?(?:medicine|medication|tablet)|should i take|can i take|what dose|how many tablets",
    r"my test result|my blood result|interpret my|diagnos|do i have|is this normal|am i safe|should i wait",
    r"pregnan|breastfeed|surgery|operation|dental extraction|side effect|interaction|ibuprofen|aspirin|naproxen|antibiotic",
    r"talk to (?:a |the )?(?:doctor|nurse)|speak to (?:a |the )?(?:doctor|nurse|person)|real person|human help|unclear|confus|not helpful",
    r"عندي ألم|دوائي|جرعة|تشخيص|نتيجة التحليل|أريد طبيب|أريد ممرضة"
]

# Known generic educational prompts bypass over-conservative symptom words only when phrased exactly as an educational request.
GENERIC = {
    "what is dvt": "DVT",
    "what is deep vein thrombosis": "DVT",
    "what is pe": "PE",
    "what is pulmonary embolism": "PE",
    "what are anticoagulants": "Anticoagulants",
    "what is a blood thinner": "Anticoagulants",
    "what is blood pressure": "Blood pressure",
    "what is diabetes": "Diabetes",
    "what is asthma": "Asthma",
    "what is cholesterol": "Cholesterol",
    "what is an infection": "Infection",
    "what is an ultrasound": "Ultrasound",
    "what is medication safety": "Medication safety",
    "ما هي الجلطة الوريدية العميقة": "DVT",
    "ما هو السكري": "Diabetes",
    "ما هو ضغط الدم": "Blood pressure",
}

def normalize(s):
    return re.sub(r"[^\w\s\u0600-\u06ff]", " ", s.casefold()).strip()

def route(text):
    """Conservative demo routing. NOT a validated symptom/urgency detector."""
    q = normalize(text)
    if not q:
        return "unknown", "Please type a general educational question."
    if q in GENERIC:
        topic = GENERIC[q]
        return "education", TOPICS[topic][1]
    for pat in URGENT_PATTERNS:
        if re.search(pat, text.casefold()):
            return "urgent", "This may need immediate medical attention. In hospital, press your nurse-call button or alert staff now. Outside hospital, call your local emergency number (998 for ambulance in the UAE). Do not drive yourself or wait for this chatbot. No alert has been sent."
    # Exact matches to Saeed's 48 fictional prompts, for safe and reproducible demonstrations.
    for item in BANK:
        if normalize(item["question"]) == q:
            if item["category"] == "urgent":
                return "urgent", "This may be an emergency. In hospital, alert staff immediately. At home, call an ambulance (998 in the UAE). Do not drive yourself. No alert has been sent."
            if item["category"] == "review":
                return "review", "This question needs a healthcare professional. Please contact your care team. This prototype has not sent a message."
            if item["number"] in (5,6,8,16):
                return "review", "Medication timing and doses must come from your verified prescription and pharmacist. This demo cannot determine your personal dose."
            return "education", "**Fictional case education (not personal advice):** " + item["answer"]
    for pat in REVIEW_PATTERNS:
        if re.search(pat, text.casefold()):
            return "review", "This question needs a healthcare professional. Please contact your care team. This prototype has not sent a message. For severe or rapidly worsening symptoms, seek urgent help immediately."
    # Simple concept retrieval: informational definitions only, never personalised assessment.
    for topic, (name, description) in TOPICS.items():
        aliases = {topic.casefold(), name.casefold()}
        if topic == "DVT": aliases |= {"dvt", "deep vein thrombosis", "blood clot"}
        if topic == "PE": aliases |= {"pulmonary embolism"}
        if topic == "Anticoagulants": aliases |= {"blood thinner", "blood thinners", "apixaban", "anticoagulant"}
        if any(a in text.casefold() for a in aliases):
            return "education", description
    # Never pretend to answer every medical topic; unknown requests get a clear boundary.
    return "unknown", "I don't have reviewed educational information for that topic yet. Please ask a healthcare professional or choose a topic in the Education Library. I cannot diagnose or give individual treatment advice."

def change_page(p):
    st.session_state.page = p

def card(title, description, emoji="✦"):
    st.markdown(f'<div class="tile"><h3>{emoji} {title}</h3><p>{description}</p></div>', unsafe_allow_html=True)

def send_message(question):
    if not question or not question.strip():
        return
    status, answer = route(question)
    st.session_state.messages.append({"role":"user","content":question})
    st.session_state.messages.append({"role":"assistant","content":answer,"status":status})

with st.sidebar:
    st.markdown("## 💙 MediConnect")
    st.caption("Healthcare Assistant · University demo")
    st.divider()
    st.markdown("**Explore**")
    for item, emoji in zip(NAV, ["🏠","📖","💬","🩺","👩‍⚕️","🛡️"]):
        st.button(f"{emoji}  {item}", key=f"nav_{item}", use_container_width=True, type="primary" if st.session_state.page == item else "secondary", on_click=change_page, args=(item,))
    st.divider()
    st.caption("Demo only · Fictional data · No clinical monitoring")
    st.caption("Emergency? Alert staff or call local emergency services. UAE ambulance: 998.")

page = st.session_state.page
if page == "Welcome":
    st.markdown('''<div class="hero"><div class="eyebrow">✦ Healthcare assistant · Patient education</div><h1>Clearer care.<br>Closer connections.</h1><p>Understand your treatment, explore trusted educational topics, and find the right human support — in one welcoming place.</p></div>''', unsafe_allow_html=True)
    st.markdown('<div class="kicker">Welcome to your care portal</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        card("Continue as Patient", "Explore DVT, medication education, and an AI-style question experience.", "♡")
        st.button("Continue as Patient  →", type="primary", use_container_width=True, on_click=change_page, args=("Patient Education",))
    with c2:
        card("Healthcare Professional", "Explore the clinical oversight and handoff demonstration.", "♧")
        st.button("Healthcare Professional  →", use_container_width=True, on_click=change_page, args=("Healthcare Professional",))
    st.write("")
    st.info("I am a general education demo, not a doctor or nurse. I cannot diagnose, prescribe, monitor or contact staff. You may choose human help instead.")
    a,b,c=st.columns(3)
    with a: st.button("💬 Open assistant", use_container_width=True, on_click=change_page, args=("AI-style Chat",))
    with b: st.button("🛡️ Speak to a person", use_container_width=True, on_click=change_page, args=("Safety & Privacy",))
    with c: st.button("📋 View fictional case", use_container_width=True, on_click=change_page, args=("Fictional DVT Case",))

elif page == "Patient Education":
    st.markdown('<div class="kicker">Patient education library</div>', unsafe_allow_html=True)
    st.title("Health information, made clearer")
    st.write("Browse short, general explanations. This library is educational, not a personal medical assessment.")
    st.subheader("Featured: DVT and anticoagulants")
    cols=st.columns(3)
    for col,key in zip(cols,["DVT","PE","Anticoagulants"]):
        with col:
            title,desc=TOPICS[key]
            card(title,desc,"✚")
    st.subheader("Explore more medical terms")
    selection=st.selectbox("Choose a topic",list(TOPICS.keys()),format_func=lambda k:TOPICS[k][0])
    st.markdown(f"### {TOPICS[selection][0]}")
    st.write(TOPICS[selection][1])
    st.button("Ask the assistant  →", type="primary", on_click=change_page, args=("AI-style Chat",))
    st.warning("If you have new, worsening, or concerning symptoms, seek a healthcare professional instead of relying on this information.")

elif page == "AI-style Chat":
    st.markdown('<div class="kicker">MediConnect assistant · Educational demo</div>', unsafe_allow_html=True)
    st.title("What would you like to know?")
    st.write("Ask about DVT, blood pressure, diabetes, asthma, medicines, and other topics in our limited education library.")
    st.info("This chat looks conversational but uses prepared responses, not a generative AI model. It cannot answer every medical question or reliably identify every emergency.")
    if not st.session_state.consent:
        st.warning("Privacy: Please do not enter real names, IDs, contact details, test results, symptoms, medications, or personal medical history. Use fictional examples only. This demo does not send messages to hospital staff.")
        x,y=st.columns(2)
        with x:
            if st.button("Continue with demo chat",type="primary",use_container_width=True):
                st.session_state.consent=True
                st.rerun()
        with y:
            st.button("Speak to a person instead",use_container_width=True,on_click=change_page,args=("Safety & Privacy",))
    else:
        st.markdown("**Try a sample educational question**")
        a,b,c=st.columns(3)
        for col, prompt in zip([a,b,c],["What is DVT?","What is diabetes?","What is a blood thinner?"]):
            with col:
                if st.button(prompt,use_container_width=True,key=f"sample_{prompt}"):
                    send_message(prompt)
                    st.rerun()
        for message in st.session_state.messages:
            with st.chat_message(message["role"],avatar="💙" if message["role"]=="assistant" else "👤"):
                if message.get("status")=="urgent": st.error(message["content"])
                elif message.get("status")=="review": st.warning(message["content"])
                else: st.markdown(message["content"])
        question=st.chat_input("Ask a general medical education question…")
        if question:
            send_message(question)
            st.rerun()
        left,right=st.columns(2)
        with left:
            if st.button("🗑️ Exit / Clear demo chat",use_container_width=True):
                st.session_state.messages=[]
                st.session_state.consent=False
                st.rerun()
        with right:
            st.button("👩‍⚕️ Speak to a person",use_container_width=True,on_click=change_page,args=("Safety & Privacy",))
        with st.expander("Feedback and accountability"):
            if st.button("This answer was unclear"):
                st.info("Please ask a healthcare professional. No feedback was sent to staff.")
            if st.button("Report a concern"):
                st.info("This prototype does not send reports. Tell the demonstration facilitator or your healthcare team directly.")
    st.caption("General educational demo — not medical advice. For urgent symptoms, press the bedside call button or call emergency services. No messages are monitored or sent.")

elif page == "Fictional DVT Case":
    st.markdown('<div class="kicker">Saeed’s teaching case · Synthetic data only</div>', unsafe_allow_html=True)
    st.title("Meet Fatima Ahmed")
    st.info("Fatima is entirely fictional. This case illustrates a clinician-documented DVT pathway; it is not your medical record or a treatment recommendation.")
    a,b,c=st.columns(3)
    with a: card("46 years", "Fictional patient · Arabic preferred", "👤")
    with b: card("Left popliteal DVT", "Ultrasound-confirmed in the fictional case", "🩺")
    with c: card("Outpatient follow-up", "Treatment and review arranged by the fictional care team", "📅")
    st.subheader("Case journey")
    st.markdown("**1. Presentation:** Left calf pain, swelling and warmth after a long flight.\n\n**2. Hospital assessment:** A clinician evaluates the patient and ultrasound confirms the clot.\n\n**3. Treatment:** The fictional clinician prescribes apixaban and gives a written plan. This app never prescribes or adjusts doses.\n\n**4. Follow-up:** A treatment review is planned and elective septoplasty is postponed pending clinician reassessment.")
    st.subheader("Saeed's 48 patient questions")
    st.caption("These are proposed sample responses for a fictional case and require clinical approval before patient use. The labels are case-design categories, not a validated triage tool.")
    group=st.selectbox("Choose a question category",["Education (1–18)","Care team review (19–36)","Immediate assessment (37–48)"])
    category={"Education (1–18)":"education","Care team review (19–36)":"review","Immediate assessment (37–48)":"urgent"}[group]
    for item in BANK:
        if item["category"]==category:
            with st.expander(f'{item["number"]}. {item["question"]}'):
                if category=="urgent":
                    st.error("Emergency example — get immediate human help; no alert is sent by this prototype.")
                elif category=="review":
                    st.warning("Care team review example — this prototype does not contact anyone.")
                st.write(item["answer"])
                st.caption("Source: Saeed's fictional DVT case and patient question bank. For teaching only.")

elif page == "Healthcare Professional":
    st.markdown('<div class="kicker">Professional demonstration · No live clinical connection</div>', unsafe_allow_html=True)
    st.title("Healthcare professional portal")
    st.write("A demonstration of how a future approved system could support clinical oversight. This version has **no login, patient records, messaging, or staff notification system**.")
    a,b=st.columns(2)
    with a: card("Review educational content", "Review and version-control patient information before any clinical use.", "📖")
    with b: card("Human handoff", "A real service would need authenticated routing and verified receipt states.", "🤝")
    st.subheader("Demonstration workflow")
    st.markdown("**Patient asks a question** → **Educational answer or safety handoff** → **Patient contacts a real clinician directly**")
    st.warning("No message has been sent. No clinician has been alerted. No medical record has been accessed.")
    st.button("View safety principles",type="primary",on_click=change_page,args=("Safety & Privacy",))

elif page == "Safety & Privacy":
    st.markdown('<div class="kicker">Human first · Safety by design</div>', unsafe_allow_html=True)
    st.title("Your safety comes first")
    st.error("**Need urgent help?** In hospital, press the bedside nurse-call button or alert staff immediately. Outside hospital, call local emergency services (UAE ambulance: 998). Do not wait for this app. It has not alerted anyone.")
    st.subheader("Speak to a person")
    st.write("You can always choose a nurse, doctor, pharmacist, or hospital staff member instead of this assistant. Declining the chatbot does not affect your care.")
    st.info("**Non-urgent review:** This question needs a healthcare professional. Please contact your care team. This prototype has not sent a message.")
    st.subheader("What this demo can and cannot do")
    a,b=st.columns(2)
    with a: card("Can do", "Show general education, a fictional DVT case, and sample question responses.", "✓")
    with b: card("Cannot do", "Diagnose, prescribe, interpret personal results, monitor emergencies, or contact clinicians.", "✕")
    st.subheader("Privacy and responsible use")
    st.write("Use fictional names and synthetic questions only. Do not enter personal identifiers, medical records, detailed medical histories, images, or test results. This demo keeps chat messages in the current Streamlit session for display and offers a clear-chat control; it is not an approved confidential clinical messaging service.")
    st.caption("Design rules adapted from Ali's Healthcare Assistant Ethical Principles for Prototype. A real deployment requires hospital-approved privacy information, security review, clinical validation, and verified human handoff.")
    if st.button("Exit / Clear demo chat",type="primary"):
        st.session_state.messages=[]
        st.session_state.consent=False
        st.success("Current demo conversation cleared from this session.")

st.divider()
st.caption("MediConnect · University educational prototype · Hessa-inspired design · Saeed's fictional DVT case · Ali's safety principles · Not a clinical service")
