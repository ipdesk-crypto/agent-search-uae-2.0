import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Kyrix | Intelligence Command",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. LUXURY DARK THEME CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; } 
    .logo-container { display: flex; justify-content: center; padding: 10px 0 20px 0; }
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #F1F5F9 !important; font-family: 'Inter', sans-serif; }
    
    .metric-badge {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: #F59E0B !important;
        padding: 12px 24px; border-radius: 12px; font-weight: 800;
        font-size: 18px; border: 1px solid #334155; display: inline-block; margin-bottom: 20px;
    }
    .section-header {
        font-size: 12px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase;
        padding: 10px 15px; border-radius: 8px 8px 0 0; margin-top: 20px;
        border: 1px solid #475569; border-bottom: none;
    }
    .dynamic-banner { background: linear-gradient(90deg, #1E293B 0%, #334155 100%); color: #CBD5E1 !important; }
    .special-banner { background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%); color: #FFFFFF !important; }
    
    .data-card { 
        background-color: #111827; padding: 12px; 
        border: 1px solid #1F2937; border-bottom: 1px solid #374151;
        min-height: 60px;
    }
    .label-text { font-size: 9px; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 2px; }
    .value-text { font-size: 13px; color: #F8FAFC; font-weight: 500; line-height: 1.4; }
    .priority-value { color: #F59E0B !important; font-weight: 700; font-family: 'Courier New', monospace; }
    
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B; }
    .stDownloadButton button {
        background-color: #F59E0B !important; color: #0F172A !important;
        font-weight: 700 !important; border: none !important; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. UTILITIES ---
def harmonize_phone_strict(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return "—"
    clean_num = re.sub(r'\D', '', str(val))
    if clean_num.startswith("00971"): clean_num = clean_num[2:]
    elif clean_num.startswith("0"): clean_num = clean_num[1:]
    if not clean_num.startswith("971"): clean_num = "971" + clean_num
    return f"+{clean_num}"

def generate_dossier_text(row, group_map, all_groups):
    report = "KYRIX INTELLIGENCE COMMAND | DOSSIER EXPORT\n"
    report += f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "="*50 + "\n\n"
    for group in all_groups:
        report += f"[{group.upper()}]\n"
        report += "-"*20 + "\n"
        cols = [c for c, g in group_map.items() if g == group]
        for col in cols:
            if col in row:
                val = str(row[col]) if pd.notna(row[col]) else "—"
                if col == "Harmonized Phone Number": val = harmonize_phone_strict(row[col])
                report += f"{col}: {val}\n"
        report += "\n"
    report += "="*50 + "\nEND OF DOSSIER"
    return str(report)

# --- 4. DATA ENGINE ---
@st.cache_data
def load_data():
    path = "Data Structure - Registered Agents in UAE (Kyrix Intangible) - Enriched Data 2.0.csv"
    if not os.path.exists(path): return None, None, []
    
    g_row = pd.read_csv(path, skiprows=1, nrows=1, header=None).iloc[0].tolist()
    df = pd.read_csv(path, skiprows=2)
    df.columns = df.columns.str.strip()
    
    current_group, group_map, all_groups = "General Info", {}, []
    for i, col_name in enumerate(df.columns):
        g = str(g_row[i]) if i < len(g_row) and pd.notna(g_row[i]) else None
        if g and g.strip() and g.lower() != 'nan': current_group = g.strip()
        if current_group not in all_groups: all_groups.append(current_group)
        group_map[col_name] = current_group
    
    df = df[df['Firm Name'].notna()].copy()
    return df, group_map, all_groups

# --- 5. APP LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=180)
        st.markdown('<div style="background:#1E293B; padding:40px; border-radius:12px; border:1px solid #334155; text-align:center;"><h2>KYRIX ACCESS</h2>', unsafe_allow_html=True)
        key = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if key == "Kyrix2024": st.session_state.auth = True; st.rerun()
            else: st.error("Unauthorized Access")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    if os.path.exists("logo.png"):
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("logo.png", width=220)
        st.markdown('</div>', unsafe_allow_html=True)

    df, group_map, all_groups = load_data()
    if df is not None:
        with st.sidebar:
            st.markdown("### COMMAND FILTERS")
            mode = st.radio("Search Mode", ["Global Intelligence", "Field Filter"])
            scol = st.selectbox("Choose Field", df.columns, index=1) if mode == "Field Filter" else None
            query = st.text_input("Type keyword", placeholder="Enter terms...")

        res = df
        if query:
            if mode == "Global Intelligence":
                res = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
            else:
                res = df[df[scol].astype(str).str.contains(query, case=False, na=False)]

        tab_db, tab_analytics = st.tabs(["📋 MASTER DATABASE", "📈 ANALYTICS"])

        with tab_db:
            st.markdown(f'<div class="metric-badge">● {len(res)} ACTIVE AGENTS IDENTIFIED</div>', unsafe_allow_html=True)
            st.dataframe(res, use_container_width=True, hide_index=True)
            
            if not res.empty:
                st.markdown("---")
                st.markdown("### 🔍 PROFILE DOSSIER")
                d1, d2 = st.columns([3, 1])
                with d1:
                    choice = st.selectbox("Select Agent:", res['Firm Name'].unique())
                    row = res[res['Firm Name'] == choice].iloc[0]
                with d2:
                    st.write("<br>", unsafe_allow_html=True)
                    dossier_content = generate_dossier_text(row, group_map, all_groups)
                    st.download_button(label="📥 DOWNLOAD DOSSIER", data=dossier_content, file_name=f"Kyrix_{choice.replace(' ','_')}.txt", mime="text/plain")

                col_left, col_right = st.columns(2)
                for idx, group_name in enumerate(all_groups):
                    target_col = col_left if idx % 2 == 0 else col_right
                    with target_col:
                        is_enriched = "Enriched" in group_name
                        st.markdown(f'<div class="section-header {"special-banner" if is_enriched else "dynamic-banner"}">{group_name}</div>', unsafe_allow_html=True)
                        
                        # Filter columns for this group
                        group_cols = [c for c, g in group_map.items() if g == group_name]
                        
                        # FORCED DISPLAY: If this is the Enriched Data section, ensure these two are included
                        if is_enriched:
                            priority_fields = ["Harmonized Phone Number", "Address from License"]
                            for pf in priority_fields:
                                if pf in row and pf not in group_cols:
                                    group_cols.insert(0, pf) # Inject them if they aren't already grouped here

                        for col in group_cols:
                            if "Unnamed" in col or col not in row: continue
                            val = row[col] if pd.notna(row[col]) else "—"
                            
                            style = "value-text"
                            if col == "Harmonized Phone Number":
                                val = harmonize_phone_strict(val)
                                style = "value-text priority-value"
                            
                            st.markdown(f"""
                                <div class='data-card'>
                                    <div class='label-text'>{col}</div>
                                    <div class='{style}'>{val}</div>
                                </div>
                            """, unsafe_allow_html=True)
