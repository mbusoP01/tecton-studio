import streamlit as st
import os
import json
import time
import shutil
import streamlit.components.v1 as components
from brains import talk_to_brain
from blueprints import ARCHITECT_SYSTEM_PROMPT, BUILDER_SYSTEM_PROMPT
from utils import save_file, create_zip_from_folder, scan_directory, read_file, assemble_preview_html
from dotenv import load_dotenv
import re 

load_dotenv()
# --- CLOUD FIX: Bridge Gemini Key to App ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["API_KEY"] = st.secrets["GEMINI_API_KEY"]
except:
    pass
# -------------------------------------------

# --- THEME CONFIGURATION ---
THEMES = {
    "Quantum (Default)": {
        "primary": "rgba(255, 255, 255, 0.95)", 
        "secondary": "#F5F5F7", 
        "text": "#1D1D1F", 
        "accent": "#0071E3", 
        "border": "1px solid #E5E5EA", 
        "font": "-apple-system, BlinkMacSystemFont, sans-serif", 
        "bg_css": "background: #F2F2F7;", 
        "input_bg": "#FFFFFF"
    },
    "Hacker (Matrix)": {
        "primary": "rgba(13, 17, 23, 0.95)", 
        "secondary": "#001A00", 
        "text": "#00FF41", 
        "accent": "#008F11", 
        "border": "1px solid #003B00", 
        "font": "'Courier New', monospace", 
        "bg_css": "background-color: #000000; background-image: linear-gradient(0deg, transparent 24%, rgba(0, 255, 65, .05) 25%, rgba(0, 255, 65, .05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 65, .05) 75%, rgba(0, 255, 65, .05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 255, 65, .05) 25%, rgba(0, 255, 65, .05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 65, .05) 75%, rgba(0, 255, 65, .05) 76%, transparent 77%, transparent); background-size: 50px 50px;", 
        "input_bg": "#050505"
    },
    "Neon City (Cyberpunk)": {
        "primary": "rgba(20, 0, 40, 0.9)", 
        "secondary": "#2D0040", 
        "text": "#E0E0E0", 
        "accent": "#FF00FF", 
        "border": "1px solid rgba(255, 0, 255, 0.3)", 
        "font": "sans-serif", 
        "bg_css": "background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);", 
        "input_bg": "rgba(0,0,0,0.3)"
    },
    "Aurora (Northern Lights)": {
        "primary": "rgba(16, 24, 39, 0.8)", 
        "secondary": "#161B33", 
        "text": "#E2E8F0", 
        "accent": "#00F0FF", 
        "border": "1px solid rgba(79, 209, 197, 0.2)", 
        "font": "sans-serif", 
        "bg_css": "background: linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);", 
        "input_bg": "rgba(0,0,0,0.2)"
    },
    "Golden Hour (Luxury)": {
        "primary": "rgba(255, 252, 245, 0.95)", 
        "secondary": "#FFF7ED", 
        "text": "#431407", 
        "accent": "#D97706", 
        "border": "1px solid #FED7AA", 
        "font": "'Georgia', serif", 
        "bg_css": "background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);", 
        "input_bg": "#FFFFFF"
    },
    "Midnight (Deep Focus)": {
        "primary": "rgba(15, 23, 42, 0.95)", 
        "secondary": "#1E293B", 
        "text": "#F8FAFC", 
        "accent": "#38BDF8", 
        "border": "1px solid #334155", 
        "font": "sans-serif", 
        "bg_css": "background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);", 
        "input_bg": "#0F172A"
    },
    "Lofi (Chill)": {
        "primary": "rgba(255, 240, 245, 0.95)", 
        "secondary": "#F3E5F5", 
        "text": "#4A4A4A", 
        "accent": "#BA68C8", 
        "border": "1px solid #E1BEE7", 
        "font": "'Courier New', monospace", 
        "bg_css": "background: linear-gradient(to bottom, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);", 
        "input_bg": "#FFF5F8"
    },
    "Forest (Zen)": {
        "primary": "rgba(240, 253, 244, 0.95)", 
        "secondary": "#DCFCE7", 
        "text": "#14532D", 
        "accent": "#16A34A", 
        "border": "1px solid #BBF7D0", 
        "font": "sans-serif", 
        "bg_css": "background: linear-gradient(180deg, #D1FAE5 0%, #10B981 100%);", 
        "input_bg": "#FFFFFF"
    },
    "Obsidian (Dark)": {
        "primary": "#121212", 
        "secondary": "#1E1E1E", 
        "text": "#EDEDED", 
        "accent": "#EDEDED", 
        "border": "1px solid #333", 
        "font": "sans-serif", 
        "bg_css": "background-color: #000000;", 
        "input_bg": "#2C2C2C"
    },
    "Blueprint (Engineering)": {
        "primary": "#003366", 
        "secondary": "#004080", 
        "text": "#FFFFFF", 
        "accent": "#FFD700", 
        "border": "1px dashed #FFD700", 
        "font": "'Courier New', monospace", 
        "bg_css": "background-color: #002244; background-image: linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px); background-size: 20px 20px; background-position: -1px -1px;", 
        "input_bg": "#002b55"
    }
}

# --- SESSION STATE INIT ---
if "active_theme" not in st.session_state: st.session_state.active_theme = "Quantum (Default)"
if "preview_theme" not in st.session_state: st.session_state.preview_theme = "Quantum (Default)"
if "active_project" not in st.session_state: st.session_state.active_project = None
if "history" not in st.session_state: st.session_state.history = []
if "is_building" not in st.session_state: st.session_state.is_building = False
if "show_code_view" not in st.session_state: st.session_state.show_code_view = False
if "last_generated_code" not in st.session_state: st.session_state.last_generated_code = ""
if "current_file_name" not in st.session_state: st.session_state.current_file_name = ""

st.set_page_config(page_title="Tecton", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Tecton")
    st.caption("v5.2 Studio Edition (Hardened)")
    st.markdown("---")
    
    with st.expander("Personalization", expanded=True):
        st.caption("Theme Selector")
        selected = st.selectbox("Library", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.active_theme), label_visibility="collapsed")
        preview_config = THEMES[selected]
        
        st.markdown(f"""
        <div style="margin-top:10px; margin-bottom:15px;">
            <div style="{preview_config['bg_css']} height: 60px; border-radius: 6px; border: 1px solid #ccc; display: flex; align-items: center; justify_content: center;">
                <div style="background-color: {preview_config['primary']}; padding: 2px 8px; border-radius: 4px; border: {preview_config['border']}; color: {preview_config['text']}; font-size: 10px;">
                    Preview
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if selected != st.session_state.active_theme:
            if st.button("Confirm Theme"):
                st.session_state.active_theme = selected
                st.rerun()

    st.markdown("---")
    with st.expander("Recent Builds", expanded=True):
        if st.session_state.history:
            for project in st.session_state.history:
                hc1, hc2 = st.columns([4, 1])
                with hc1:
                    if st.button(f"[F] {project}", key=f"load_{project}"):
                        st.session_state.active_project = project
                        st.rerun()
        else:
            st.caption("No active session builds.")

    api_key = os.getenv("API_KEY")
    if not api_key:
        st.warning("Key Required")
        api_key = st.text_input("Groq Key", type="password")
        if api_key: os.environ["API_KEY"] = api_key

# --- CSS INJECTION ---
current_theme = THEMES[st.session_state.active_theme]
st.markdown(f"""
    <style>
    /* ANIMATIONS */
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes slideUp {{ from {{ transform: translateY(10px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
    @keyframes pulse-glow {{ 0% {{ box-shadow: 0 0 5px {current_theme['accent']}; }} 50% {{ box-shadow: 0 0 20px {current_theme['accent']}; }} 100% {{ box-shadow: 0 0 5px {current_theme['accent']}; }} }}
    
    :root {{
        --primary-color: {current_theme['primary']};
        --secondary-color: {current_theme['secondary']};
        --text-color: {current_theme['text']};
        --accent-color: {current_theme['accent']};
        --border-color: {current_theme['border'].split(' ')[-1]};
        --font-fam: {current_theme['font']};
        --input-bg: {current_theme['input_bg']};
    }}

    header {{ background-color: transparent !important; visibility: visible !important; }}
    
    /* UI ELEMENTS */
    .stApp {{ {current_theme['bg_css']} font-family: var(--font-fam); color: var(--text-color); }}
    
    section[data-testid="stSidebar"] {{ background-color: var(--secondary-color); border-right: 1px solid var(--border-color); }}
    section[data-testid="stSidebar"] * {{ color: var(--text-color) !important; }}
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{ 
        background-color: var(--input-bg); color: var(--text-color); border: {current_theme['border']}; border-radius: 8px; 
    }}
    
    div[data-testid="stVerticalBlock"] > div:has(div.creation-card) {{ 
        background-color: var(--primary-color); padding: 2.5rem; border-radius: 20px; border: {current_theme['border']}; 
        backdrop-filter: blur(10px); animation: slideUp 0.5s ease-out;
    }}
    
    .stButton > button {{ 
        background-color: var(--accent-color); color: {'#000' if 'Matrix' in st.session_state.active_theme else '#FFF'}; 
        border-radius: 10px; border: none; transition: all 0.2s;
    }}
    .stButton > button:hover {{ transform: scale(1.02); }}
    
    section[data-testid="stSidebar"] .stButton > button {{ background: transparent; border: 1px solid var(--text-color); color: var(--text-color); }}

    /* ENTERTAINMENT / STATUS WIDGET */
    .status-widget {{
        background-color: var(--input-bg);
        border: {current_theme['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: var(--text-color);
        margin-top: 20px;
        animation: fadeIn 1s ease;
    }}
    
    h1, h2, h3, p, label {{ color: var(--text-color) !important; }}
    
    /* TAB STYLING */
    button[data-baseweb="tab"] {{
        background-color: transparent;
        color: var(--text-color);
        border-radius: 5px;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: var(--accent-color) !important;
        color: #fff !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

def extract_json_from_text(text):
    """
    Robustly extracts the first JSON array ([...]) found in a noisy text response.
    """
    if text is None: return None # Safety check for None input
    
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        json_str = match.group(0)
        json_str = json_str.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None
    return None


def render_idle_animation():
    """Professional system status display."""
    st.markdown(f"""
    <div class="status-widget">
        <div style="font-size: 2em; margin-bottom: 10px; color: var(--accent-color);">●</div>
        <div style="font-weight: 600; font-size: 1.1em;">System Standby</div>
        <div style="opacity: 0.7; font-size: 0.9em; margin-top: 5px;">Ready for input parameters</div>
        <div style="margin-top: 15px; height: 2px; width: 100%; background: linear-gradient(90deg, transparent, var(--accent-color), transparent); opacity: 0.5;"></div>
    </div>
    """, unsafe_allow_html=True)

def build_app_logic():
    """Core build loop with progress bar and live code viewing."""
    st.session_state.is_building = True
    
    # 1. Architect Phase
    with st.spinner("Architecting Solution..."):
        existing_files = scan_directory(st.session_state.active_project)
        
        # Call Brain
        archetype_response = talk_to_brain(
            "You are TECTON's Visual Scaffolding Engine. Based on the user's request, identify the best visual archetype (e.g., 'Notion-like data app', 'Stripe modern checkout', 'Apple clean website', 'GitHub dashboard'). Output ONLY the archetype name in one phrase.",
            st.session_state.user_prompt
        )
        
        # Check Archetype Response
        if not archetype_response:
            st.error("Signal Lost: Could not contact AI. Check your API Key/Internet.")
            st.session_state.is_building = False
            st.stop()

        archetype = archetype_response.strip()
        
        commercial_prompt = (
            f"User Request: {st.session_state.user_prompt}\n"
            f"**VISUAL ARCHETYPE:** {archetype}\n\n"
            "### FINAL DELIVERY STANDARDS (CTO LEVEL):\n"
            "1. **STYLE**: You MUST use **Tailwind CSS classes** via CDN for all styling. Do not write separate style.css files if possible. This ensures high-quality, professional, mobile-responsive design.\n"
            "2. **PRE-FILL CONTENT**: If the app is empty, pre-fill it with 2 demo items/sections/tasks. Write real, engaging marketing copy. Never use 'Lorem Ipsum' or blank sections.\n"
            "3. **ROBUSTNESS**: Ensure all JS/HTML code is perfectly functional and complete (no //TODO comments). The resulting files must be ready for immediate deployment.\n"
            "4. **OUTPUT FORMAT**: You must output ONLY a JSON list of file paths (STRINGS) inside square brackets."
        )
        
        architect_prompt = f"Existing Files: {existing_files}\nUser Request: {commercial_prompt}"
        arch_resp = talk_to_brain(ARCHITECT_SYSTEM_PROMPT, architect_prompt)
        
        # Check Architect Response
        if not arch_resp:
             st.error("Architectural Signal Lost.")
             st.session_state.is_building = False
             st.stop()

        file_list = extract_json_from_text(arch_resp)
        
        if not file_list or not isinstance(file_list, list):
            st.error("Architectural Collapse: Tecton failed to create a valid file blueprint. Try a simpler prompt.")
            st.session_state.is_building = False
            st.stop()
            
        # FIX: Ensure file_list is a list of strings, not objects
        file_list = [list(f.values())[0] if isinstance(f, dict) else f for f in file_list]

    # 2. Builder Phase Setup
    progress_bar = st.progress(0)
    status_text = st.empty()
    code_display_area = st.empty()
    
    total = len(file_list)
    start_time = time.time()
    
    for i, filename in enumerate(file_list):
        # Time Calc
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1) if i > 0 else 0
        eta = avg_time * (total - i)
        
        status_text.markdown(f"**Building:** `{filename}` | **Progress:** {int((i/total)*100)}% | **ETA:** {eta:.1f}s")
        
        prev_content = read_file(st.session_state.active_project, filename)
        
        builder_prompt = (
            f"Project Context: {file_list}\nTarget: {filename}\nExisting Content:\n{prev_content}\n"
            "REQUIREMENT: Write COMPLETE, COMMERCIAL-GRADE code. Use Tailwind CSS via CDN in HTML."
        )
        
        code = talk_to_brain(BUILDER_SYSTEM_PROMPT, builder_prompt)
        
        if code:
            # Clean code string
            if code.startswith("```"):
                parts = code.split("\n")
                if len(parts) > 2:
                    code = "\n".join(parts[1:-1])
                else:
                    code = code.replace("```", "")
            
            # Show Live Code at Top of Right Column
            language = 'python' if filename.endswith('.py') else 'javascript' if filename.endswith('.js') else 'html'
            code_display_area.code(code, language=language)
            
            # SANITIZE PATH & SAVE
            safe_filename = filename.lstrip('/').lstrip('\\')
            try:
                save_file(st.session_state.active_project, safe_filename, code)
            except Exception as e:
                st.warning(f"Skipped {filename}: {e}")
        
        progress_bar.progress((i + 1) / total)
    
    status_text.success("Build Complete.")
    
    # AUTO-SWITCH to Main File for viewing
    main_files = ["index.html", "main.py", "App.js", "README.md"]
    for mf in main_files:
        safe_mf = mf.lstrip('/').lstrip('\\')
        if os.path.exists(os.path.join(st.session_state.active_project, safe_mf)):
            st.session_state.last_generated_code = read_file(st.session_state.active_project, safe_mf)
            st.session_state.current_file_name = safe_mf
            break
            
    time.sleep(1)
    st.session_state.is_building = False
    st.rerun()

# --- MAIN LAYOUT (Preserved from v4.1) ---
in_studio = st.session_state.active_project is not None

if not in_studio:
    # LANDING PAGE
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown('<div class="creation-card"></div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>What should we build?</h1>", unsafe_allow_html=True)
        
        p_name = st.text_input("Project Name", "my_app")
        prompt = st.text_area("Describe your vision", height=120)
        
        if st.button("Start Building", use_container_width=True):
            if not os.getenv("API_KEY"): st.error("Key Required"); st.stop()
            st.session_state.active_project = p_name
            st.session_state.user_prompt = prompt
            
            if p_name not in st.session_state.history: st.session_state.history.append(p_name)
            if not os.path.exists(p_name): os.makedirs(p_name)
            
            st.session_state.is_building = True
            st.rerun()

else:
    # STUDIO MODE
    c1, c2 = st.columns([3, 1])
    with c1: st.markdown(f"### Editing: **{st.session_state.active_project}**")
    with c2:
        if st.button("✕ Close Project"):
            st.session_state.active_project = None
            st.session_state.show_code_view = False
            st.rerun()

    # Logic for Build
    if st.session_state.is_building:
        # Use the right column for build progress
        pass

    # Split Pane: Left = Chat, Right = Preview/Code Tabs
    col_edit, col_preview = st.columns([1, 1.5])
    
    with col_edit:
        st.markdown('<div class="creation-card"></div>', unsafe_allow_html=True)
        prompt = st.text_area("Refine your app", height=100)
        
        if st.button("Update Reality", use_container_width=True):
            if not os.getenv("API_KEY"): st.error("Key Required"); st.stop()
            st.session_state.user_prompt = prompt
            st.session_state.is_building = True
            st.session_state.show_code_view = True
            st.rerun()
            
        # Code View Toggle Logic
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render Code Monitor or Idle Animation
        if st.session_state.is_building:
            st.empty() # Placeholder for when the right side takes over build UI
        else:
            tabs_container = st.container()
            with tabs_container:
                # Code Monitor or Idle Animation Display
                if st.session_state.last_generated_code:
                    st.markdown("#### Code Monitor")
                    st.caption(f"File: {st.session_state.current_file_name}")
                    # Use st.code with dynamic language detection
                    language = 'html' if st.session_state.current_file_name.endswith('.html') else 'css' if st.session_state.current_file_name.endswith('.css') else 'javascript'
                    st.code(st.session_state.last_generated_code, language=language)
                else:
                    render_idle_animation()

    with col_preview:
        if st.session_state.is_building:
            # Run build logic directly in the right column so code streams visibly
            build_app_logic()
        else:
            # TABS for Switching between Preview and Code
            tab1, tab2 = st.tabs(["📱 Live Preview", "💻 Source Code"])
            
            with tab1:
                if not os.path.exists(st.session_state.active_project):
                    st.info("Project missing.")
                else:
                    preview_html = assemble_preview_html(st.session_state.active_project)
                    if preview_html:
                        components.html(preview_html, height=600, scrolling=True)
                    else:
                        st.info("Build to see preview.")
            
            with tab2:
                # File Explorer / Code Viewer
                files = scan_directory(st.session_state.active_project)
                if files:
                    selected_file = st.selectbox("Select File", files)
                    content = read_file(st.session_state.active_project, selected_file)
                    st.code(content, language='html' if selected_file.endswith('.html') else 'css' if selected_file.endswith('.css') else 'javascript')
                else:
                    st.caption("No files generated yet.")
                
                # Download button at bottom of code tab
                st.markdown("---")
                zip_buffer = create_zip_from_folder(st.session_state.active_project)

                st.download_button("Download Code", data=zip_buffer, file_name=f"{st.session_state.active_project}.zip", mime="application/zip", use_container_width=True)
