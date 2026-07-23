import streamlit as st

def apply_custom_css():
    """
    Applies modern, rich, state-of-the-art UI styling.
    Includes custom dark/light glassmorphic cards, gradient headers, and badges.
    """
    st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #312E81 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.2);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #38BDF8;
    }

    .metric-label {
        font-size: 0.875rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Agent Communication Badge */
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #1E293B;
        color: #38BDF8;
        border: 1px solid #334155;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .agent-log-box {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #38BDF8;
        max-height: 250px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)
