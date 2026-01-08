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
        "Character description": "The person who created the 67 virus.",
    },
    "Pink": {
        "hp": 650,
        "dmg": (12, 18),
        "ability": "Comfortably Numb",
        "ability_description": "Increase defense by 15 (stacking up to 60). 25 energy.",
        "Character description": "Ultra-powerful numbing pills are given to every employee for efficiency.",
    },
    "Crying man": {
        "hp": 450,
        "dmg": (22, 32),
        "ability": "National Fervor",
        "ability_description": "Increase attack by 8% for rest of battle. 5% crit. 30 energy.",
        "Character description": "Very patriotic, will defend his country, even cries at national anthems.",
    },
    "Jar jar bing": {  # UNCHANGED (INTENTIONALLY BROKEN)
        "hp": 1000,
        "dmg": (7, 10),
        "ability": "BigHard",
        "ability_description": "5% chance to deal 1000 damage. 20 energy.",
        "Character description": "We can't afford the star wars ip, so we got jar jar's brother to help us out.",
    }
}

ENEMIES = {
    "Goblin": {"hp": 120, "dmg": (10, 18)},
    "Orc": {"hp": 320, "dmg": (15, 25)},
    "Dragon": {"hp": 1100, "dmg": (15, 50)},
}

# ---------------- CHARACTER SELECTION ----------------
if "game_started" not in st.session_state:
    st.subheader("Choose Your Hero")
    hero_choice = st.selectbox("Hero", HEROES.keys())

    st.subheader("Choose Enemy")
    enemy_choice = st.selectbox("Enemy", ENEMIES.keys())

    if st.button("Start Battle"):
        hero = HEROES[hero_choice]
        enemy = ENEMIES[enemy_choice]

        st.session_state.update({
            "hero_name": hero_choice,
            "enemy_name": enemy_choice,
            "player_hp": hero["hp"],
            "enemy_hp": enemy["hp"],
            "player_energy": 100,
            "enemy_energy": 50,
            "player_combo": 0,
            "enemy_combo": 0,
            "player_rest_streak": 0,
            "player_rest_penalty": False,
            "enemy_stunned": False,
            "player_defense": 0,
            "enemy_defense": 0,
            "player_attack_buff": 0.0,
            "brainrot_active": False,
            "brainrot_turns": 0,
            "temp_defense": 0,
            "turn_log": [],
            "game_over": False,
            "game_started": True,
        })
        st.rerun()

# ---------------- GAME ----------------
if st.session_state.get("game_started"):
    hero = HEROES[st.session_state.hero_name]
    enemy_data = ENEMIES[st.session_state.enemy_name]
    s = st.session_state

    # Apply Brainrot Infection
    if s.brainrot_active and s.brainrot_turns > 0:
        dmg = max(0, 15 - s.enemy_defense)
        s.enemy_hp -= dmg
        s.brainrot_turns -= 1
        s.turn_log.append(
            f"Brainrot Infection deals {dmg} damage. ({s.brainrot_turns} turns left)"
        )
        if s.brainrot_turns == 0:
            s.brainrot_active = False

    # -------- Display Stats --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🧍 {s.hero_name}")
        st.write(f"❤️ HP: {s.player_hp}")
        st.write(f"🔋 Energy: {s.player_energy}")
        st.write(f"🔥 Combo: {s.player_combo}")
        st.write(f"🛡️ Defense: {s.player_defense}")
        st.write(f"🛡️ Temp Defense: {s.temp_defense}")
        st.write(f"⚔️ Attack Buff: {s.player_attack_buff*100:.0f}%")

    with col2:
        st.subheader(f"👹 {s.enemy_name}")
        st.write(f"❤️ HP: {s.enemy_hp}")
        st.write(f"🔋 Energy: {s.enemy_energy}")
        st.write(f"🔥 Combo: {s.enemy_combo}")
        st.write(f"🛡️ Defense: {s.enemy_defense}")

    st.divider()

    # ---------------- Enemy Turn ----------------
    def enemy_turn(player_defended=False):
        if s.enemy_stunned:
            s.turn_log.append(f"{s.enemy_name} is stunned and skips the turn!")
            s.enemy_stunned = False
            return

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

            s.enemy_energy -= 20
            s.player_hp -= dmg
            s.enemy_combo += 1
            s.turn_log.append(f"{s.enemy_name} attacks for {dmg} damage!")

            s.temp_defense = 0  # expires after 1 turn

        elif action == "defend":
            s.enemy_energy -= 10
            s.enemy_combo = 0
            s.enemy_defense += 10
            s.turn_log.append(f"{s.enemy_name} defends. (+10 defense)")

        else:
            s.enemy_energy = min(MAX_ENERGY, s.enemy_energy + 30)
            s.enemy_combo = 0
            s.turn_log.append(f"{s.enemy_name} rests.")

    # ---------------- Player Actions ----------------
    if not s.game_over:
        col1, col2, col3, col4 = st.columns(4)

        # ATTACK
        with col1:
            if st.button("⚔️ Attack"):
                if s.player_energy < 20:
                    st.warning("Not enough energy!")
                else:
                    base = random.randint(*hero["dmg"])
                    dmg = base * (1 + s.player_combo * 0.10)
                    dmg *= (1 + s.player_attack_buff)

                    if random.random() <= 0.05:
                        dmg *= 2
                        s.turn_log.append("💥 CRITICAL HIT!")

                    dmg = max(0, int(dmg - s.enemy_defense))

                    if s.player_rest_penalty:
                        dmg = int(dmg * 0.75)
                        s.turn_log.append("⚠️ Rest penalty applied!")
                        s.player_rest_penalty = False

                    s.player_energy -= 20
                    s.enemy_hp -= dmg
                    s.player_combo += 1
                    s.player_rest_streak = 0

                    s.player_attack_buff = min(
                        s.player_attack_buff + 0.05, MAX_ATTACK_BUFF
                    )

                    s.turn_log.append(f"You attack for {dmg} damage!")
                    enemy_turn()

        # DEFEND (NERFED)
        with col2:
            if st.button("🛡️ Defend"):
                if s.player_energy < 10:
                    st.warning("Not enough energy!")
                else:
                    s.player_energy -= 10
                    s.player_combo = 0
                    s.player_rest_streak = 0
                    s.temp_defense = 20
                    s.turn_log.append("You defend. (+20 defense for 1 turn)")
                    enemy_turn(player_defended=True)

        # REST
        with col3:
            if st.button("😴 Rest"):
                s.player_energy = min(MAX_ENERGY, s.player_energy + 30)
                s.player_combo = 0
                s.player_rest_streak += 1
                if s.player_rest_streak >= 2:
                    s.player_rest_penalty = True
                s.turn_log.append("You rest.")
                enemy_turn()

        # HERO ABILITY
        with col4:
            if st.button(f"✨ {hero['ability']}"):

                if hero["ability"] == "Brainrot Infection" and s.player_energy >= 30:
                    s.player_energy -= 30
                    s.brainrot_active = True
                    s.brainrot_turns = 3
                    s.turn_log.append("67 Kid used Brainrot Infection!")
                    enemy_turn()

                elif hero["ability"] == "Comfortably Numb" and s.player_energy >= 25:
                    s.player_energy -= 25
                    s.player_defense = min(s.player_defense + 15, 60)
                    s.turn_log.append(
                        f"Pink used Comfortably Numb! Defense: {s.player_defense}"
                    )
                    enemy_turn()

                elif hero["ability"] == "National Fervor" and s.player_energy >= 30:
                    s.player_energy -= 30
                    s.player_attack_buff = min(
                        s.player_attack_buff + 0.08, MAX_ATTACK_BUFF
                    )
                    s.turn_log.append(
                        f"Crying Man used National Fervor! Attack buff: {s.player_attack_buff*100:.0f}%"
                    )
                    enemy_turn()

                elif hero["ability"] == "BigHard" and s.player_energy >= 20:
                    s.player_energy -= 20
                    if random.random() <= 0.05:
                        s.enemy_hp -= 1000
                        s.turn_log.append("💥 BigHard CRITICAL! 1000 damage!")
                    else:
                        s.turn_log.append("BigHard failed to crit.")
                    enemy_turn()

    # ---------------- End Conditions ----------------
    if s.player_hp <= 0:
        s.game_over = True
        st.error("💀 You were defeated!")

    if s.enemy_hp <= 0:
        s.game_over = True
        st.success("🏆 Victory!")

    # ---------------- Battle Log ----------------
    st.divider()
    st.subheader("📜 Battle Log")
    for log in reversed(s.turn_log[-8:]):
        st.write(log)

    # ---------------- Restart ----------------
    if s.game_over and st.button("🔄 Back to Select"):
        st.session_state.clear()
        st.rerun()





