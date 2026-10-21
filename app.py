import streamlit as st

st.set_page_config(page_title='MediConnect | DVT Education', page_icon='💙', layout='centered')
st.markdown('''<style>
.stApp {background-color:#f4f8f8;color:#153f48;}
.block-container {max-width:740px;padding-top:2rem;}
h1,h2,h3 {color:#104e5a;}
.stButton > button {border-radius:14px;background:#0d5865;color:white;border:0;}
[data-testid="stSidebar"] {background:#e9f3f4;}
</style>''', unsafe_allow_html=True)
st.title('MediConnect')
st.caption('Clearer care. Closer connections. | Educational prototype')
st.warning('University demonstration only. Do not enter real patient information. This is not a clinical service or emergency monitoring system.')
page = st.sidebar.radio('Explore', ['Welcome', 'DVT Education', 'Ask a Question', 'Healthcare Professional'])

if page == 'Welcome':
    st.header('Welcome to your care portal')
    st.write('Choose a section from the sidebar to explore the prototype.')
    st.info('Patient education, made personal. This version uses prepared responses, not generative AI.')
elif page == 'DVT Education':
    st.header('Understanding DVT')
    st.write('Deep vein thrombosis (DVT) is a blood clot in a deep vein, most often in a leg.')
    st.subheader('About anticoagulants')
    st.write('Anticoagulant medicines can help prevent a clot from growing and reduce the chance of new clots forming. Follow the instructions from your healthcare team.')
    st.info('Content here is placeholder educational material. Replace it with Saeed’s reviewed answers before project evaluation.')
elif page == 'Ask a Question':
    st.header('Ask about DVT')
    st.caption('This is a limited, rule-based demonstration and cannot assess symptoms.')
    q = st.text_input('Type your question (no personal information)')
    if st.button('Send') and q.strip():
        lower = q.lower()
        red_flags = ['chest pain', 'shortness of breath', 'difficulty breathing', 'coughing blood', 'fainting']
        if any(x in lower for x in red_flags):
            st.error('Possible emergency: seek emergency medical assistance immediately. Do not rely on this chatbot.')
        elif 'what is dvt' in lower or 'deep vein thrombosis' in lower:
            st.write('DVT is a blood clot in a deep vein, most often in a leg.')
        elif 'blood thinner' in lower or 'anticoagulant' in lower:
            st.write('Anticoagulants help prevent clots from growing and new clots from forming. Follow your prescribed treatment plan.')
        else:
            st.info('I do not have a reviewed answer to that question. Please consult a qualified healthcare professional. If symptoms may be urgent, seek prompt medical care.')
    st.caption('Safety note: Keyword checks can miss serious symptoms and must not be used for real patient triage.')
else:
    st.header('Healthcare Professional')
    st.write('Demonstration placeholder. No patient records, accounts, or clinical messaging are connected.')
