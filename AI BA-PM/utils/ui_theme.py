import streamlit as st

def inject_theme():
    st.markdown("""
    <style>
      /* ── Premium AI SaaS Dark Theme ── */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
      
      /* Hide Streamlit Default Elements */
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      header {visibility: hidden;}
      
      html, body, [class*="css"] {
          font-family: 'Inter', sans-serif !important;
      }

      /* Base App Gradient / Pattern */
      .stApp {
          background-color: #0f172a !important;
          background-image: radial-gradient(circle at 15% 50%, rgba(79, 70, 229, 0.08), transparent 25%),
                            radial-gradient(circle at 85% 30%, rgba(126, 34, 206, 0.08), transparent 25%) !important;
      }

      /* Sidebar styling */
      [data-testid="stSidebar"] {
          background-color: #0b0f19 !important;
          border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
      }

      /* Global Card / Surface Mixin */
      .vision-card, .stat-box, .quota-bar, .admin-header, .artifact-card, .export-bar, [data-testid="stExpander"] {
          background-color: #1e293b !important;
          border: 1px solid rgba(255, 255, 255, 0.06) !important;
          border-radius: 14px !important;
          box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2) !important;
      }

      /* Specific adjustments for Expander native component */
      [data-testid="stExpander"] summary {
          color: #f8fafc !important;
          font-weight: 600 !important;
          border-bottom: 1px solid rgba(255,255,255,0.05);
      }
      [data-testid="stExpanderDetails"] { padding-top: 1rem; }

      /* Primary Buttons (Indigo/Purple Gradient) */
      div[data-testid="stButton"] button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
          background: linear-gradient(135deg, #4f46e5, #7e22ce) !important;
          border: none !important;
          border-radius: 10px !important;
          color: white !important;
          font-weight: 600 !important;
          box-shadow: 0px 4px 14px rgba(79, 70, 229, 0.3) !important;
          transition: all 0.2s ease !important;
          letter-spacing: 0.02em !important;
      }
      div[data-testid="stButton"] button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
          transform: translateY(-2px) !important;
          box-shadow: 0px 6px 20px rgba(126, 34, 206, 0.5) !important;
      }

      /* Secondary Buttons */
      div[data-testid="stButton"] button[kind="secondary"] {
          background: rgba(30, 41, 59, 0.8) !important;
          border: 1px solid rgba(255, 255, 255, 0.1) !important;
          border-radius: 10px !important;
          color: #f8fafc !important;
          font-weight: 500 !important;
          transition: all 0.2s ease !important;
      }
      div[data-testid="stButton"] button[kind="secondary"]:hover {
          background: rgba(79, 70, 229, 0.1) !important;
          border-color: #6366f1 !important;
          color: #e0e7ff !important;
      }

      /* Inputs, TextAreas, SelectBoxes */
      .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
          background-color: #0f172a !important;
          border: 1px solid rgba(255, 255, 255, 0.1) !important;
          border-radius: 10px !important;
          color: #f8fafc !important;
          transition: border-color 0.2s ease;
      }
      .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox [data-baseweb="select"]:focus-within {
          border-color: #6366f1 !important;
          box-shadow: 0 0 0 1px #6366f1 !important;
      }

      /* Native Tables */
      table { border-collapse: separate; border-spacing: 0; width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05); }
      th { background-color: #1e293b !important; color: #a5b4fc !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; font-weight: 600 !important; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 12px 16px !important; }
      td { background-color: #0f172a !important; color: #cbd5e1 !important; border-bottom: 1px solid rgba(255,255,255,0.02) !important; padding: 12px 16px !important; font-size: 0.9rem; }

      /* Streamlit Tabs */
      .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.05); }
      .stTabs [data-baseweb="tab"] { font-size: 0.95rem; font-weight: 500; color: #94a3b8; border-radius: 8px 8px 0 0; border: none; background: transparent; transition: all 0.2s; }
      .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #f8fafc !important; border-bottom: 2px solid #818cf8 !important; background: transparent !important; }
      
      /* Progress bar */
      .stProgress > div > div > div { background: linear-gradient(90deg, #4f46e5, #a855f7) !important; }

      /* ── Custom App Classes ── */
      
      /* app.py */
      .main-header { text-align: center; padding: 2.5rem 0 1.5rem; }
      .main-header h1 { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #a5b4fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
      .main-header p { color: #94a3b8; font-size: 1.15rem; margin-top: 0; }
      .feature-pill { display: inline-block; background: rgba(99, 102, 241, 0.1); color: #818cf8; padding: 6px 14px; border-radius: 24px; font-size: 0.85rem; font-weight: 500; margin: 4px; border: 1px solid rgba(99, 102, 241, 0.2); }
      .stat-box { padding: 1.5rem; text-align: center; } 
      .stat-box h3 { font-size: 2.2rem; color: #a5b4fc; margin: 0; font-weight: 700; }
      .stat-box p { color: #94a3b8; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; padding-top: 4px; }

      /* 01_Generate.py */
      .gen-header h2 { color: #f8fafc; margin-bottom: 0; font-weight: 700; letter-spacing: -0.01em; }
      .gen-header p  { color: #94a3b8; margin-top: 6px; }
      .step-label    { font-weight: 600; color: #818cf8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.8rem; display: inline-block; background: rgba(99,102,241,0.1); padding: 4px 10px; border-radius: 6px; }
      .quota-bar     { padding: 1rem 1.5rem; margin-bottom: 1rem; color: #e2e8f0; font-size: 0.95rem; }
      .voice-tip     { background: rgba(99,102,241,0.08); border-left: 3px solid #6366f1; padding: 0.8rem 1.2rem; border-radius: 0 8px 8px 0; color: #cbd5e1; font-size: 0.9rem; margin-bottom: 1rem; }

      /* 02_Document.py */
      .artifact-card { padding: 1.8rem; margin-bottom: 1.5rem; }
      .section-title { color: #818cf8; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; }
      .confidence-high   { color: #34d399; font-size: 0.75rem; font-weight: 600; padding: 3px 10px; background: rgba(16, 185, 129, 0.1); border-radius: 20px; border: 1px solid rgba(16,185,129,0.2); }
      .confidence-medium { color: #fbbf24; font-size: 0.75rem; font-weight: 600; padding: 3px 10px; background: rgba(245, 158, 11, 0.1); border-radius: 20px; border: 1px solid rgba(245,158,11,0.2); }
      .confidence-low    { color: #f87171; font-size: 0.75rem; font-weight: 600; padding: 3px 10px; background: rgba(239, 68, 68, 0.1); border-radius: 20px; border: 1px solid rgba(239,68,68,0.2); }
      .severity-HIGH   { background: rgba(239, 68, 68, 0.15); color: #fca5a5; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(239,68,68,0.3); }
      .severity-MEDIUM { background: rgba(245, 158, 11, 0.15); color: #fde68a; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(245,158,11,0.3); }
      .severity-LOW    { background: rgba(16, 185, 129, 0.15); color: #a7f3d0; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(16,185,129,0.3); }
      .export-bar { padding: 1.5rem; margin-top: 1rem; text-align: center; }

      /* 05_Admin.py */
      .admin-header { padding: 1.8rem; margin-bottom: 1.5rem; display: flex; flex-direction: column; background: linear-gradient(135deg, #1e1b4b, #312e81) !important; border: 1px solid rgba(99,102,241,0.2) !important; }
      .admin-header h1 { color: #f8fafc; margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.01em; }
      .admin-header p  { color: #a5b4fc; margin: 0; font-size: 0.95rem; margin-top: 4px; }
      .stat-val  { font-size: 2.4rem; font-weight: 700; color: #a5b4fc; }
      .stat-lbl  { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }
      .badge-admin { background: rgba(139, 92, 246, 0.15); color: #c4b5fd; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(139,92,246,0.3); }
      .badge-pro   { background: rgba(14, 165, 233, 0.15); color: #7dd3fc; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(14,165,233,0.3); }
      .badge-free  { background: rgba(100, 116, 139, 0.15); color: #cbd5e1; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; border: 1px solid rgba(100,116,139,0.3); }
    </style>
    """, unsafe_allow_html=True)
