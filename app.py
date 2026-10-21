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
