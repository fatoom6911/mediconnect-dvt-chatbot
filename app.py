"""MediConnect core patient journey — educational demonstration, not a clinical system."""
import re
from difflib import SequenceMatcher
import streamlit as st

st.set_page_config(page_title="MediConnect | Medication Journey",page_icon="💙",layout="wide",initial_sidebar_state="collapsed")
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

# Sample patient context comes from Saeed's case, not user input or hospital records.
PATIENT = {
    "display_name":"Fatima", "medication":"Apixaban (Eliquis)",
    "diagnosis":"Deep vein thrombosis (DVT), left popliteal vein",
    "purpose":"An anticoagulant that helps prevent the existing blood clot from growing and new clots forming.",
    "instructions":"In this sample prescription: days 1–7, 10 mg twice daily (two 5 mg tablets per dose); from day 8, 5 mg twice daily (one 5 mg tablet per dose). Follow the written switch date. These details are NOT dosing advice for another patient.",
    "side_effects":"Bleeding is an important risk. New or unusual bleeding needs a healthcare professional's assessment. Heavy or uncontrolled bleeding needs emergency help.",
    "follow_up":"A clinician review is planned at approximately three months; this is not an automatic stop date.",
}
STEPS=[("Medication","💊"),("What it's for","♡"),("How to take it","◷"),("Side effects","🛡"),("Ask a question","💬"),("Red flags","⚠"),("What to do next","➜")]
EMERGENCY=("🚨 **Possible emergency — get human help now.** If in hospital, press the nurse-call button or alert staff immediately. "
           "If outside hospital in the UAE, call **998** for an ambulance (or your local emergency number elsewhere). "
           "Do not drive yourself. **This prototype has NOT alerted anyone.**")
REVIEW=("This needs a healthcare professional. Contact your treating team or pharmacist for an individual assessment. "
        "If symptoms are new or worsening, seek prompt medical assessment. **No message has been sent.**")
UNKNOWN=("I don't have an approved answer to that question in this prototype. Please ask your healthcare team. "
         "If you are experiencing new or concerning symptoms, seek medical assessment; do not rely on this chat.")

# This is a conservative demo rule set, NOT a validated symptom detector or clinical triage engine.
EMERGENCY_PHRASES=["chest pain","chest hurts","pain in my chest","shortness of breath","difficulty breathing",
 "cannot breathe","cant breathe","can't breathe","breathless","coughing up blood","cough blood",
 "vomiting blood","vomit blood","blood in vomit","coffee ground vomit","severe bleeding","bleeding heavily",
 "bleeding won't stop","bleeding wont stop","uncontrolled bleeding","fainted","fainting","passed out",
 "unconscious","face drooping","face droop","slurred speech","can't speak","cannot speak",
 "seizure","severe allergic reaction","tongue swelling","lips swelling","kill myself","suicidal",
 "hit my head","head injury","fell and hit my head","sudden severe headache","worst headache",
 "black tarry stool","black sticky stool","ألم الصدر","ضيق التنفس","نزيف شديد","إغماء"]
REVIEW_PHRASES=["stop my medicine","stop taking","change my dose","increase my dose","decrease my dose",
 "missed dose","forgot my dose","extra dose","double dose","side effect i'm having","side effect i have",
 "blood in urine","nosebleed","bleeding gums","my blood test","my results","interpret my results",
 "can i take ibuprofen","can i take aspirin","pregnant","my leg is swollen","more swollen",
 "new swelling","other calf hurts","do i have","diagnose me","should i take","what dose should i",
 "can i stop","i have a headache","i feel dizzy","i am bleeding","i feel unwell",
 "speak to a nurse","speak to a doctor","talk to a person","talk to a nurse"]

def normalize(s):
    return re.sub(r"[^a-z0-9\u0600-\u06ff ]+"," ",s.lower()).strip()

def phrase_in(t,phrase):
    return re.search(r"(?<!\w)"+re.escape(normalize(phrase))+r"(?!\w)",t) is not None

def is_emergency(t):
    return any(phrase_in(t,x) for x in EMERGENCY_PHRASES)

def is_review(t):
    return any(phrase_in(t,x) for x in REVIEW_PHRASES)

def answer(question):
    t=normalize(question)
    if not t: return UNKNOWN
    # Urgent signs take priority over every education answer.
    if is_emergency(t): return EMERGENCY
    if is_review(t) or re.search(r"\b(i have|i feel|i am having|my symptoms|i took|i missed|i need to)\b",t):return REVIEW
    # Questions referring to "my" medication are answered from the same patient context shown on screen.
    purpose=["what is my medication for","why am i taking","why do i take","what does my medicine do",
             "what is apixaban for","why apixaban","why eliquis","what is it for","what does it do"]
    instructions=["how do i take it","how do i take my medication","how to take apixaban",
                  "how to take my medicine","how many tablets","when do i take","day 8","first week","twice daily"]
    side=["side effects","side effect","what are the risks","bleeding risk","what should i watch for"]
    if any(x in t for x in purpose):return f"Your listed medicine is **{PATIENT['medication']}**. {PATIENT['purpose']}"
    if any(x in t for x in instructions):return f"**Sample written plan for Fatima only:** {PATIENT['instructions']} If anything is unclear, ask the prescribing team before changing a dose."
    if any(x in t for x in side):return PATIENT['side_effects']+" For current symptoms, speak to your care team."
    if any(x in t for x in ["what medicine","which medicine","my medicine","my medication","medication name","medicine name","what am i prescribed"]):
        return f"The sample record lists **{PATIENT['medication']}** for **{PATIENT['diagnosis']}**. {PATIENT['purpose']}"
    if "dvt" in t or "blood clot" in t or "deep vein" in t:
        return "DVT means deep vein thrombosis: a blood clot in a deep vein, often in the leg. In Fatima's sample record, ultrasound confirmed a clot behind the left knee."
    if "pulmonary embolism" in t or re.search(r"\bpe\b",t):
        return "Pulmonary embolism (PE) is a clot in a lung blood vessel and can be life-threatening. New chest pain, breathlessness or fainting requires emergency help."
    if "anticoagulant" in t or "blood thinner" in t:
        return PATIENT['purpose']+" These medicines can increase bleeding risk."
    if "headache" in t or "head ache" in t or "headach" in t:
        return "A headache is pain or discomfort in the head and has many possible causes. This chatbot cannot determine the cause. A sudden extremely severe headache, confusion, weakness or difficulty speaking needs emergency help. For a headache you are experiencing, contact your care team, especially while taking an anticoagulant."
    # Limited matching to Saeed's reviewed-for-demo education question bank only.
    for item in BANK:
        if item['category']!='education':continue
        if SequenceMatcher(None,t,normalize(item['question'])).ratio()>=.88:
            return "**From the sample case:** "+item['answer']
    return UNKNOWN

CSS="""
<style>
:root {color-scheme:light;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:#f1f7f7!important;color:#123e49!important;}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none!important;}
[data-testid="stHeader"]{background:transparent!important;}
.block-container{max-width:1250px!important;width:100%!important;padding:3.4rem 2rem 4rem!important;}
*,*::before,*::after{box-sizing:border-box!important;}
[data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],[data-testid="column"],.element-container{min-width:0!important;}
.stMarkdown p,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{overflow-wrap:anywhere!important;}
h1,h2,h3,p{color:#123e49;}h1{font-size:clamp(1.9rem,3.8vw,3.5rem)!important;letter-spacing:-.04em!important;line-height:1.1!important;}
.hero{background:linear-gradient(115deg,#073a48,#126b70);color:#fff;border-radius:25px;padding:clamp(24px,4vw,46px);margin:0 0 20px;}
.hero *{color:#fff!important;}.hero h1{margin:10px 0 14px!important;}.hero p{font-size:1.1rem;line-height:1.65;max-width:750px;}
.panel{background:#fff;border:1px solid #d7e7e7;border-radius:18px;padding:clamp(18px,2.2vw,29px);margin:12px 0 18px;box-shadow:0 5px 18px #163e4910;overflow-wrap:anywhere;}
.panel h3{font-size:1.2rem!important;margin:0 0 9px!important;}.panel p{line-height:1.7;color:#476b73;}
.eyebrow{color:#217c80;font-weight:800;letter-spacing:.11em;text-transform:uppercase;font-size:.76rem;}
.stButton button{min-height:46px!important;height:auto!important;width:100%!important;white-space:normal!important;border-radius:12px!important;color:#114b55!important;border:1px solid #c8ddde!important;background:#fff!important;font-weight:700!important;}
.stButton button[kind="primary"]{background:#087a7f!important;color:white!important;border-color:#087a7f!important;}
[data-testid="stChatMessage"]{background:white!important;border:1px solid #d8e6e7!important;border-radius:14px!important;padding:12px!important;margin:10px 0!important;}
[data-testid="stChatInput"]{background:white!important;border:1px solid #94c3c5!important;border-radius:14px!important;}
[data-testid="stAlert"]{border-radius:12px!important;}
@media(max-width:700px){.block-container{padding:2.7rem .8rem 3rem!important;}.hero{border-radius:16px;padding:24px 20px;}.panel{padding:18px;}}
</style>
"""
st.markdown(CSS,unsafe_allow_html=True)
if 'step' not in st.session_state:st.session_state.step=0
if 'messages' not in st.session_state:st.session_state.messages=[]

def goto(i):
    st.session_state.step=i
    st.rerun()

def panel(title,body):
    st.markdown(f'<div class="panel"><h3>{title}</h3><p>{body}</p></div>',unsafe_allow_html=True)

st.markdown('<div class="hero"><div style="font-size:.85rem;font-weight:800;letter-spacing:.15em">MEDICONNECT · PATIENT JOURNEY</div><h1>Understand your medication.<br>Know your next step.</h1><p>A focused treatment journey with clear medication information, an assistant that uses the sample patient record, and direct human-help guidance.</p></div>',unsafe_allow_html=True)
st.caption('Educational university demonstration · Synthetic patient record only · No hospital connection, real sign-in, monitoring or medical advice.')

# Small responsive step navigation instead of unrelated sidebar pages.
with st.container():
    cols=st.columns(7,gap='small')
    for i,((label,ico),col) in enumerate(zip(STEPS,cols)):
        with col:
            if st.button(f'{i+1}. {label}',key=f'step_{i}',type='primary' if st.session_state.step==i else 'secondary'):
                goto(i)

idx=st.session_state.step
st.progress((idx+1)/len(STEPS),text=f'Step {idx+1} of 7 · {STEPS[idx][0]}')

if idx==0:
    st.header('My medication')
    panel('💊 Apixaban (Eliquis)',f"<b>Listed for:</b> {PATIENT['diagnosis']}<br><b>Medication type:</b> Anticoagulant (blood thinner)<br><b>Follow-up:</b> {PATIENT['follow_up']}")
    st.info('The details on this screen are taken from Saeed’s sample DVT case. They are not linked to a real patient chart.')
elif idx==1:
    st.header('What is it for?')
    panel('♡ Why this medication was prescribed',PATIENT['purpose'])
    panel('About DVT','DVT is a clot in a deep vein. The sample record describes a left popliteal DVT confirmed by ultrasound. Anticoagulation helps reduce further clotting; it does not dissolve the clot immediately.')
elif idx==2:
    st.header('How to take it')
    panel('◷ Sample written treatment plan',PATIENT['instructions'])
    panel('Important reminders','Apixaban may be taken with or without food. Follow the prescription and ask your pharmacist about unclear instructions. Do not double up, stop early or change the schedule based on this demonstration.')
    st.warning('These doses belong to the fictional teaching case only. This app cannot verify a real prescription or recommend individual dosing.')
elif idx==3:
    st.header('Side effects and safety')
    panel('🛡 What to watch for',PATIENT['side_effects'])
    panel('Contact your healthcare team','New or worsening leg swelling, unusual bruising or bleeding, uncertain doses, new medicines, or unexpected reactions need a healthcare professional’s review. Do not adjust your medicine yourself.')
    st.error('Heavy bleeding, chest pain, difficulty breathing, fainting or stroke-like symptoms may be emergencies. Go to the Red flags step for immediate help instructions.')
elif idx==4:
    st.header('Ask about my medication')
    st.info(f"This assistant knows the **sample record**: {PATIENT['medication']} for {PATIENT['diagnosis']}. It cannot access real health records or diagnose symptoms.")
    st.caption('Try: “What is my medication for?” or “How do I take it?” You can also type your own question. Avoid entering real health information.')
    for m in st.session_state.messages:
        with st.chat_message(m['role']):st.markdown(m['content'])
    prompt=st.chat_input('Type your medication question here…')
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        st.session_state.messages.append({'role':'assistant','content':answer(prompt)})
        st.rerun()
    a,b=st.columns(2)
    with a:
        if st.button('Clear demo chat'):
            st.session_state.messages=[]
            st.rerun()
    with b:
        if st.button('Speak to a person instead',type='primary'):goto(6)
    st.caption('Not a general-purpose AI model. Unknown, ambiguous and individual medical questions are referred to healthcare staff. The keyword checks cannot detect every emergency.')
elif idx==5:
    st.header('Recognize a red flag')
    st.error(EMERGENCY)
    panel('⚠ Emergency examples','Sudden chest pain, trouble breathing, coughing blood, fainting, stroke-like symptoms, severe bleeding, or a serious head injury while taking anticoagulants.')
    st.warning('Do not wait for the chatbot to assess symptoms. It cannot contact a nurse, book emergency care, or determine whether symptoms are harmless.')
elif idx==6:
    st.header('What to do next')
    st.error(EMERGENCY)
    panel('Need advice, but it is not an emergency?',REVIEW)
    panel('Your choice matters','You can always speak to a nurse, doctor or pharmacist instead of using this assistant. No messages, alerts, or appointments are sent by this demonstration.')

st.divider()
left,right=st.columns(2)
with left:
    if st.button('← Previous step',disabled=idx==0):goto(idx-1)
with right:
    if st.button('Next step →',type='primary',disabled=idx==len(STEPS)-1):goto(idx+1)
st.caption('Medical content: Saeed’s sample DVT case. Human handoff and privacy approach: Ali’s principles. Visual direction: Hessa’s MediConnect design. All responses require clinical review before real-world use.')
