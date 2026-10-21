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
