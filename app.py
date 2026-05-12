import base64
import logging
from pathlib import Path

import streamlit as st

from config import get_settings
from models import RecommendError
from services.gemini import GeminiClient
from services.tmdb import TMDBClient
from services.recommender import recommend

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("chatflix")

SYSTEM_PROMPT = Path("prompts/system.txt").read_text(encoding="utf-8")
POSTER_FALLBACK_PATH = Path("assets/poster_fallback.png")

CSS = """
<style>
  .stApp { background: #000; }
  section.main > div { padding-top: 1rem; }

  .cf-brand {
    color: #a855f7; letter-spacing: 3px; font-size: 11px;
    font-weight: 600; text-align: center; margin-bottom: 32px;
  }
  .cf-hero-title {
    font-size: 44px; font-weight: 700; text-align: center; line-height: 1.1;
    margin: 24px 0 8px;
    background: linear-gradient(135deg, #c084fc 0%, #7c3aed 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .cf-hero-sub {
    color: #888; font-size: 14px; text-align: center; margin-bottom: 28px;
  }

  .stTextInput > div > div > input {
    background: #0f0a1a; border: 1px solid #2d1b4e; border-radius: 10px;
    color: #ddd; padding: 14px 16px; font-size: 14px;
  }
  .stTextInput > div > div > input:focus {
    border-color: #7c3aed; box-shadow: 0 0 0 2px rgba(124,58,237,0.25);
  }

  .stButton > button {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    color: #fff; border: none; padding: 10px 28px;
    border-radius: 10px; font-size: 14px; font-weight: 600;
    box-shadow: 0 4px 12px rgba(124,58,237,0.35);
    transition: all 180ms ease-out;
  }
  .stButton > button:hover {
    filter: brightness(1.08);
    box-shadow: 0 6px 16px rgba(124,58,237,0.45);
  }
  .stButton > button:active { transform: translateY(1px); }

  .cf-card {
    background: linear-gradient(180deg, #0f0a1a, #0a0612);
    border: 1px solid #2d1b4e; border-radius: 14px;
    padding: 24px; margin-top: 24px;
    display: flex; gap: 20px;
  }
  .cf-poster {
    width: 140px; height: 210px; object-fit: cover;
    border-radius: 8px; flex-shrink: 0;
    box-shadow: 0 6px 16px rgba(124,58,237,0.25);
  }
  .cf-card-body { flex: 1; min-width: 0; color: #ddd; }
  .cf-title { font-size: 22px; font-weight: 700; color: #fff; margin: 0 0 4px; }
  .cf-meta { color: #888; font-size: 12px; margin-bottom: 12px; }
  .cf-meta strong { color: #c084fc; }
  .cf-genre-pill {
    display: inline-block; background: #1a0f2e; border: 1px solid #3d2a5e;
    color: #c084fc; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; margin-right: 6px; margin-bottom: 4px;
  }
  .cf-syn { font-size: 13px; line-height: 1.6; margin: 12px 0; }
  .cf-just-label {
    color: #a855f7; font-size: 10px; letter-spacing: 2px;
    font-weight: 600; margin: 8px 0 4px;
  }
  .cf-just { font-size: 13px; line-height: 1.6; font-style: italic; color: #ddd; }

  .cf-error {
    background: #2a0f0f; border: 1px solid #7c1d1d; color: #fca5a5;
    padding: 12px 16px; border-radius: 10px; margin: 16px auto;
    max-width: 560px; text-align: center; font-size: 13px;
  }
</style>
"""


def init_session_state():
    st.session_state.setdefault("excluded_titles", [])
    st.session_state.setdefault("last_card", None)
    st.session_state.setdefault("last_prompt", "")
    st.session_state.setdefault("error", None)


def main():
    st.set_page_config(page_title="Chatflix", page_icon=":clapper:", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    init_session_state()

    st.markdown('<div class="cf-brand">CHATFLIX</div>', unsafe_allow_html=True)

    if st.session_state.last_card is None:
        st.markdown('<h1 class="cf-hero-title">Que filme<br>você procura?</h1>', unsafe_allow_html=True)
        st.markdown('<p class="cf-hero-sub">Descreva clima, humor, atmosfera ou tema</p>', unsafe_allow_html=True)

    if st.session_state.error:
        st.markdown(f'<div class="cf-error">{st.session_state.error}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
