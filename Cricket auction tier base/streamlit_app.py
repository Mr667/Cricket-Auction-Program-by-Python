import streamlit as st
import random
import pandas as pd
import time
import streamlit.components.v1 as components
import re

def render_timer(remaining_seconds):
    timer_html = """
    <div id="timer-container" style="
        background-color: #1e1e24;
        border-radius: 12px;
        padding: 12px 20px;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #333;
        margin-bottom: 20px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #bbb; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; display: flex; align-items: center; gap: 6px;">
                ⏱️ BIDDING TIME REMAINING
            </span>
            <span id="timer-text" style="color: #00ffcc; font-size: 24px; font-weight: 800; font-variant-numeric: tabular-nums; text-shadow: 0 0 10px rgba(0,255,204,0.3);">02:00</span>
        </div>
        <div style="background-color: #2b2b36; height: 8px; border-radius: 4px; overflow: hidden; width: 100%;">
            <div id="timer-bar" style="background: linear-gradient(90deg, #00ffcc, #0099ff); height: 100%; width: 100%; transition: width 1s linear, background-color 0.5s;"></div>
        </div>
        <audio id="buzzer" src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" preload="auto"></audio>
    </div>

    <script>
        (function() {
            let timeLeft = REMAINING_SECONDS;
            const totalDuration = 120; // 2 minutes (120 seconds)
            const timerText = document.getElementById('timer-text');
            const timerBar = document.getElementById('timer-bar');
            const buzzer = document.getElementById('buzzer');
            
            function updateTimer() {
                if (timeLeft <= 0) {
                    timerText.innerText = "🚨 TIME'S UP!";
                    timerText.style.color = "#ff4d4d";
                    timerText.style.textShadow = "0 0 10px rgba(255,77,77,0.5)";
                    timerBar.style.width = "0%";
                    timerBar.style.background = "#ff4d4d";
                    
                    // Play buzzer when hitting exactly 0
                    if (timeLeft === 0) {
                        buzzer.play().catch(e => console.log("Audio play blocked. Play requires user interaction first."));
                    }
                    timeLeft = -1;
                    return;
                }
                
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                timerText.innerText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                const percentage = (timeLeft / totalDuration) * 100;
                timerBar.style.width = `${percentage}%`;
                
                // Color and style updates based on remaining time
                if (timeLeft > 60) {
                    timerText.style.color = "#00ffcc";
                    timerText.style.textShadow = "0 0 10px rgba(0,255,204,0.3)";
                    timerBar.style.background = "linear-gradient(90deg, #00ffcc, #0099ff)";
                } else if (timeLeft > 20) {
                    timerText.style.color = "#ffcc00";
                    timerText.style.textShadow = "0 0 10px rgba(255,204,0,0.3)";
                    timerBar.style.background = "linear-gradient(90deg, #ffcc00, #ff6600)";
                } else {
                    timerText.style.color = "#ff4d4d";
                    timerText.style.textShadow = "0 0 10px rgba(255,77,77,0.5)";
                    timerBar.style.background = "linear-gradient(90deg, #ff4d4d, #ff1a1a)";
                    // Pulsing animation for the last 20 seconds
                    timerText.style.animation = "pulse 0.8s infinite alternate";
                }
                
                timeLeft--;
            }
            
            // Add custom pulse animation keyframes
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes pulse {
                    from { transform: scale(1); opacity: 1; }
                    to { transform: scale(1.05); opacity: 0.7; }
                }
            `;
            document.head.appendChild(style);
            
            updateTimer();
            const interval = setInterval(updateTimer, 1000);
        })();
    </script>
    """.replace("REMAINING_SECONDS", str(remaining_seconds))
    components.html(timer_html, height=75)


def parse_amount(amt_str):
    if not amt_str: return None
    amt_str = str(amt_str).lower().replace(",", "").replace("₹", "").strip()
    try:
        if amt_str.endswith('k'):
            return int(float(amt_str[:-1]) * 1000)
        elif 'lakh' in amt_str or amt_str.endswith('l'):
            val = amt_str.replace('lakhs', '').replace('lakh', '').replace('l', '').strip()
            return int(float(val) * 100000)
        elif 'cr' in amt_str or 'crore' in amt_str or amt_str.endswith('c'):
            val = amt_str.replace('crores', '').replace('crore', '').replace('cr', '').replace('c', '').strip()
            return int(float(val) * 10000000)
        else:
            return int(float(amt_str))
    except ValueError:
        return None

def get_base_price(tier):
    tier_norm = str(tier).strip().capitalize()
    return 100000 if tier_norm == "Diamond" else 50000

def convert_drive_link(url):
    if not url:
        return url
    url = str(url).strip()
    if 'drive.google.com' in url:
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w1000"
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if match:
            return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w1000"
    return url

def format_currency(amount):
    s, *d = str(amount).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return f"₹{r}"

st.set_page_config(page_title="Cricket Auction Dashboard", layout="wide", page_icon="🏏")

# --- Custom CSS for beautiful UI ---
st.markdown("""
    <style>
    .player-card {
        background-color: #1e1e24;
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 20px;
    }
    .player-name {
        font-size: 32px;
        font-weight: 800;
        margin: 10px 0 5px 0;
        color: #ffcc00;
    }
    .player-role {
        font-size: 18px;
        color: #cccccc;
        font-weight: 500;
        margin-top: 10px;
    }
    .role-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        color: white !important;
    }
    .role-batsman {
        background: linear-gradient(135deg, #ff4d4d, #c30000);
        color: white;
    }
    .role-bowler {
        background: linear-gradient(135deg, #00bfff, #005f9e);
        color: white;
    }
    .role-all-rounder {
        background: linear-gradient(135deg, #b030b0, #600060);
        color: white;
    }
    .role-wicketkeeper {
        background: linear-gradient(135deg, #ff8c00, #b85d00);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.members = {}
    st.session_state.players = []
    st.session_state.unsold_players = []
    st.session_state.current_player = None
    st.session_state.current_bid = 0
    st.session_state.current_bidder = None
    st.session_state.logs = []
    st.session_state.bid_end_time = None
    st.session_state.last_action = None
    st.session_state.show_celebration = None

def add_log(msg):
    st.session_state.logs.insert(0, msg)
    if len(st.session_state.logs) > 15:
        st.session_state.logs.pop()

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    if not st.session_state.initialized:
        st.subheader("📁 Import Data (Optional)")
        st.caption("Leave empty to use sample data.")
        members_file = st.file_uploader("Upload Franchises (TXT - 1 per line)", type=['txt', 'csv'])
        players_file = st.file_uploader("Upload Players (CSV or Excel with 'Name', 'Role' columns)", type=['csv', 'xlsx', 'xls'])
        
        if st.button("🚀 Initialize Auction Data", type="primary", use_container_width=True):
            # Load Members
            if members_file is not None:
                content = members_file.getvalue().decode("utf-8")
                loaded_members = [line.strip() for line in content.split('\n') if line.strip()]
            else:
                loaded_members = [f"Franchise_{i}" for i in range(1, 13)]
            
            # Load Players
            if players_file is not None:
                try:
                    if players_file.name.endswith('.csv'):
                        df_p = pd.read_csv(players_file)
                    else:
                        df_p = pd.read_excel(players_file)
                    
                    # 1. Smart Name Column Detector
                    name_col = None
                    for col in df_p.columns:
                        col_l = str(col).strip().lower()
                        if col_l in ['name', 'player name', 'playername', 'names', 'players', 'player']:
                            name_col = col
                            break
                    if name_col is None:
                        for col in df_p.columns:
                            if 'name' in str(col).strip().lower():
                                name_col = col
                                break
                    if name_col is None:
                        name_col = df_p.columns[0]

                    # 2. Smart Role/Specialism Column Detector
                    role_col = None
                    for col in df_p.columns:
                        col_l = str(col).strip().lower()
                        if col_l in ['role', 'specialism', 'skills', 'skill', 'category', 'type', 'playing role', 'playingrole', 'speciality', 'specialism/skills']:
                            role_col = col
                            break
                    if role_col is None:
                        for col in df_p.columns:
                            col_l = str(col).strip().lower()
                            if col != name_col and any(k in col_l for k in ['role', 'skill', 'spec', 'cat', 'type', 'special']):
                                role_col = col
                                break
                    
                    # 3. Smart Photo Column Detector
                    photo_col = None
                    for col in df_p.columns:
                        col_l = str(col).strip().lower()
                        if any(k in col_l for k in ['photo', 'image', 'img', 'pic', 'link', 'url', 'drive']):
                            photo_col = col
                            break

                    # 4. Smart Tier Column Detector
                    tier_col = None
                    for col in df_p.columns:
                        col_l = str(col).strip().lower()
                        if col_l in ['tier', 'category', 'grade', 'class']:
                            tier_col = col
                            break

                    loaded_players = []
                    for _, row in df_p.iterrows():
                        name = row[name_col] if name_col in df_p.columns else row.iloc[0]
                        
                        # Resolve role: check if column is found AND is different from name column!
                        if role_col and role_col in df_p.columns and role_col != name_col:
                            role = row[role_col]
                        else:
                            # If no distinct role column is available in the CSV, dynamically assign a deterministic
                            # cricket role based on the player's name so it feels realistic and matches expectations!
                            roles_pool = ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"]
                            name_hash = sum(ord(c) for c in str(name))
                            role = roles_pool[name_hash % len(roles_pool)]
                        
                        # Resolve photo
                        photo_url = row[photo_col] if photo_col and photo_col in df_p.columns else None
                        if pd.notna(photo_url):
                            photo_url = convert_drive_link(photo_url)
                            
                        # Resolve tier
                        tier = row[tier_col] if tier_col and tier_col in df_p.columns else "Standard"
                        
                        loaded_players.append({
                            "name": str(name).strip(), 
                            "role": str(role).strip(),
                            "photo": str(photo_url).strip() if pd.notna(photo_url) else None,
                            "tier": str(tier).strip()
                        })
                except Exception as e:
                    st.error(f"Error reading players file: {e}")
                    loaded_players = []
            else:
                loaded_players = [
                    {"name": "Virat Kohli", "role": "Batsman", "tier": "Diamond"},
                    {"name": "Jasprit Bumrah", "role": "Bowler", "tier": "Diamond"},
                    {"name": "Hardik Pandya", "role": "All-rounder", "tier": "Diamond"},
                    {"name": "MS Dhoni", "role": "Wicketkeeper", "tier": "Diamond"},
                    {"name": "Rashid Khan", "role": "Bowler", "tier": "Standard"},
                    {"name": "Ben Stokes", "role": "All-rounder", "tier": "Standard"},
                    {"name": "Rohit Sharma", "role": "Batsman", "tier": "Diamond"},
                    {"name": "Trent Boult", "role": "Bowler", "tier": "Standard"},
                    {"name": "Suryakumar Yadav", "role": "Batsman", "tier": "Diamond"},
                    {"name": "Mitchell Starc", "role": "Bowler", "tier": "Standard"}
                ]
            
            st.session_state.members = {
                m: {"balance": 1000000, "squad": []} for m in loaded_members
            }
            st.session_state.players = loaded_players
            st.session_state.unsold_players = []
            st.session_state.current_player = None
            st.session_state.initialized = True
            add_log(f"🟢 System Initialized with {len(loaded_members)} Members and {len(loaded_players)} Players.")
            st.rerun()

    if st.session_state.initialized:
        st.markdown("### 📋 Quick Stats")
        st.write(f"**Players Left:** {len(st.session_state.players)}")
        st.write(f"**Unsold Queue:** {len(st.session_state.unsold_players)}")
        
        with st.expander("🔍 View Loaded Data (Debug)", expanded=False):
            st.dataframe(st.session_state.players)
            
        st.divider()
        if st.button("🛑 Reset Entire System", use_container_width=True):
            st.session_state.initialized = False
            st.rerun()

# --- Header ---
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    st.image("rio_lions_logo.jpg", width=100)
with header_col2:
    st.title("Rio Lions Cricket Auction Dashboard")

if st.session_state.get('show_celebration'):
    cel = st.session_state.show_celebration
    is_sold = cel.get("type", "SOLD") == "SOLD"
    
    if is_sold:
        main_text = "• SOLD •"
        details_html = f"<div class='sold-details'>{cel['player']} ➔ {cel['member']}</div><div class='sold-price'>{format_currency(cel['price'])}</div>"
        text_class = "sold-text stamp-effect"
        text_animation = "stampSlam 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards"
        overlay_animation = "fadeOutOverlay 1s ease 4s forwards"
    else:
        main_text = "UNSOLD"
        details_html = f"<div class='sold-details'>{cel['player']} Returns to Pool</div>"
        text_class = "sold-text unsold-effect"
        text_animation = "fadeInDown 0.8s ease forwards"
        overlay_animation = "fadeOutOverlay 1s ease 4s forwards"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Stardos+Stencil:wght@700&display=swap');
        
        .sold-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.85);
            z-index: 999999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            animation: {overlay_animation};
        }}
        .sold-text {{
            font-size: 150px;
            font-weight: 900;
            text-transform: uppercase;
            margin: 0;
            line-height: 1;
            text-align: center;
            display: inline-block;
            animation: {text_animation};
            font-family: 'Stardos Stencil', cursive, sans-serif;
        }}
        .stamp-effect {{
            color: #d32f2f;
            border: 6px solid #d32f2f;
            padding: 20px 40px;
            border-radius: 20px;
            background: transparent;
            outline: 12px solid #d32f2f;
            outline-offset: 8px;
            margin: 30px; /* Space for the outline */
            /* Ensure the stamp stays rotated after animation */
            transform: rotate(-15deg);
        }}
        .unsold-effect {{
            color: #888888;
            text-shadow: 0 0 40px #555555, 0 0 80px #222222;
        }}
        .sold-details {{
            font-size: 50px;
            color: white;
            margin-top: 50px;
            font-weight: bold;
            opacity: 0;
            animation: fadeInDetails 1s ease 1s forwards;
            text-align: center;
        }}
        .sold-price {{
            font-size: 70px;
            color: #00ffcc;
            text-shadow: 0 0 20px #00ffcc;
            margin-top: 10px;
            opacity: 0;
            animation: fadeInDetails 1s ease 1.5s forwards;
            text-align: center;
        }}
        @keyframes stampSlam {{
            0% {{ transform: scale(3) rotate(-20deg); opacity: 0; }}
            50% {{ transform: scale(1.05) rotate(-10deg); opacity: 1; }}
            100% {{ transform: scale(1) rotate(-15deg); opacity: 1; }}
        }}
        @keyframes fadeInDown {{
            0% {{ transform: translateY(-50px); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}
        @keyframes fadeInDetails {{
            0% {{ opacity: 0; transform: translateY(30px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeOutOverlay {{
            0% {{ opacity: 1; visibility: visible; }}
            100% {{ opacity: 0; visibility: hidden; }}
        }}
        </style>
        <div class="sold-overlay">
            <div class="{text_class}">{main_text}</div>
            {details_html}
        </div>
    """, unsafe_allow_html=True)
    st.session_state.show_celebration = None

if not st.session_state.initialized:
    st.info("👋 Welcome! Please click **'🚀 Initialize Auction Data'** in the sidebar to begin.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔨 Live Auction", "📊 Franchises Status", "🏆 Final Summary"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_player is None:
            st.success("The floor is open. Ready to bring the next player under the hammer!")
            
            st.markdown("### 🎯 Bring Player to Floor")
            st_col1, st_col2 = st.columns(2)
            
            with st_col1:
                st.markdown("#### 🎲 Standard Draw")
                if st.button("Draw Random Standard Player", type="primary", use_container_width=True):
                    standard_pool = [p for p in st.session_state.players if str(p.get("tier", "Standard")).strip().capitalize() != "Diamond"]
                    if not standard_pool:
                        if not st.session_state.players:
                            st.error("🏁 All players processed. Auction over!")
                        else:
                            st.error("No Standard players left in the pool. Only Diamonds remain.")
                    else:
                        st.session_state.current_player = random.choice(standard_pool)
                        st.session_state.players.remove(st.session_state.current_player)
                        st.session_state.current_bid = get_base_price(st.session_state.current_player.get("tier", "Standard"))
                        st.session_state.current_bidder = None
                        st.session_state.bid_end_time = time.time() + 120
                        add_log(f"🎲 Drew {st.session_state.current_player['name']} ({st.session_state.current_player['role']}) for auction.")
                        st.rerun()

            with st_col2:
                st.markdown("#### 💎 Diamond Selection")
                diamond_pool = [p for p in st.session_state.players if str(p.get("tier", "Standard")).strip().capitalize() == "Diamond"]
                if diamond_pool:
                    diamond_names = [p['name'] for p in diamond_pool]
                    selected_diamond = st.selectbox("Select Diamond Player", ["-- Select --"] + diamond_names, label_visibility="collapsed")
                    if st.button("Select Diamond Player", type="primary", use_container_width=True):
                        if selected_diamond == "-- Select --":
                            st.warning("Please select a Diamond player from the list.")
                        else:
                            for p in diamond_pool:
                                if p['name'] == selected_diamond:
                                    st.session_state.current_player = p
                                    st.session_state.players.remove(p)
                                    st.session_state.current_bid = get_base_price(p.get("tier", "Standard"))
                                    st.session_state.current_bidder = None
                                    st.session_state.bid_end_time = time.time() + 120
                                    add_log(f"💎 Selected Diamond Player {p['name']} ({p['role']}) for auction.")
                                    st.rerun()
                                    break
                else:
                    st.info("No Diamond players left in pool.")

            st.write("<br>", unsafe_allow_html=True)
            undo_col1, undo_col2 = st.columns([1, 3])
            with undo_col1:
                if st.session_state.get('last_action'):
                    if st.button("↩️ Undo", use_container_width=True):
                        la = st.session_state.last_action
                        p = la['player']
                        if la['type'] == 'SOLD':
                            st.session_state.members[la['bidder']]['balance'] += la['price']
                            st.session_state.members[la['bidder']]['squad'] = [
                                x for x in st.session_state.members[la['bidder']]['squad'] if x['name'] != p['name']
                            ]
                            add_log(f"↩️ UNDO: Cancelled sale of {p['name']}.")
                        elif la['type'] == 'UNSOLD':
                            if p in st.session_state.unsold_players:
                                st.session_state.unsold_players.remove(p)
                            add_log(f"↩️ UNDO: Brought {p['name']} back from Unsold.")
                        
                        st.session_state.current_player = p
                        st.session_state.current_bid = get_base_price(p.get("tier", "Standard"))
                        st.session_state.current_bidder = None
                        st.session_state.bid_end_time = time.time() + 120
                        st.session_state.last_action = None
                        st.rerun()
        else:
            p = st.session_state.current_player
            
            # Beautiful Player Card
            st.markdown('<div class="player-card">', unsafe_allow_html=True)
            
            # Use real photo if available, else placeholder
            photo_url = p.get('photo')
            safe_name = p['name'].replace(' ', '+').replace("'", "")
            fallback_img = f"https://dummyimage.com/800x400/232b2b/ffcc00.png&text={safe_name}"
            
            if photo_url and str(photo_url).lower() not in ['nan', 'none', '']:
                st.markdown(
                    f'<img src="{photo_url}" referrerpolicy="no-referrer" '
                    f'style="width:100%; max-height:450px; object-fit:contain; border-radius:10px; margin-bottom:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);" '
                    f'onerror="this.onerror=null; this.src=\'{fallback_img}\';" />', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<img src="{fallback_img}" '
                    f'style="width:100%; max-height:450px; object-fit:contain; border-radius:10px; margin-bottom:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);" />', 
                    unsafe_allow_html=True
                )
                
            # Determine role badge class, icon, and display name
            role_lower = p.get('role', 'Player').lower()
            if 'batsman' in role_lower or 'bat' in role_lower:
                role_class = "role-batsman"
                role_icon = "🏏"
                role_display = "Batsman"
            elif 'bowler' in role_lower or 'bowl' in role_lower:
                role_class = "role-bowler"
                role_icon = "🥎"
                role_display = "Bowler"
            elif 'all-rounder' in role_lower or 'allrounder' in role_lower or 'all rounder' in role_lower:
                role_class = "role-all-rounder"
                role_icon = "⚡"
                role_display = "All-rounder"
            elif 'keeper' in role_lower or 'wk' in role_lower or 'wicket' in role_lower:
                role_class = "role-wicketkeeper"
                role_icon = "🧤"
                role_display = "Wicketkeeper"
            else:
                role_class = "role-batsman"
                role_icon = "🏃"
                role_display = p.get('role', 'Player')

            st.markdown(f'<div class="player-name">{p["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="player-role"><span class="role-badge {role_class}">{role_icon} {role_display}</span> • <span class="role-badge" style="background: #444;">{p.get("tier", "Standard")} ({format_currency(get_base_price(p.get("tier", "Standard")))})</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Calculate and render the bidding timer
            if st.session_state.bid_end_time is not None:
                remaining_seconds = max(0, int(st.session_state.bid_end_time - time.time()))
            else:
                remaining_seconds = 120
            render_timer(remaining_seconds)
            
            # Bid metrics
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.metric("Current Bid", format_currency(st.session_state.current_bid))
            with mcol2:
                st.metric("Highest Bidder", st.session_state.current_bidder if st.session_state.current_bidder else "None")
            
            st.divider()
            
            # Action Controls
            st.subheader(f"💰 Place a Bid for {p['name']} ({role_display})")
            b_col1, b_col2, b_col3 = st.columns([2, 2, 1])
            with b_col1:
                member_options = list(st.session_state.members.keys())
                bidder = st.selectbox("Select Franchise", member_options)
            with b_col2:
                bid_amt = st.text_input("Amount (e.g., 50k, 1.5cr, 50,000)", value="")
            with b_col3:
                st.write("") # spacing
                st.write("") # spacing
                if st.button("Raise Paddle", type="primary", use_container_width=True):
                    amt = parse_amount(bid_amt)
                    base_p = get_base_price(p.get("tier", "Standard"))
                    if st.session_state.members[bidder]['balance'] < 50000:
                        st.error(f"{bidder} has less than ₹50,000 remaining and can no longer participate in the auction.")
                    elif amt is None:
                        st.error("Invalid amount format.")
                    elif amt <= st.session_state.current_bid and st.session_state.current_bidder is not None:
                        st.error("Bid must be higher than current bid.")
                    elif amt < base_p:
                         st.error(f"Bid cannot be lower than base price ({format_currency(base_p)}).")
                    elif amt > st.session_state.members[bidder]['balance']:
                        st.error("Insufficient balance!")
                    else:
                        st.session_state.current_bid = amt
                        st.session_state.current_bidder = bidder
                        add_log(f"💵 {bidder} raised paddle to {format_currency(amt)}")
                        st.rerun()
            
            st.write("<br>", unsafe_allow_html=True)
            
            # Resolve Buttons
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                if st.button("🔨 Mark as SOLD", type="primary", use_container_width=True):
                    if not st.session_state.current_bidder:
                        st.error("Cannot sell without any bids!")
                    else:
                        final_member = st.session_state.current_bidder
                        final_amt = st.session_state.current_bid
                        
                        st.session_state.members[final_member]['balance'] -= final_amt
                        st.session_state.members[final_member]['squad'].append({
                            "name": p['name'], "role": p['role'], "tier": p.get("tier", "Standard"), "price": final_amt
                        })
                        add_log(f"🎉 SOLD: {p['name']} ({p['role']}) to {final_member} for {format_currency(final_amt)}!")
                        
                        st.session_state.last_action = {
                            "type": "SOLD", "player": p, "bidder": final_member, "price": final_amt
                        }
                        
                        st.session_state.show_celebration = {
                            "type": "SOLD", "player": p['name'], "member": final_member, "price": final_amt
                        }
                        
                        st.session_state.current_player = None
                        st.session_state.current_bid = 0
                        st.session_state.current_bidder = None
                        st.session_state.bid_end_time = None
                        st.rerun()
            
            with r_col2:
                if st.button("❌ Mark as UNSOLD", use_container_width=True):
                    st.session_state.unsold_players.append(p)
                    add_log(f"❌ UNSOLD: {p['name']} ({p['role']}) returns to pool.")
                    
                    st.session_state.last_action = {
                        "type": "UNSOLD", "player": p
                    }
                    
                    st.session_state.show_celebration = {
                        "type": "UNSOLD", "player": p['name']
                    }
                    
                    st.session_state.current_player = None
                    st.session_state.current_bid = 0
                    st.session_state.current_bidder = None
                    st.session_state.bid_end_time = None
                    st.rerun()

    with col2:
        st.subheader("📜 Event Log")
        log_box = st.container(height=650)
        with log_box:
            for log in st.session_state.logs:
                st.markdown(f"> {log}")

with tab2:
    st.header("📊 Franchise Status Board")
    data = []
    for member, info in st.session_state.members.items():
        data.append({
            "Franchise": member,
            "Remaining Purse": format_currency(info['balance']),
            "Players Bought": len(info['squad']),
            "Raw_Balance": info['balance']
        })
    if data:
        df = pd.DataFrame(data).sort_values(by="Raw_Balance", ascending=False).drop(columns=["Raw_Balance"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No franchises initialized yet.")

with tab3:
    st.header("🏆 Final Auction Summary")
    
    col_idx = 0
    cols = st.columns(3)
    for member, info in st.session_state.members.items():
        with cols[col_idx % 3]:
            st.markdown(f"#### {member}")
            st.markdown(f"**Purse Left:** {format_currency(info['balance'])}")
            st.markdown(f"**Squad Size:** {len(info['squad'])}")
            if info['squad']:
                for p in info['squad']:
                    st.caption(f"- {p['name']} ({p['role']} - {p.get('tier', 'Standard')}) ➔ {format_currency(p['price'])}")
            else:
                st.caption("No players bought yet.")
            st.divider()
        col_idx += 1
