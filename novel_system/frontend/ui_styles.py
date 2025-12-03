import streamlit as st


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
        :root {
            --bg: #0e1116;
            --panel: rgba(255,255,255,0.04);
            --muted: #9aa2b1;
            --accent: #7c8cff;
            --accent-2: #74d4ff;
            --border: rgba(255,255,255,0.08);
        }
        body, input, textarea, select, button {
            font-family: 'Space Grotesk', 'IBM Plex Sans', sans-serif;
            color: #e7ecf5;
        }
        .block-container { padding-top: 1.25rem; }
        .glass-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 14px 50px rgba(0,0,0,0.22);
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.35rem 0.7rem;
            border-radius: 12px;
            background: rgba(124,140,255,0.18);
            color: #e7ecf5;
            font-size: 0.85rem;
            margin-right: 0.35rem;
        }
        .muted { color: var(--muted); font-size: 0.9rem; }
        .metric-card {
            padding: 0.75rem 1rem;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
        }
        .status-bar {
            padding: 0.65rem 0.9rem;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: linear-gradient(120deg, rgba(124,140,255,0.14), rgba(116,212,255,0.08));
            font-size: 0.95rem;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #7c8cff;
            box-shadow: 0 0 0 6px rgba(124,140,255,0.2);
        }
        .step-list { padding-left: 1.2rem; line-height: 1.6; }
        .step-list li { margin-bottom: 0.4rem; }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        </style>
        """,
        unsafe_allow_html=True,
    )
