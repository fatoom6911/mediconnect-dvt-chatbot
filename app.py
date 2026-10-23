"""MediConnect patient-education university demonstration. No clinical service connected."""
import re
from difflib import SequenceMatcher
from datetime import date
import streamlit as st

st.set_page_config(page_title="MediConnect | Healthcare Assistant", page_icon="💙", layout="wide", initial_sidebar_state="collapsed")
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

st.markdown('''<style>
:root {color-scheme:light;}
html,body,.stApp,[data-testid="stAppViewContainer"] {background:#eef5f5!important;color:#163e49!important;}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none!important;}
[data-testid="stHeader"]{background:transparent!important;height:2.7rem!important;}
[data-testid="stToolbar"]{opacity:.7;}
.block-container {max-width:1220px!important;width:100%!important;padding:2.9rem 2.1rem 4rem!important;min-height:100vh;}
*,*:before,*:after{box-sizing:border-box!important;}
[data-testid="stVerticalBlock"], [data-testid="column"], .element-container, .stMarkdown, .stMarkdown div {min-width:0;max-width:100%;}
.stMarkdown p,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {overflow-wrap:anywhere;}
h1,h2,h3,h4,p,label{color:#163e49;}h1{font-size:clamp(1.8rem,3vw,2.8rem)!important;line-height:1.14!important;letter-spacing:-.035em;}h2{font-size:clamp(1.35rem,2vw,1.8rem)!important;}
.hero {background:linear-gradient(125deg,#073c4b,#126b75);border-radius:25px;padding:clamp(24px,4vw,52px);color:#fff;margin:0 0 25px;box-shadow:0 16px 30px #113e4b16;overflow:hidden;}
.hero *{color:white!important;}.hero h1{font-size:clamp(2.2rem,5vw,4.2rem)!important;line-height:1.05!important;max-width:850px;margin:22px 0!important;}.hero p{font-size:clamp(1rem,1.4vw,1.2rem);max-width:750px;line-height:1.6;}
.eyebrow{color:#2a8a91;font-size:.76rem;letter-spacing:.15em;font-weight:800;text-transform:uppercase;margin:16px 0;}
.card {background:#fff;border:1px solid #d8e8e9;border-radius:20px;padding:clamp(18px,2.3vw,30px);margin:7px 0 15px;box-shadow:0 7px 25px #0c3b4710;min-height:125px;overflow-wrap:anywhere;}
.card h3{margin:0 0 12px!important;font-size:clamp(1.05rem,1.6vw,1.3rem)!important;}.card p{font-size:1rem;line-height:1.65;color:#4d707a;margin:0;}
.med {background:linear-gradient(120deg,#0a4553,#146f77);border-radius:22px;padding:30px;color:#fff;overflow-wrap:anywhere;margin-bottom:15px;}.med *{color:white!important;}
.stButton button,.stFormSubmitButton button{min-height:47px!important;width:100%!important;white-space:normal!important;height:auto!important;border-radius:12px!important;border:1px solid #c8dfe2!important;background:#fff!important;color:#124653!important;font-weight:700!important;overflow-wrap:anywhere!important;padding:10px 15px!important;}
.stButton button:hover{border-color:#0c7f87!important;background:#e8f7f5!important;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:#087d84!important;color:#fff!important;border-color:#087d84!important;}
[data-testid="stChatMessage"]{background:white!important;border:1px solid #d9e8ea;border-radius:16px;padding:12px!important;margin:12px 0!important;max-width:100%;overflow-wrap:anywhere;}
[data-testid="stChatInput"]{background:white!important;border:1px solid #95c6c8!important;border-radius:14px!important;}
[data-testid="stAlert"]{border-radius:14px!important;overflow-wrap:anywhere;}
[data-testid="stHorizontalBlock"]{align-items:stretch;}
.small-note{color:#64828a;font-size:.8rem;margin-top:14px;line-height:1.6;}
@media(max-width:700px){.block-container{padding:2.7rem .85rem 4rem!important;}.hero{border-radius:18px;padding:24px 20px;}.card{padding:18px;}.stButton button{font-size:.86rem!important;}.stApp h1{font-size:1.8rem!important;}}
</style>''',unsafe_allow_html=True)

DEFAULTS={'screen':'Welcome','role':'Patient','messages':[],'log':[],'requests':[],'onboarded':False,'journey_step':0}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

EMERGENCY="🚨 **Get emergency help now.** In hospital, press the nurse-call button or alert staff immediately. Outside hospital, call an ambulance (998 in the UAE; otherwise your local emergency number). Do not drive yourself. **This demo has not alerted anyone.**"
REVIEW="This needs advice from a healthcare professional. Contact your care team; if symptoms are new or worsening, seek prompt assessment. **No message has been sent.**"
URGENT=['chest pain','chest hurts','cant breathe','cannot breathe',"can't breathe",'shortness of breath','difficulty breathing','breathless','coughing blood','cough blood','vomit blood','bleeding heavily','uncontrolled bleeding','severe bleeding','fainted','fainting','unconscious','face droop','slurred speech','seizure','tongue swelling','suicidal','kill myself','hit my head','head injury','worst headache','sudden severe headache','severe headache and confused','ألم الصدر','ضيق التنفس','نزيف شديد','إغماء']
REVIEW_TERMS=['my dose','change my dose','stop taking','should i stop','extra dose','missed dose','pregnant','new swelling','more swollen','blood in urine','nosebleed','my results','my blood test','diagnose me','do i have','prescribe','surgery','medication interaction','my headache','i have a headache','i have headache','i feel dizzy','my symptoms','أغير الجرعة','نتائج تحاليلي']
TOPICS={
'dvt':'Deep vein thrombosis (DVT) is a clot in a deep vein, often in a leg. Symptoms may include pain, swelling or warmth. New symptoms should be assessed by a clinician.',
'diabetes':'Diabetes is a condition involving high blood glucose. Care may involve nutrition, activity, monitoring and prescribed treatment, depending on the individual.',
'headache':'A headache is pain or discomfort in the head. Many causes are possible, including tension and migraine. A sudden extremely severe headache, or headache with confusion, weakness, fainting or trouble speaking, needs emergency assessment. New, persistent or worsening headaches need clinical advice.',
'migraine':'Migraine is a neurological condition that can cause recurring headache, sometimes with nausea or sensitivity to light and sound. Diagnosis and treatment are individualized.',
'asthma':'Asthma affects the airways and may cause wheezing, coughing and breathing symptoms. If you are having trouble breathing now, seek emergency help.',
'blood pressure':'Blood pressure measures the force of blood against artery walls. Persistently high readings should be discussed with a clinician, who can interpret them in context.',
'hypertension':'Hypertension means persistently high blood pressure. A clinician can review readings, risk factors and appropriate care.',
'anemia':'Anemia means too little hemoglobin or too few healthy red blood cells. Causes vary and require medical assessment.',
'cholesterol':'Cholesterol is a substance carried in blood. Some cholesterol patterns are associated with cardiovascular risk; clinicians interpret tests alongside other factors.',
'apixaban':'Apixaban (Eliquis) is an anticoagulant used for some blood-clot conditions. It can increase bleeding risk. Do not start, stop or change doses based on this demo.',
'blood thinner':'Blood thinners, or anticoagulants, reduce blood clotting. They can prevent clots growing and new clots forming but may increase bleeding risk.',
'pulmonary embolism':'Pulmonary embolism is a clot blocking a lung blood vessel. Sudden chest pain, breathing difficulty or fainting requires emergency help.',
'fever':'Fever means body temperature is higher than usual and can have several causes. New or persistent fever needs clinical advice, especially with concerning symptoms.',
'cold':'A common cold is a viral infection of the upper respiratory tract. It often causes a runny nose, sore throat or cough. Worsening or concerning symptoms need clinical review.',
'allergy':'An allergy is an immune response to a substance. Severe swelling of the tongue or difficulty breathing requires emergency help.',
'paracetamol':'Paracetamol (acetaminophen) is a medicine used for pain and fever. The safe amount depends on the product and individual circumstances; ask a pharmacist for personal dosing advice.',
}
ALIASES={'head ache':'headache','hedache':'headache','headach':'headache','headche':'headache','dvr':'dvt','dv t':'dvt','diabtes':'diabetes','diabetis':'diabetes','blood thiner':'blood thinner','ashtma':'asthma','apixban':'apixaban'}

def clean(t): return re.sub(r'[^a-z0-9\u0600-\u06ff ]',' ',t.lower()).strip()
def contains(text,phrase):
    return bool(re.search(r'(?<!\w)'+re.escape(clean(phrase))+r'(?!\w)',text))
def answer(q):
    t=clean(q)
    for wrong,right in ALIASES.items():t=re.sub(r'(?<!\w)'+re.escape(wrong)+r'(?!\w)',right,t)
    if any(contains(t,w) for w in URGENT):return EMERGENCY
    if any(contains(t,w) for w in REVIEW_TERMS):return REVIEW
    if any(x in t for x in ['what is my medication for','what is my medicine for','why am i taking it','why do i take it','what does my medicine do']):
        return 'Your listed medication is apixaban (Eliquis) for DVT. It helps prevent the clot from growing and reduces the risk of new clots.'
    if any(x in t for x in ['what is my medication','what is my medicine','which medication am i taking','what medication am i taking']):
        return 'The sample patient record lists apixaban (Eliquis), an anticoagulant prescribed for DVT.'
    if any(x in t for x in ['how do i take my medicine','how do i take it','how to take my medication']):
        return 'In Fatima Ahmed’s sample case, the documented plan is 10 mg twice daily for seven days, then 5 mg twice daily from day eight. This is not a prescription for anyone else. Check your own written instructions with your clinician or pharmacist.'
    # A question about a symptom personally experienced is never treated as general education.
    if re.search(r'\b(i have|i feel|my symptoms|i am experiencing|i m having)\b',t):return REVIEW
    for term in sorted(TOPICS,key=len,reverse=True):
        if contains(t,term):return TOPICS[term]
    # A limited, conservative typo match for known topic names only.
    tokens=t.split()
    for token in tokens:
        if len(token)>4:
            near=max(TOPICS,key=lambda k:SequenceMatcher(None,token,k).ratio())
            if SequenceMatcher(None,token,near).ratio()>.86:return TOPICS[near]
    # Saeed's case questions: only answer exact or very close education questions.
    for item in BANK:
        if item['category']=='education' and SequenceMatcher(None,t,clean(item['question'])).ratio()>.91:
            return 'In the example patient plan: '+item['answer']
    return "I don't have a reviewed answer for that question. I can explain general topics such as headache, DVT, diabetes, asthma, blood pressure and medicines. For symptoms, personal results or treatment decisions, please ask a healthcare professional."

def go(page):st.session_state.screen=page;st.rerun()
def card(title,desc):
    st.markdown('<div class="card"><h3>'+title+'</h3><p>'+desc+'</p></div>',unsafe_allow_html=True)
def hero(eyebrow,title,desc):
    st.markdown(f'<div class="hero"><div class="eyebrow" style="color:#9ee2e0">{eyebrow}</div><h1>{title}</h1><p>{desc}</p></div>',unsafe_allow_html=True)
def heading(title,subtitle=''):
    st.markdown('<div class="eyebrow">MEDICONNECT · HEALTHCARE ASSISTANT</div>',unsafe_allow_html=True)
    st.title(title)
    if subtitle:st.caption(subtitle)
def navigation():
    st.divider()
    cols=st.columns(5)
    for c,label,page in zip(cols,['⌂ Home','♡ Journey','💊 Meds','🛡 Safety','💬 Chat'],['Dashboard','Journey','Medication','Safety','Chat']):
        with c:
            if st.button(label,key='nav_'+page):go(page)

def two_card_actions(items):
    for pair_start in range(0,len(items),2):
        cols=st.columns(2,gap='large')
        for col,item in zip(cols,items[pair_start:pair_start+2]):
            with col:
                title,desc,target=item
                card(title,desc)
                if st.button('Open '+title.split(' ',1)[-1]+' →',key='tile_'+target,use_container_width=True):go(target)

page=st.session_state.screen
if page=='Journey':
    heading('My medication journey','Fatima Ahmed · Apixaban (Eliquis) · Patient education')
    steps=['My medication','What it is for','How to take it','Side effects','Ask a question','Red flags','What to do next']
    st.progress((st.session_state.journey_step+1)/7,text=f"Step {st.session_state.journey_step+1} of 7")
    j=st.session_state.journey_step
    if j==0:
        card('💊 Apixaban (Eliquis)','Medication listed in Fatima Ahmed’s sample treatment plan for deep vein thrombosis (DVT).')
    elif j==1:
        card('Why this medication is prescribed','Apixaban is an anticoagulant. It helps prevent the existing clot from growing and reduces the risk of new clots. It does not dissolve the clot immediately.')
    elif j==2:
        card('Documented treatment plan','For this teaching case, the written plan is 10 mg twice daily for seven days, followed by 5 mg twice daily from day eight. These are case details, not instructions for other patients.')
        st.warning('Follow only your own verified prescription. Do not change medication based on this demo.')
    elif j==3:
        card('Side effects and precautions','Bleeding is an important risk with apixaban. New unusual bleeding, bruising or swelling should be discussed promptly with a healthcare professional.')
    elif j==4:
        st.info('The assistant uses the same sample medication information shown in this journey. It is a limited educational chatbot, not a clinical service.')
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):st.markdown(msg['content'])
        prompt=st.chat_input('Ask about my medication...')
        if prompt:
            st.session_state.messages.append({'role':'user','content':prompt})
            st.session_state.messages.append({'role':'assistant','content':answer(prompt)})
            st.rerun()
        if st.button('Clear conversation',key='journey_clear'):st.session_state.messages=[];st.rerun()
    elif j==5:
        st.error(EMERGENCY)
        card('Recognize red flags','Chest pain, difficulty breathing, coughing blood, fainting, stroke-like symptoms, major bleeding, or head injury while taking anticoagulants require immediate help.')
    else:
        st.error(EMERGENCY)
        st.info(REVIEW)
        card('Human help','In hospital, use the bedside nurse-call button or tell staff. Outside hospital, contact your care team. This demonstration does not send alerts or messages.')
    back,next_=st.columns(2)
    with back:
        if st.button('← Previous step',disabled=j==0,key='journey_prev'):
            st.session_state.journey_step-=1;st.rerun()
    with next_:
        if st.button('Next step →' if j<6 else 'Return to dashboard',type='primary',key='journey_next'):
            if j<6:st.session_state.journey_step+=1;st.rerun()
            else:go('Dashboard')
    if st.button('⌂ Patient dashboard',key='journey_home'):go('Dashboard')
elif page=='Welcome':
    hero('PATIENT EDUCATION, MADE PERSONAL','Clearer care.<br>Closer connections.','Understand your treatment, find educational information and know when to reach your healthcare team.')
    heading('Welcome to your care portal','Choose how you would like to explore the experience.')
    a,b=st.columns(2,gap='large')
    with a:
        card('♡ Continue as Patient','View treatment information, medications, safety guidance and the healthcare assistant.')
        if st.button('Continue as Patient →',type='primary'):st.session_state.role='Patient';go('Sign in')
    with b:
        card('♧ Healthcare Professional','Explore the clinical oversight and patient education demonstration.')
        if st.button('Healthcare Professional →'):st.session_state.role='Professional';go('Sign in')
    st.caption('University prototype · Demonstration accounts only · No real patient services.')
elif page=='Sign in':
    hero('SECURE ACCESS · SIMULATED','Your care, in one place.','Explore the sample patient portal without creating an account.')
    heading('Sign in to continue','This is a simulated sign-in. No password or real personal information is needed.')
    st.text_input('Demo account',value='Fatima Ahmed · Patient demonstration' if st.session_state.role=='Patient' else 'Healthcare professional · Demonstration',disabled=True)
    if st.button('Enter portal →',type='primary'):go('Dashboard' if st.session_state.role=='Patient' else 'Professional')
    if st.button('← Back'):go('Welcome')
elif page=='Dashboard':
    heading('Welcome back, Fatima Ahmed!','Your treatment overview · Medication journey')
    st.markdown('<div class="med"><div class="eyebrow" style="color:#b9e9e9">CURRENT TREATMENT PLAN</div><h2>💊 Apixaban (Eliquis)</h2><p>Deep vein thrombosis · Left popliteal vein</p><p>Prescribed course: at least 3 months, followed by clinical review.</p></div>',unsafe_allow_html=True)
    st.subheader('Your medication journey')
    st.write('Follow your treatment information in order: medication, purpose, instructions, side effects, questions, red flags and next steps.')
    if st.button('Start my medication journey →',type='primary',key='start_journey'):st.session_state.journey_step=0;go('Journey')
    st.subheader('Other patient sections')
    two_card_actions([('♡ My Diagnosis','Understand DVT and the case background.','Diagnosis'),('💊 My Medication','Review apixaban and the treatment timeline.','Medication'),('📋 Medication Instructions','Understand how to follow a written treatment plan.','Instructions'),('🛡 Side Effects & Safety','Know when to seek professional or emergency help.','Safety'),('💬 Ask AI Assistant','Type your own medical education questions.','Chat'),('✉ Healthcare Team Messages','Explore the demonstration inbox.','Messages'),('🗓 Book Appointment','Prepare a sample appointment request.','Appointments'),('📝 Medication Log','Try a sample medication tracker.','Log')])
    st.error('Emergency symptoms? Alert staff or call emergency services (UAE ambulance: 998). This app does not send alerts.')
    navigation()
elif page=='Diagnosis':
    heading('My Diagnosis','Deep vein thrombosis · Patient education')
    two_card_actions([('♡ What is DVT?','A clot in a deep vein, commonly in the leg.','Chat'),('💊 My Treatment','Anticoagulants help prevent clot growth.','Medication')])
    card('Understanding the diagnosis','In the example patient record, ultrasound confirms a clot in the left popliteal vein. Symptoms included calf swelling, pain and warmth after a long flight.')
    card('Why treatment matters','A clot may lead to complications including pulmonary embolism. Treatment and follow-up are planned by the treating team.')
    navigation()
elif page in ('Medication','Instructions'):
    heading('My Medication','Apixaban (Eliquis) · Treatment education')
    st.markdown('<div class="med"><h2>💊 Apixaban</h2><p>Helps reduce clot growth and prevent new clots forming.</p></div>',unsafe_allow_html=True)
    a,b=st.columns(2,gap='large')
    with a:card('Days 1–7 · Example plan','10 mg twice daily using two 5 mg tablets per dose, as documented in the case.')
    with b:card('Day 8 onward · Example plan','5 mg twice daily using one 5 mg tablet per dose, as documented in the case.')
    card('Clinical review','Treatment is planned for at least three months with clinician review before any decision to stop. The timing and doses shown are case details, not instructions for other patients.')
    st.warning('Never start, stop or change medication using this demonstration. Follow your own verified prescription.')
    if st.button('View side effects and safety →',type='primary'):go('Safety')
    navigation()
elif page=='Safety':
    heading('Side Effects & Safety','Know when to get help')
    a,b=st.columns(2,gap='large')
    with a:card('✓ General education','Follow the prescription, inform clinicians and dentists about anticoagulants, and ask a pharmacist before new medicines.')
    with b:card('! Contact your care team','New swelling, unusual bleeding, uncertain doses or medication interactions need professional review.')
    st.warning('For new or worsening symptoms, seek prompt clinical assessment. No message is sent by this app.')
    st.error(EMERGENCY)
    if st.button('Speak to a person →',type='primary'):go('Help')
    navigation()
elif page=='Chat':
    heading('Ask AI Assistant','Ask your question in your own words')
    st.info('Medical education demo with prepared answers, not a general-purpose AI model. It cannot diagnose, prescribe or reliably detect every emergency.')
    st.caption('Please do not enter real patient information, test results, ID numbers or medical records.')
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):st.markdown(msg['content'])
    prompt=st.chat_input('Type your medical education question here…')
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        st.session_state.messages.append({'role':'assistant','content':answer(prompt)})
        st.rerun()
    a,b=st.columns(2)
    with a:
        if st.button('Clear chat'):st.session_state.messages=[];st.rerun()
    with b:
        if st.button('Speak to a person'):go('Help')
    st.caption('No one is monitoring this chat. For urgent symptoms, seek human help immediately.')
    navigation()
elif page=='Appointments':
    heading('Appointments','Prepare a demonstration appointment request')
    st.info('Try the form to see a sample confirmation. This is not a real booking; no clinic receives the request.')
    with st.form('appointment_form'):
        service=st.selectbox('Appointment type',['DVT follow-up','Medication counselling','General medical consultation'])
        when=st.date_input('Preferred date',min_value=date.today())
        period=st.selectbox('Preferred time',['Morning','Afternoon','Evening'])
        submit=st.form_submit_button('Create sample appointment request',type='primary')
    if submit:
        st.session_state.requests.append({'service':service,'date':str(when),'time':period})
        st.success(f'Sample request created: {service} · {when} · {period}. NOT BOOKED — no clinic has received this.')
    if st.session_state.requests:
        st.subheader('Your sample requests')
        for item in st.session_state.requests:
            card(item['service'],item['date']+' · '+item['time']+' · Not sent / not booked')
        if st.button('Clear sample requests'):st.session_state.requests=[];st.rerun()
    navigation()
elif page=='Messages':
    heading('Healthcare Team Messages','Sample inbox')
    card('No new messages','A future hospital-connected version could show verified messages from your care team. This demo cannot send or receive messages.')
    if st.button('How to contact staff →',type='primary'):go('Help')
    navigation()
elif page=='Log':
    heading('Medication Log','Practice tracking with sample data')
    status=st.selectbox('Sample entry',['Taken','Not taken','Unsure'])
    if st.button('Save practice entry',type='primary'):st.session_state.log.append(status);st.success('Practice entry saved in this session. No clinician notified.')
    for i,item in enumerate(st.session_state.log,1):st.write(f'Entry {i}: {item}')
    if st.button('Clear log'):st.session_state.log=[];st.rerun()
    navigation()
elif page=='Help':
    heading('Speak to a person','Human help is always an option')
    st.error(EMERGENCY)
    st.info(REVIEW)
    st.write('In hospital, contact a nurse, doctor or pharmacist. Outside hospital, contact your own healthcare provider. No request has been sent.')
    if st.button('Return to dashboard →',type='primary'):go('Dashboard')
    navigation()
elif page=='Professional':
    heading('Healthcare Professional','Clinical oversight and patient education')
    card('Patient case overview','Fatima Ahmed, age 46, with ultrasound-confirmed left popliteal DVT in the sample case. Apixaban and follow-up were documented by the fictional care team.')
    card('Human oversight','The assistant must not diagnose, adjust doses, interpret individual results or claim messages were sent. Clinical staff retain responsibility.')
    st.subheader('Saeed’s 48 patient questions')
    category=st.selectbox('Category',['Education','Clinician review','Immediate assessment'])
    cat={'Education':'education','Clinician review':'review','Immediate assessment':'urgent'}[category]
    for item in BANK:
        if item['category']==cat:
            with st.expander(f"{item['number']}. {item['question']}"):
                st.write(item['answer'])
                st.caption('Proposed case response; clinical review required before real use.')
    navigation()
