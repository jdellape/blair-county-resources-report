import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(st.secrets["firebase"].to_dict())
        firebase_admin.initialize_app(cred)

    return firestore.client()
