"""MediConnect mobile-style university demo. No real patient data or clinical use."""
import re
from difflib import SequenceMatcher
import streamlit as st

st.set_page_config(page_title="MediConnect | Patient Portal", page_icon="💙", layout="centered", initial_sidebar_state="collapsed")

BANK = [{'number': 1,
  'question': 'What is the clot in my leg?',
  'answer': 'It is a clot in the left popliteal deep vein behind your knee, confirmed on your ultrasound.',
  'category': 'education'},
 {'number': 2,
  'question': 'Does a blood thinner dissolve it immediately?',
  'answer': 'Apixaban reduces further clotting. Your body may gradually clear the clot; recovery is not '
            'immediate.',
  'category': 'education'},
 {'number': 3,
  'question': 'Did my flight definitely cause this?',
  'answer': 'Long sitting and obesity may contribute, but your history cannot prove one cause.',
  'category': 'education'},
 {'number': 4,
  'question': 'What is the name of my medicine?',
  'answer': 'It is apixaban, sold as Eliquis. It is an oral anticoagulant that blocks clotting factor Xa.',
  'category': 'education'},
 {'number': 5,
  'question': 'How many tablets do I take during the first week?',
  'answer': 'Your prescription uses 5 mg tablets: take two per dose, twice daily for seven days. Check that '
            'your pack really contains 5 mg tablets.',
  'category': 'education'},
 {'number': 6,
  'question': 'What changes on day 8?',
  'answer': 'Take one 5 mg tablet per dose, twice daily, according to your written switch date. If the date '
            'is unclear, ask the pharmacist before changing it.',
  'category': 'education'},
 {'number': 7,
  'question': 'Do I take it with breakfast?',
  'answer': 'You may take apixaban with or without food. Keep to the twice-daily schedule your team gave '
            'you.',
  'category': 'education'},
 {'number': 8,
  'question': 'I forgot one dose today and know which one it was. What does the leaflet say?',
  'answer': 'Take the missed dose as soon as possible on the same day and resume twice-daily dosing. Never '
            'double a dose to make up for one. If timing is unclear, ask your pharmacist.',
  'category': 'education'},
 {'number': 9,
  'question': 'If the swelling settles, can I stop early?',
  'answer': 'Feeling better does not mean treatment is complete. Keep to your prescription and speak with '
            'your clinician before any change. Stopping early can increase clot risk.',
  'category': 'education'},
 {'number': 10,
  'question': 'Why do I have a review at three months?',
  'answer': 'That is when your clinician reviews whether you should continue treatment. It is not an '
            'automatic stop date.',
  'category': 'education'},
 {'number': 11,
  'question': 'What side effect should I know about?',
  'answer': 'Bleeding is the main concern. New unusual bleeding needs clinical advice; severe bleeding needs '
            'emergency help.',
  'category': 'education'},
 {'number': 12,
  'question': 'Should I tell my dentist?',
  'answer': 'Yes. Tell every clinician and dentist that you take apixaban, and carry your medicine list. Do '
            'not stop it for a procedure unless the responsible clinician gives a plan.',
  'category': 'education'},
 {'number': 13,
  'question': 'How should I store these tablets?',
  'answer': 'Keep them at room temperature, 20–25°C, in a safe place out of children’s reach. Follow the '
            'storage directions on your dispensed pack.',
  'category': 'education'},
 {'number': 14,
  'question': 'Can I give spare tablets to my husband?',
  'answer': 'No. Apixaban is prescribed for your own condition and can cause serious bleeding. He needs his '
            'own clinical advice.',
  'category': 'education'},
 {'number': 15,
  'question': 'What is the difference between DVT and PE?',
  'answer': 'DVT is a deep-vein clot. PE is a clot in a lung blood vessel and can be life-threatening.',
  'category': 'education'},
 {'number': 16,
  'question': 'What does twice daily mean in my discharge plan?',
  'answer': 'It means two separate doses each day, using the times written by your team. Do not take the '
            'whole day’s tablets together.',
  'category': 'education'},
 {'number': 17,
  'question': 'Why is my nose operation postponed?',
  'answer': 'Your recent DVT makes interrupting treatment risky. The plan is to wait at least three months '
            'after diagnosis and then reassess with your surgical team.',
  'category': 'education'},
 {'number': 18,
  'question': 'Will the chatbot change my dose if I send a blood result?',
  'answer': 'No. Your clinical team must interpret results and decide treatment changes. I can explain the '
            'written plan and help identify when you need medical attention.',
  'category': 'education'},
 {'number': 19,
  'question': 'My leg is more swollen today. Should I wait for next week?',
  'answer': 'Contact your team for assessment today; in hospital, tell the nurse now. New breathlessness, '
            'chest pain or fainting means emergency help immediately.',
  'category': 'review'},
 {'number': 20,
  'question': 'My other calf has started hurting and swelling. Is it another clot?',
  'answer': 'Arrange assessment today. An online conversation cannot diagnose or exclude another DVT. '
            'Escalate immediately if PE symptoms appear.',
  'category': 'review'},
 {'number': 21,
  'question': 'My gums bleed a little when brushing, but it stops. Is that okay?',
  'answer': 'Report new bleeding to your team today, even if it stopped. If bleeding becomes heavy or will '
            'not stop, seek emergency help.',
  'category': 'review'},
 {'number': 22,
  'question': 'I keep getting short nosebleeds that stop. Should I skip a tablet?',
  'answer': 'Speak to your team today; do not decide to skip doses yourself. Persistent or heavy bleeding, '
            'weakness or faintness needs immediate assessment.',
  'category': 'review'},
 {'number': 23,
  'question': 'My period is heavier than usual but I feel well. What should I do?',
  'answer': 'Contact your team today and describe the amount and duration. Rapid heavy bleeding, dizziness, '
            'fainting or marked weakness requires emergency help.',
  'category': 'review'},
 {'number': 24,
  'question': 'There is a pink tinge in my urine. Can it wait?',
  'answer': 'Get medical advice today, even without pain. Heavy blood loss, clots preventing urination, '
            'faintness or severe pain requires immediate assessment.',
  'category': 'review'},
 {'number': 25,
  'question': 'A large bruise appeared without an injury. Is this normal?',
  'answer': 'Report it today, especially if enlarging. Rapid expansion, severe pain, weakness or fainting '
            'requires immediate assessment.',
  'category': 'review'},
 {'number': 26,
  'question': 'Can I take ibuprofen, naproxen or aspirin for pain?',
  'answer': 'Check with your pharmacist or prescriber before taking them. They can increase bleeding risk '
            'with apixaban. Ask for an appropriate pain plan.',
  'category': 'review'},
 {'number': 27,
  'question': 'Another doctor prescribed an antibiotic. Can I start it?',
  'answer': 'Have the pharmacist check its exact name, dose and your medicines before the first dose; if '
            'treatment is urgent, contact the prescribing service promptly.',
  'category': 'review'},
 {'number': 28,
  'question': 'Can I use St John’s wort or a herbal supplement?',
  'answer': 'Ask a pharmacist before use. St John’s wort can reduce apixaban exposure and should be avoided '
            'with it; other products need individual review.',
  'category': 'review'},
 {'number': 29,
  'question': 'I accidentally took an extra dose. What now?',
  'answer': 'Contact your prescriber or urgent medical advice service now, even if you feel well. Tell them '
            'the strength, amount and time. Any major bleeding or collapse requires emergency help.',
  'category': 'review'},
 {'number': 30,
  'question': 'I missed yesterday’s doses and cannot remember today’s. Should I catch up?',
  'answer': 'Do not take extra tablets to catch up. Contact your pharmacist or prescriber now to establish a '
            'safe schedule.',
  'category': 'review'},
 {'number': 31,
  'question': 'I vomited after my tablet. Should I take another?',
  'answer': 'Contact your pharmacist or clinician now for advice based on timing and whether the tablet was '
            'retained. Do not automatically repeat it. Blood in vomit requires emergency help.',
  'category': 'review'},
 {'number': 32,
  'question': 'I am running out of tablets tonight. Can I take half doses?',
  'answer': 'Contact your pharmacy or prescribing service now to arrange supply. Do not ration or halve the '
            'prescribed dose yourself.',
  'category': 'review'},
 {'number': 33,
  'question': 'I might be pregnant. Should I stop apixaban?',
  'answer': 'Contact your prescribing team today for a safe treatment plan. Do not leave a DVT untreated by '
            'stopping on your own. Tell them if you are breastfeeding or planning to do so.',
  'category': 'review'},
 {'number': 34,
  'question': 'Can I have a dental extraction or reschedule septoplasty now?',
  'answer': 'Ask the procedural clinician and anticoagulation prescriber to agree a plan before booking or '
            'changing tablets. Your postponed septoplasty still needs reassessment after the minimum delay.',
  'category': 'review'},
 {'number': 35,
  'question': 'Can I fly next week or begin strenuous exercise?',
  'answer': 'Discuss the timing and activity with your treating team before making plans. Your recent DVT, '
            'symptoms, medication and injury risk need individual consideration.',
  'category': 'review'},
 {'number': 36,
  'question': 'My father had a clot. Do I need genetic tests or lifelong tablets?',
  'answer': 'Tell your clinician about his postoperative clot. It does not establish an inherited disorder '
            'in you. Testing and treatment duration need a clinical review.',
  'category': 'review'},
 {'number': 37,
  'question': 'I suddenly cannot catch my breath. Could this be anxiety?',
  'answer': 'This could be a serious emergency. In hospital, alert staff now. At home, call 998 in the UAE '
            'or your local ambulance number. Do not drive yourself.',
  'category': 'urgent'},
 {'number': 38,
  'question': 'My chest hurts sharply when I breathe. Can I wait?',
  'answer': 'Get emergency help now: alert hospital staff immediately, or call an ambulance at home. Do not '
            'wait to see whether it passes.',
  'category': 'urgent'},
 {'number': 39,
  'question': 'I coughed up blood, even though I took my tablets. What should I do?',
  'answer': 'Seek emergency assessment now. Alert staff in hospital or call an ambulance at home. Taking '
            'apixaban does not make this safe to ignore.',
  'category': 'urgent'},
 {'number': 40,
  'question': 'I fainted and now my heart is racing and I feel breathless. Is that a side effect?',
  'answer': 'Call for emergency help now. In hospital, use the call bell or alert staff; at home, call an '
            'ambulance and do not drive.',
  'category': 'urgent'},
 {'number': 41,
  'question': 'My cut is bleeding heavily and pressure is not stopping it. What now?',
  'answer': 'Keep firm direct pressure with a clean cloth while help is arranged. Alert staff immediately or '
            'call an ambulance at home. Tell responders you take apixaban.',
  'category': 'urgent'},
 {'number': 42,
  'question': 'I vomited blood or material like coffee grounds. Can I take an antacid?',
  'answer': 'Get emergency help now. Alert hospital staff or call an ambulance at home. Do not delay for a '
            'home remedy; the emergency team must direct treatment and further dosing.',
  'category': 'urgent'},
 {'number': 43,
  'question': 'My stool is black and sticky like tar. Is that from the medicine?',
  'answer': 'Seek immediate emergency assessment. In hospital, tell staff now; at home, call an ambulance, '
            'especially with weakness or dizziness. Do not dismiss this as an expected effect.',
  'category': 'urgent'},
 {'number': 44,
  'question': 'I suddenly have an extremely severe headache and feel confused. Should I rest?',
  'answer': 'Get emergency help immediately. Alert staff or call an ambulance at home; do not drive or wait '
            'for a routine appointment.',
  'category': 'urgent'},
 {'number': 45,
  'question': 'My face is drooping and I cannot speak clearly. What should I do?',
  'answer': 'Alert staff immediately or call an ambulance now. If possible, note when symptoms began without '
            'delaying help. Do not take extra apixaban or aspirin.',
  'category': 'urgent'},
 {'number': 46,
  'question': 'I fell and hit my head but feel fine. Can I stay home?',
  'answer': 'You need immediate medical assessment because you take apixaban. Tell staff now if in hospital. '
            'At home, arrange immediate emergency assessment; call an ambulance for significant injury, '
            'symptoms or unsafe transport. Do not drive yourself.',
  'category': 'urgent'},
 {'number': 47,
  'question': 'My period is suddenly very heavy and I feel faint. Should I just call tomorrow?',
  'answer': 'Get emergency help now. Alert hospital staff or call an ambulance at home. Do not wait until '
            'tomorrow; tell responders about the bleeding and last apixaban dose.',
  'category': 'urgent'},
 {'number': 48,
  'question': 'My lips and tongue are swelling and breathing is difficult. What should I do?',
  'answer': 'Alert hospital staff immediately or call an ambulance at home. This may be a severe allergic '
            'reaction and needs emergency treatment now.',
  'category': 'urgent'}]

st.markdown("""<style>
:root{color-scheme:light}html,body,.stApp,[data-testid="stAppViewContainer"]{background:#edf3f3!important;color:#143d49!important}
[data-testid="stHeader"]{background:#edf3f3!important;box-shadow:none!important;height:2.2rem!important}
[data-testid="stToolbar"]{opacity:.35!important}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none!important}
.block-container{max-width:570px!important;padding:1rem 1.1rem 5rem!important;background:#f8fbfb;min-height:100vh;box-shadow:0 10px 40px #0d3c4814}
h1,h2,h3,h4,p,label{color:#143d49}h1{font-size:1.9rem!important;letter-spacing:-.05em}h2{font-size:1.35rem!important}
.hero{background:linear-gradient(145deg,#073f4d,#126d77);border-radius:24px;padding:33px 25px;color:white;margin:10px 0 24px;box-shadow:0 12px 24px #0b51551c}
.hero *{color:white!important}.hero h1{font-size:2.25rem!important;line-height:1.13;margin:18px 0}.hero p{font-size:14px;line-height:1.65}
.eyebrow{font-size:11px;letter-spacing:1.8px;font-weight:800;color:#2d8e95;text-transform:uppercase;margin:10px 0}
.panel{background:white;border:1px solid #deebed;border-radius:19px;padding:21px;margin:12px 0;box-shadow:0 5px 14px #093e4b08}
.panel h3{margin:0 0 10px;font-size:18px}.panel p{font-size:14px;line-height:1.7;color:#52737c}
.med{background:linear-gradient(145deg,#104552,#176976);color:white;border-radius:19px;padding:23px;margin:13px 0}
.med *{color:white!important}.med small{opacity:.8}.med h2{font-size:1.4rem!important}
.stButton button{width:100%;min-height:46px;border-radius:12px!important;border:1px solid #d7e6e8!important;background:white!important;color:#134654!important;font-weight:700!important}
.stButton button:hover{border-color:#158c91!important;background:#eaf8f7!important}
.stButton button[kind="primary"],.stFormSubmitButton button{background:#117b82!important;color:white!important;border-color:#117b82!important}
[data-testid="stChatMessage"]{background:white;border:1px solid #dbe8ea;border-radius:16px;margin:9px 0;padding:10px}
[data-testid="stChatInput"]{border:1px solid #91c4c5;border-radius:16px;background:white}
[data-testid="stAlert"]{border-radius:14px}.foot{color:#69848a;font-size:11px;text-align:center;margin-top:20px}
@media(min-width:800px){.block-container{border-radius:22px;margin-top:15px!important}}
</style>""",unsafe_allow_html=True)


if "screen" not in st.session_state: st.session_state.screen="Welcome"
if "role" not in st.session_state: st.session_state.role="Patient"
if "signed" not in st.session_state: st.session_state.signed=False
if "messages" not in st.session_state: st.session_state.messages=[]
if "lang" not in st.session_state: st.session_state.lang="English"
if "log" not in st.session_state: st.session_state.log=[]

EMERGENCY="🚨 **Get emergency help now.** If you are in hospital, press your bedside call button or alert staff immediately. Outside hospital, call an ambulance (998 in the UAE; otherwise your local emergency number). Do not drive yourself. **This app has not contacted anyone.**"
REVIEW="🟠 **Please speak with a healthcare professional.** This question needs individual clinical assessment. Contact your care team; for new or worsening symptoms seek prompt assessment. **This prototype has not sent a message.**"
URGENT_TERMS=["chest pain","chest hurts","cant breathe","can't breathe","cannot breathe","breathless","shortness of breath","difficulty breathing","coughing blood","coughed blood","vomit blood","vomited blood","bleeding heavily","heavy bleeding","won't stop bleeding","fainted","fainting","unconscious","face droop","slurred speech","seizure","severe allergic","tongue swelling","suicidal","kill myself","hit my head","head injury","black tarry stool","worst headache","ألم الصدر","ضيق التنفس","نزيف شديد","إغماء","جلطة دماغية"]
REVIEW_TERMS=["my dose","change my dose","stop taking","should i stop","extra dose","missed dose","pregnant","new swelling","more swollen","blood in urine","nosebleed","interaction","my results","my blood test","diagnose me","do i have","prescribe","surgery","side effect i'm having","أغير الجرعة","نتائج تحاليلي"]
GENERAL={
"diabetes":"Diabetes is a condition in which blood glucose is higher than normal. Management depends on the person and may include nutrition, activity, monitoring and prescribed medicines. A clinician can discuss individual care.",
"blood pressure":"Blood pressure measures the force of blood against artery walls. Persistently high blood pressure can affect health. A clinician should interpret your readings and discuss treatment.",
"asthma":"Asthma is a condition that can cause inflammation and narrowing of airways, leading to cough, wheeze or breathlessness. If you currently have difficulty breathing, seek urgent help.",
"anemia":"Anemia means having too few healthy red blood cells or insufficient hemoglobin. Causes vary and need professional assessment.",
"cholesterol":"Cholesterol is a fat-like substance in the blood. Some types are associated with cardiovascular risk. Your care team can explain testing and management.",
"dvt":"Deep vein thrombosis (DVT) is a blood clot in a deep vein, often in a leg. Symptoms may include swelling, pain or warmth. New symptoms need medical assessment.",
"blood thinner":"Anticoagulants, sometimes called blood thinners, help prevent clots from growing and new clots forming. They can increase bleeding risk; never change your prescription based on this demo.",
"apixaban":"Apixaban (Eliquis) is an anticoagulant used for certain blood-clot conditions. It can increase bleeding risk. Follow your clinician's written prescription.",
"pulmonary embolism":"Pulmonary embolism (PE) occurs when a blood clot blocks a lung blood vessel. Sudden chest pain, difficulty breathing or fainting needs emergency help.",
"pe":"Pulmonary embolism (PE) is a blood clot in a lung blood vessel. Sudden breathing difficulty or chest pain needs emergency help."
}

def clean(s):
    return re.sub(r"[^a-z0-9\u0600-\u06ff ]"," ",s.lower()).strip()

def respond(q):
    t=clean(q)
    if any(clean(w) in t for w in URGENT_TERMS): return EMERGENCY,"urgent"
    if any(clean(w) in t for w in REVIEW_TERMS): return REVIEW,"review"
    for k,v in GENERAL.items():
        if clean(k) in t: return v,"education"
    # Match only sufficiently similar questions; don't invent answers.
    matches=[]
    for item in BANK:
        score=SequenceMatcher(None,t,clean(item['question'])).ratio()
        matches.append((score,item))
    score,item=max(matches,key=lambda x:x[0])
    if score>=0.76:
        if item['category']=='urgent': return EMERGENCY,"urgent"
        if item['category']=='review': return REVIEW,"review"
        # These answers refer to the fictional Fatima case, not the actual user.
        return "**In the fictional Fatima case:** "+item['answer'],"education"
    return "I don't have a reviewed answer to that question. I can explain general topics such as DVT, diabetes, asthma, blood pressure, and anticoagulants. For personal symptoms, medicines or test results, please ask a healthcare professional.","unknown"

def nav(target):
    st.session_state.screen=target
    st.rerun()

def tile(title,detail):
    st.markdown(f'<div class="panel"><h3>{title}</h3><p>{detail}</p></div>',unsafe_allow_html=True)

def top(title,sub=""):
    st.markdown('<div class="eyebrow">MEDICONNECT • PATIENT PORTAL</div>',unsafe_allow_html=True)
    st.title(title)
    if sub: st.caption(sub)

def bottom():
    st.divider()
    a,b,c,d,e=st.columns(5)
    for col,label,target in [(a,"🏠 Home","Dashboard"),(b,"♡ DVT","Diagnosis"),(c,"💊 Meds","Medication"),(d,"🛡️ Safety","Safety"),(e,"💬 Chat","Chat")]:
        with col:
            if st.button(label,key="bottom_"+target): nav(target)
    st.markdown('<div class="foot">University demonstration • Synthetic case only • No real care team connected</div>',unsafe_allow_html=True)

screen=st.session_state.screen
if screen=="Welcome":
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#a4e1e0">PATIENT EDUCATION, MADE PERSONAL</div><h1>Clearer care.<br>Closer connections.</h1><p>Understand your treatment, find trusted educational information, and know when to ask for help.</p></div>',unsafe_allow_html=True)
    top("Welcome to your care portal","Choose how to explore this demonstration")
    tile("♡ Continue as Patient","View the fictional treatment plan, education and medical assistant.")
    if st.button("Continue as Patient  →",type="primary"): st.session_state.role="Patient";nav("Sign in")
    tile("♧ Healthcare Professional","Review a simulated patient and the clinical handoff design.")
    if st.button("Healthcare Professional  →"): st.session_state.role="Professional";nav("Sign in")
    st.info("Demonstration only. No real accounts, records, messaging, or emergency monitoring.")
elif screen=="Sign in":
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#a4e1e0">SIMULATED ACCESS</div><h1>Your care, in one place.</h1><p>Continue to the demonstration portal. No real authentication is connected.</p></div>',unsafe_allow_html=True)
    top("Sign in to continue", "No email address or password required")
    st.info("This is a fictional sign-in screen. Never enter a real password or personal information.")
    st.text_input("Demonstration account",value="Fatima Ahmed — fictional patient" if st.session_state.role=="Patient" else "Demo healthcare professional",disabled=True)
    if st.button("Enter demonstration dashboard →",type="primary"): st.session_state.signed=True;nav("Dashboard" if st.session_state.role=="Patient" else "Professional")
    if st.button("← Back to role selection"): nav("Welcome")
elif screen=="Dashboard":
    top("Welcome back, Fatima!", "Fictional patient • Your treatment overview")
    st.markdown('<div class="med"><small>CURRENT TREATMENT PLAN • FICTIONAL CASE</small><h2>💊 Apixaban (Eliquis)</h2><p>Deep Vein Thrombosis · Left popliteal vein</p><hr><p>Prescribed course: at least 3 months, then clinician review</p><p>Follow-up: demonstration dates only</p></div>',unsafe_allow_html=True)
    st.subheader("How can we help today?")
    items=[("♡ My Diagnosis","Understand DVT and the fictional case","Diagnosis"),("💊 My Medication","Apixaban treatment and education","Medication"),("📋 Medication Instructions","Understand the written fictional plan","Instructions"),("🛡️ Side Effects & Safety","Warning signs and getting help","Safety"),("💬 Ask AI Assistant","Type your own medical education question","Chat"),("✉️ Healthcare Team Messages","Simulated inbox — no messages sent","Messages"),("🗓️ Book Appointment","Demonstration only — no real booking","Appointments"),("📝 Medication Log","Record synthetic practice entries only","Log")]
    for title,detail,target in items:
        if st.button(title+"   →",key="go_"+target):nav(target)
        st.caption(detail)
    st.error("Emergency symptoms? Alert hospital staff now or call an ambulance (998 in UAE). This app does not send alerts.")
    bottom()
elif screen=="Diagnosis":
    top("Understanding DVT", "My Diagnosis • Fictional patient case")
    tile("♡ What is DVT?","A deep vein thrombosis is a blood clot in a deep vein, most often in the leg. It may cause swelling, warmth, pain or tenderness.")
    tile("Why does treatment matter?","Treatment helps reduce clot growth and the chance of new clots. A clot travelling to the lungs may cause a pulmonary embolism.")
    tile("Fatima's fictional case","The example case has an ultrasound-confirmed left popliteal DVT following prolonged travel. This is not your medical record.")
    if st.button("Ask a question about DVT →",type="primary"):nav("Chat")
    bottom()
elif screen in ("Medication","Instructions"):
    top("Apixaban (Eliquis)","My Medication • Fictional verified case plan, not your prescription")
    st.markdown('<div class="med"><small>ANTICOAGULANT EDUCATION</small><h2>💊 Apixaban</h2><p>Helps prevent existing clots from growing and new clots forming.</p></div>',unsafe_allow_html=True)
    tile("Days 1–7 · Fictional case","The example written plan uses 10 mg twice daily (two 5 mg tablets per dose). This is not an instruction for you.")
    tile("Day 8 onward · Fictional case","The example plan uses 5 mg twice daily. The real patient’s prescriber must confirm dosing and dates.")
    tile("Clinical review","The fictional plan includes a treatment review after at least three months. Do not stop or change anticoagulants without a clinician’s instructions.")
    st.warning("Never use this demonstration to decide your own medication dose or whether to stop treatment.")
    if st.button("Side effects and safety →"):nav("Safety")
    bottom()
elif screen=="Safety":
    top("Know when to get help","Medication safety and human support")
    st.success("GENERAL EDUCATION: Take medicine only as prescribed. Tell clinicians and dentists about anticoagulants and check before starting new medicines.")
    st.warning("**Contact your healthcare team today** for new swelling, unusual bleeding, medication mistakes or concerns. This demo has not sent a message.")
    st.error(EMERGENCY)
    if st.button("Speak to a person →",type="primary"):nav("Help")
    bottom()
elif screen=="Chat":
    top("Ask AI Assistant", "Type any question • General education only")
    st.info("This looks like a conversational AI, but uses prepared educational answers, not a generative AI model. It cannot answer every medical question or reliably detect every emergency.")
    st.caption("Please do not enter names, phone numbers, ID numbers, records, results, or private medical history.")
    for m in st.session_state.messages:
        with st.chat_message(m['role']): st.markdown(m['content'])
    prompt=st.chat_input("Type your medical education question here…")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        answer,kind=respond(prompt)
        st.session_state.messages.append({'role':'assistant','content':answer})
        st.rerun()
    c1,c2=st.columns(2)
    with c1:
        if st.button("🗑️ Clear demo chat"):
            st.session_state.messages=[];st.rerun()
    with c2:
        if st.button("👩‍⚕️ Speak to a person"):nav("Help")
    st.caption("This assistant is not a doctor, cannot diagnose, prescribe or monitor you, and has not alerted anyone.")
    bottom()
elif screen=="Help":
    top("Speak to a person", "You can choose human help at any time")
    st.error(EMERGENCY)
    st.info(REVIEW)
    st.write("In hospital, ask the nearest nurse or doctor or use your bedside call button. Outside hospital, contact your own healthcare provider. No request has been sent by this prototype.")
    if st.button("Return to dashboard →",type="primary"):nav("Dashboard")
    bottom()
elif screen=="Messages":
    top("Healthcare Team Messages", "Demonstration inbox")
    st.info("No clinical messaging system is connected. No message has been sent, received, or acknowledged.")
    if st.button("How to contact staff →",type="primary"):nav("Help")
    bottom()
elif screen=="Appointments":
    top("Appointments", "Demonstration only")
    st.info("Appointments cannot be booked through this prototype. Please contact your care team for actual scheduling.")
    bottom()
elif screen=="Log":
    top("Medication Log", "Practice only • Do not enter real health data")
    choice=st.selectbox("Fictional dose status",["Taken (sample)","Not taken (sample)","Unsure (sample)"])
    if st.button("Add demo entry",type="primary"):
        st.session_state.log.append(choice)
        st.success("Synthetic demonstration entry added. No clinician was notified.")
    for i,x in enumerate(st.session_state.log): st.write(f"Demo entry {i+1}: {x}")
    if st.button("Clear demo log"):st.session_state.log=[];st.rerun()
    bottom()
elif screen=="Professional":
    top("Healthcare Professional", "Fictional demonstration • No patient records connected")
    tile("Case overview","Fatima Ahmed, 46, fictional ultrasound-confirmed left popliteal DVT, prescribed apixaban and outpatient follow-up.")
    tile("Human oversight","Clinicians make all decisions about diagnosis, dosing, results and discharge. The assistant must never claim a message was sent without confirmation.")
    st.subheader("Saeed's 48 patient questions")
    category=st.selectbox("Question category",["Education","Review with clinician","Immediate assessment"])
    mapping={"Education":"education","Review with clinician":"review","Immediate assessment":"urgent"}
    for item in BANK:
        if item['category']==mapping[category]:
            with st.expander(f"{item['number']}. {item['question']}"):
                st.write(item['answer'])
                st.caption("Sample response for fictional case; requires clinical approval. Not a validated triage algorithm.")
    bottom()
