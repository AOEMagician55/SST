import streamlit as st
import random

st.set_page_config(page_title="Turn-Based Fighting Game", layout="centered")
st.title("⚔️ Turn-Based Fighting Game")

MAX_ENERGY = 100
MAX_ATTACK_BUFF = 0.50
MAX_DEFENSE_CAP = 80

# ---------------- HERO & ENEMY DATA ----------------
HEROES = {
    "67 Kid": {
        "hp": 620,
        "dmg": (12, 22),
        "ability": "Brainrot Infection",
        "ability_description": "Deals 15 damage over 3 turns. Does not stack. 30 energy.",
    },
    "Pink": {
        "hp": 650,
        "dmg": (12, 18),
        "ability": "Comfortably Numb",
        "ability_description": "Increase defense by 15 (stacking up to 60). 25 energy.",
    },
    "Crying man": {
        "hp": 450,
        "dmg": (22, 32),
        "ability": "National Fervor",
        "ability_description": "Increase attack by 8% for rest of battle. 30 energy.",
    },
    "Jar jar bing": {  # i





