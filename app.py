import streamlit as st
import pandas as pd
import os
import glob
import numpy as np
import re
from datetime import datetime
from fpdf import FPDF

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
    .logo-container { display: flex; justify-content: center; padding: 20px 0; }
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
        border: 1px solid #475569; border-bottom: none;
    }
    .dynamic-banner { background: linear-gradient(90deg, #1E293B 0%, #334155 100%); color: #CBD5E1 !important; }
    .special-banner { background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%); color: #FFFFFF !important; }
    .data-card { 
        background-color: #111827; padding: 14px; 
        border: 1px solid #1F2937; border-bottom: 1px solid #374151;
    }
    .label-text { font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
    .value-text { font-size: 14px; color: #F8FAFC; font-weight: 500; }
    .priority-value { color: #F59E0B !important; font-weight: 700; font-family: 'Courier New', monospace; }
    
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1E293B; }
    .stTabs [aria-selected="true"] { background-color: #3B82F6 !important; color: #FFFFFF !important; }
    .stDownloadButton button {
        background-color: #F59E0B !important; color: #0F172A !important;
        font-weight: 700 !important; border: none !important; width: 100%; margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF ENGINE ---
class KyrixPDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(30, 64, 175) # Dark Blue
        self.cell(80)
        self.cell(30, 10, 'INTELLIGENCE DOSSIER', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Kyrix Intangible - Page {self.page_no()} - {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')

def create_pdf(row, group_map, all_groups):
    pdf = KyrixPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for group in all_groups:
        # Styling for headers
        is_enriched = "Enriched" in group
        if is_enriched:
            pdf.set_fill_color(30, 64, 175) # Blue
            pdf.set_text_color(255, 255, 255)
        else:
            pdf.set_fill_color(30, 41, 59) # Dark Slate
            pdf.set_text_color(241, 245, 249)
            
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f" {group.upper()}", 0, 1, 'L', True)
        pdf.ln(2)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        
        group_cols = [c for c, g in group_map.items() if g == group]
        for col in group_cols:
            if col in row:
                val = str(row[col]) if pd.notna(row[col]) else "—"
                # Multi-line handling for notes
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(50, 7, f"{col}:", 0, 0)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 7, val)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DATA ENGINE (Utilities from V13.9) ---
@st.cache_data
def load_data():
    path = "Data Structure - Registered Agents in UAE (Kyrix Intangible) - Enriched Data 2.0.csv"
    if not os.path.exists(path): return None, None, []
    g_row = pd.read_csv(path, skiprows=1, nrows=1, header=None).iloc[0].tolist()
    h_row = pd.read_csv(path, skiprows=2, nrows=1, header=None).iloc[0].tolist()
    df = pd.read_csv(path, skiprows=2)
    df.columns = df.columns.str.strip()
    actual_cols = df.columns.tolist()
    current_group, group_map, all_groups = "General Info", {}, []
    for i, h in enumerate(h_row):
        g = str(g_row[i]) if i < len(g_row) and pd.notna(g_row[i]) else None
        if g and g.strip() and g.lower() != 'nan': current_group = g.strip()
        if current_group not in all_groups: all_groups.append(current_group)
        if i < len(actual_cols): group_map[actual_cols[i]] = current_group
    df = df[df['Firm Name'].notna()].copy()
    df = df[~df['Firm Name'].str.contains("Firm Name|ENRICHED|CONTACTS|ADDITIONAL|DATA", na=False, case=False)]
    return df, group_map, all_groups

# --- 5. APP LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # (Authorization Screen)
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        st.markdown('<div style="background:#1E293B; padding:50px; border-radius:12px; border:1px solid #334155; text-align:center;">', unsafe_allow_html=True)
        st.markdown("<h2>KYRIX ACCESS</h2>", unsafe_allow_html=True)
        key = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            if key == "Kyrix2024": st.session_state.auth = True; st.rerun()
            else: st.error("Unauthorized Access")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    if os.path.exists("logo.png"):
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("logo.png", width=300)
        st.markdown('</div>', unsafe_allow_html=True)

    df, group_map, all_groups = load_data()
    if df is not None:
        with st.sidebar:
            st.markdown("### COMMAND FILTERS")
            search_mode = st.radio("Search Mode", ["Global Intelligence", "Field Filter"])
            scol = st.selectbox("Choose Field", df.columns, index=1) if search_mode == "Field Filter" else None
            query = st.text_input("Type keyword", placeholder="Enter terms...")
            st.caption("KYRIX COMMAND CENTER V14.0")

        # Filtering Logic
        if query:
            if search_mode == "Global Intelligence":
                mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
            else:
                mask = df[scol].astype(str).str.contains(query, case=False, na=False)
            res = df[mask]
        else: res = df

        st.markdown(f'<div class="metric-badge">● {len(res)} ACTIVE AGENTS IDENTIFIED</div>', unsafe_allow_html=True)
        tab_db, tab_map, tab_analytics = st.tabs(["📋 DATABASE", "📍 LIVE NETWORK MAP", "📈 ANALYTICS"])

        with tab_db:
            st.dataframe(res, use_container_width=True, hide_index=True)
            if not res.empty:
                st.markdown("---")
                d1, d2 = st.columns([3, 1])
                with d1:
                    st.markdown("### 🔍 COMPREHENSIVE PROFILE DOSSIER")
                    choice = st.selectbox("Select Profile:", res['Firm Name'].unique())
                    row = res[res['Firm Name'] == choice].iloc[0]
                with d2:
                    # PDF GENERATION TRIGGER
                    pdf_bytes = create_pdf(row, group_map, all_groups)
                    st.download_button(
                        label="📄 DOWNLOAD PDF DOSSIER",
                        data=pdf_bytes,
                        file_name=f"Kyrix_Dossier_{choice.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )

                # UI Display (Data Cards)
                col_left, col_right = st.columns(2)
                for idx, group_name in enumerate(all_groups):
                    target_col = col_left if idx % 2 == 0 else col_right
                    with target_col:
                        is_enriched = "Enriched" in group_name
                        banner_class = "special-banner" if is_enriched else "dynamic-banner"
                        st.markdown(f'<div class="section-header {banner_class}">{group_name}</div>', unsafe_allow_html=True)
                        group_cols = [c for c, g in group_map.items() if g == group_name]
                        for col in group_cols:
                            if "Unnamed" in col or col in ["Address from License", "Harmonized Phone Number"]: continue
                            if col in row:
                                val = row[col] if pd.notna(row[col]) else "—"
                                st.markdown(f"<div class='data-card'><div class='label-text'>{col}</div><div class='value-text'>{val}</div></div>", unsafe_allow_html=True)
