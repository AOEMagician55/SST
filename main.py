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
    "Jar jar bing": {  # intentionally broken
        "hp": 1000,
        "dmg": (7, 10),
        "ability": "BigHard",
        "ability_description": "5% chance to deal 1000 damage. 20 energy.",
    }
}

ENEMIES = {
    "Goblin": {"hp": 120, "dmg": (10, 18)},
    "Orc": {"hp": 320, "dmg": (15, 25)},
    "Dragon": {"hp": 1100, "dmg": (15, 50)},
}

# ---------------- CHARACTER SELECTION ----------------
if "game_started" not in st.session_state:
    hero_choice = st.selectbox("Hero", HEROES.keys())
    enemy_choice = st.selectbox("Enemy", ENEMIES.keys())

    if st.button("Start Battle"):
        st.session_state.update({
            "hero_name": hero_choice,
            "enemy_name": enemy_choice,
            "player_hp": HEROES[hero_choice]["hp"],
            "enemy_hp": ENEMIES[enemy_choice]["hp"],
            "player_energy": 100,
            "enemy_energy": 50,
            "player_combo": 0,
            "enemy_combo": 0,
            "player_rest_streak": 0,
            "player_rest_penalty": False,
            "player_defense": 0,      # PERMANENT (Pink only)
            "temp_defense": 0,        # TEMP (everyone)
            "enemy_defense": 0,
            "temp_enemy_defense": 0,  # TEMP enemy defense
            "player_attack_buff": 0.0,
            "brainrot_active": False,
            "brainrot_turns": 0,
            "turn_log": [],
            "game_over": False,
            "game_started": True,
        })
        st.rerun()

# ---------------- GAME ----------------
if st.session_state.get("game_started"):
    s = st.session_state
    hero = HEROES[s.hero_name]
    enemy_data = ENEMIES[s.enemy_name]

    # Brainrot DOT
    if s.brainrot_active and s.brainrot_turns > 0:
        dmg = max(0, 15 - s.enemy_defense)
        s.enemy_hp -= dmg
        s.brainrot_turns -= 1
        s.turn_log.append(f"Brainrot deals {dmg} damage ({s.brainrot_turns} turns left)")
        if s.brainrot_turns == 0:
            s.brainrot_active = False

    # -------- UI --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(s.hero_name)
        st.write(f"HP: {s.player_hp}")
        st.write(f"Energy: {s.player_energy}")
        st.write(f"Defense: {s.player_defense}")
        st.write(f"Temp Defense: {s.temp_defense}")
        st.write(f"Attack Buff: {s.player_attack_buff*100:.0f}%")

    with col2:
        st.subheader(s.enemy_name)
        st.write(f"HP: {s.enemy_hp}")
        st.write(f"Defense: {s.enemy_defense}")
        st.write(f"Temp Defense: {s.temp_enemy_defense}")

    st.divider()

    # ---------------- Enemy Turn ----------------
    def enemy_turn(player_defended=False):
        action = "rest" if s.enemy_energy < 20 else random.choice(
            ["attack", "attack", "defend", "rest"]
        )

        if action == "attack":
            base = random.randint(*enemy_data["dmg"])
            dmg = int(base * (1 + s.enemy_combo * 0.10))

            effective_defense = min(
                s.player_defense + s.temp_defense, MAX_DEFENSE_CAP
            )
            dmg = max(0, dmg - effective_defense)

            if player_defended:
                dmg //= 2

            s.player_hp -= dmg
            s.enemy_energy -= 20
            s.enemy_combo += 1
            s.temp_defense = 0
            s.turn_log.append(f"{s.enemy_name} attacks for {dmg} damage!")

        elif action == "defend":
            s.enemy_energy -= 10
            s.enemy_combo = 0
            s.temp_enemy_defense = 10   # 🔒 UNSTACKABLE
            s.turn_log.append(f"{s.enemy_name} defends (+10 defense for 1 turn)")

        else:
            s.enemy_energy = min(MAX_ENERGY, s.enemy_energy + 30)
            s.enemy_combo = 0
            s.turn_log.append(f"{s.enemy_name} rests.")

    # ---------------- Player Actions ----------------
    if not s.game_over:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Attack"):
                base = random.randint(*hero["dmg"])
                dmg = base * (1 + s.player_combo * 0.10)
                dmg *= (1 + s.player_attack_buff)

                dmg = max(
                    0,
                    int(dmg - (s.enemy_defense + s.temp_enemy_defense))
                )

                s.temp_enemy_defense = 0  # reset enemy defense
                s.enemy_hp -= dmg
                s.player_energy -= 20
                s.player_combo += 1
                s.player_attack_buff = min(
                    s.player_attack_buff + 0.05, MAX_ATTACK_BUFF
                )

                s.turn_log.append(f"You attack for {dmg} damage!")
                enemy_turn()

        with col2:
            if st.button("Defend"):
                s.player_energy -= 10
                s.player_combo = 0
                s.temp_defense = 20       # 🔒 UNSTACKABLE
                s.turn_log.append("You defend (+20 defense for 1 turn)")
                enemy_turn(player_defended=True)

        with col3:
            if st.button("Rest"):
                s.player_energy = min(MAX_ENERGY, s.player_energy + 30)
                s.player_combo = 0
                s.turn_log.append("You rest.")
                enemy_turn()

        with col4:
            if st.button(hero["ability"]):
                if hero["ability"] == "Comfortably Numb":
                    s.player_energy -= 25
                    s.player_defense = min(s.player_defense + 15, 60)  # ✅ ONLY PINK
                    s.turn_log.append("Pink hardens defenses!")
                    enemy_turn()

                elif hero["ability"] == "Brainrot Infection":
                    s.player_energy -= 30
                    s.brainrot_active = True
                    s.brainrot_turns = 3
                    s.turn_log.append("Brainrot applied!")
                    enemy_turn()

                elif hero["ability"] == "National Fervor":
                    s.player_energy -= 30
                    s.player_attack_buff = min(
                        s.player_attack_buff + 0.08, MAX_ATTACK_BUFF
                    )
                    s.turn_log.append("Crying Man rallies!")
                    enemy_turn()

                elif hero["ability"] == "BigHard":
                    s.player_energy -= 20
                    if random.random() <= 0.05:
                        s.enemy_hp -= 1000
                        s.turn_log.append("💥 BIGHARD CRITICAL!")
                    else:
                        s.turn_log.append("BigHard missed.")
                    enemy_turn()

    # ---------------- End ----------------
    if s.player_hp <= 0:
        s.game_over = True
        st.error("You lost!")

    if s.enemy_hp <= 0:
        s.game_over = True
        st.success("Victory!")

    st.subheader("Battle Log")
    for log in reversed(s.turn_log[-8:]):
        st.write(log)

    if s.game_over and st.button("Restart"):
        st.session_state.clear()
        st.rerun()




