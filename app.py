import streamlit as st
import pandas as pd
import os
import glob
import numpy as np
from datetime import datetime

# --- 1. CRITICAL DIAGNOSTIC IMPORT ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly
    plotly_loaded = True
    import_error = None
except Exception as e:
    plotly_loaded = False
    import_error = str(e)

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="Kyrix | Intelligence Command",
    page_icon="🛡️",
    layout="wide"
)

# --- 3. LUXURY DARK THEME CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; } 
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #F1F5F9 !important; font-family: 'Inter', sans-serif; }
    .metric-badge {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: #F59E0B !important;
        padding: 15px 30px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 20px;
        border: 1px solid #334155;
        display: inline-block;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 13px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase;
        padding: 12px 20px; border-radius: 8px 8px 0 0; margin-top: 25px;
        border: 1px solid #475569;
    }
    .dynamic-banner { background: linear-gradient(90deg, #1E293B 0%, #334155 100%); color: #CBD5E1 !important; }
    .special-banner { background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%); color: #FFFFFF !important; }
    
    .data-card { background-color: #1E293B; padding: 16px; border: 1px solid #334155; border-top: none; }
    .label-text { font-size: 10px; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
    .value-text { font-size: 15px; color: #FFFFFF; font-weight: 500; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B; }
    .stTabs [aria-selected="true"] { background-color: #3B82F6 !important; color: #FFFFFF !important; }
    
    .stDownloadButton button {
        background-color: #F59E0B !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
@st.cache_data
def load_data():
    files = glob.glob("*.csv")
    if not files: return None, None, []
    path = files[0]

    g_row = pd.read_csv(path, skiprows=1, nrows=1, header=None).iloc[0].tolist()
    h_row = pd.read_csv(path, skiprows=2, nrows=1, header=None).iloc[0].tolist()
    
    current_group = "General Info"
    group_map = {}
    all_groups = []
    
    for i, h in enumerate(h_row):
        g = str(g_row[i]) if i < len(g_row) and pd.notna(g_row[i]) else None
        if g and g.strip() and g.lower() != 'nan': 
            current_group = g.strip()
        
        if current_group not in all_groups:
            all_groups.append(current_group)
            
        h_clean = str(h).strip()
        if h_clean and h_clean != 'nan':
            group_map[h_clean] = current_group

    df = pd.read_csv(path, skiprows=2)
    df.columns = df.columns.str.strip()
    df = df[df['Firm Name'].notna()].copy()
    df = df[~df['Firm Name'].str.contains("Firm Name|ENRICHED|CONTACTS|ADDITIONAL|DATA", na=False, case=False)]
    
    if 'Rating' in df.columns:
        df['Rating'] = df['Rating'].astype(str).apply(lambda v: "⭐⭐⭐⭐⭐" if '5' in v else "⭐⭐⭐⭐" if '4' in v else "⭐⭐⭐" if '3' in v else "—")

    return df, group_map, all_groups

def generate_dossier_text(row, group_map, all_groups):
    report = f"KYRIX INTELLIGENCE COMMAND | DOSSIER EXPORT\n"
    report += f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "="*50 + "\n\n"
    
    for group in all_groups:
        report += f"[{group.upper()}]\n"
        report += "-"*20 + "\n"
        group_cols = [c for c, g in group_map.items() if g == group]
        for col in group_cols:
            if col in row:
                report += f"{col}: {row[col]}\n"
        report += "\n"
    
    report += "="*50 + "\n"
    report += "END OF DOSSIER"
    return report

# --- 5. APP LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        st.markdown('<div style="background:#1E293B; padding:50px; border-radius:12px; border:1px solid #334155; text-align:center;">', unsafe_allow_html=True)
        st.markdown("<h2>KYRIX ACCESS</h2>", unsafe_allow_html=True)
        key = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if key == "Kyrix2024":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Unauthorized Access")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    df, group_map, all_groups = load_data()
    
    if df is not None:
        with st.sidebar:
            st.write("<br>")
            if os.path.exists("logo.png"): st.image("logo.png")
            st.markdown("### COMMAND FILTERS")
            scol = st.selectbox("Search Field", df.columns, index=1 if len(df.columns) > 1 else 0)
            query = st.text_input("Enter Keywords...")
            st.write("---")
            st.caption("KYRIX COMMAND CENTER V12.2")

        mask = df[scol].astype(str).str.contains(query, case=False, na=False)
        res = df[mask]
        st.markdown(f'<div class="metric-badge">● {len(res)} ACTIVE AGENTS IDENTIFIED</div>', unsafe_allow_html=True)

        tab_db, tab_map, tab_analytics = st.tabs(["📋 DATABASE", "📍 LIVE NETWORK MAP", "📈 ANALYTICS"])

        with tab_db:
            st.dataframe(res, use_container_width=True, hide_index=True)
            
            if not res.empty:
                st.markdown("---")
                d1, d2 = st.columns([3, 1])
                with d1:
                    st.markdown("### 🔍 COMPREHENSIVE PROFILE DOSSIER")
                    choice = st.selectbox("Expand Intelligence Profile:", res['Firm Name'].unique())
                
                row = res[res['Firm Name'] == choice].iloc[0]
                
                with d2:
                    st.write("<br><br>", unsafe_allow_html=True)
                    dossier_content = generate_dossier_text(row, group_map, all_groups)
                    st.download_button(
                        label="📥 DOWNLOAD DOSSIER",
                        data=dossier_content,
                        file_name=f"Kyrix_Dossier_{choice.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

                col_left, col_right = st.columns(2)
                
                # Identify special fields for placement
                special_fields = ["Address of License", "Harmonized Phone Number"]

                for idx, group_name in enumerate(all_groups):
                    target_col = col_left if idx % 2 == 0 else col_right
                    with target_col:
                        banner_class = "special-banner" if "Enriched" in group_name else "dynamic-banner"
                        st.markdown(f'<div class="section-header {banner_class}">{group_name}</div>', unsafe_allow_html=True)
                        
                        group_cols = [c for c, g in group_map.items() if g == group_name]
                        
                        # Display regular columns for this group
                        for col in group_cols:
                            # Skip the special fields if we are in the Enriched group, we'll append them at the end
                            if col in row and "Unnamed" not in col and col not in special_fields:
                                val = row[col] if pd.notna(row[col]) else "—"
                                st.markdown(f"<div class='data-card'><div class='label-text'>{col}</div><div class='value-text'>{val}</div></div>", unsafe_allow_html=True)
                        
                        # IF this is the ENRICHED section, append the specific fields at the bottom
                        if "Enriched" in group_name:
                            for spec in special_fields:
                                if spec in row:
                                    val = row[spec] if pd.notna(row[spec]) else "—"
                                    st.markdown(f"<div class='data-card' style='border-left: 3px solid #F59E0B;'><div class='label-text'>{spec}</div><div class='value-text'>{val}</div></div>", unsafe_allow_html=True)

        with tab_map:
            if plotly_loaded:
                coords = {"Dubai": [25.2, 55.27], "Abu Dhabi": [24.45, 54.37], "Sharjah": [25.34, 55.42], "Ajman": [25.40, 55.44]}
                m_df = res.copy()
                if 'Emirate' in m_df.columns:
                    m_df['lat'] = m_df['Emirate'].map(lambda x: coords.get(str(x).strip(), [25.2, 55.2])[0]) + np.random.uniform(-0.01, 0.01, len(m_df))
                    m_df['lon'] = m_df['Emirate'].map(lambda x: coords.get(str(x).strip(), [25.2, 55.2])[1]) + np.random.uniform(-0.01, 0.01, len(m_df))
                    fig = px.scatter_mapbox(m_df, lat="lat", lon="lon", hover_name="Firm Name", zoom=7, height=600, color_discrete_sequence=["#3B82F6"])
                    fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Plotly load failed.")

        with tab_analytics:
            if plotly_loaded:
                ca, cb = st.columns(2)
                with ca:
                    if 'Emirate' in df.columns:
                        valid_em = df[df['Emirate'].astype(str).str.strip().isin(coords.keys())]
                        st.plotly_chart(px.bar(valid_em['Emirate'].value_counts().reset_index(), x='Emirate', y='count', title="Regional Hubs", template="plotly_dark"), use_container_width=True)
                with cb:
                    if 'Firm Type' in df.columns:
                        valid_ft = df[~df['Firm Type'].astype(str).str.contains("nan|Firm Type", na=True)]
                        st.plotly_chart(px.pie(valid_ft['Firm Type'].value_counts().reset_index(), values='count', names='Firm Type', title="Market Split", hole=0.4, template="plotly_dark"), use_container_width=True)
