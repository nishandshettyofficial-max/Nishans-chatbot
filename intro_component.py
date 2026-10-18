"""
intro_component.py
Reusable Streamlit component that renders the full-screen cinematic intro animation
with particle formation of Nishan's portrait, ambient stars, signature curves,
and luxury typography inspired by Vadim Carazan's digital experience.
"""

import os
import streamlit as st
import streamlit.components.v1 as components

COMPONENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "components", "cinematic_intro"))

# Declare Streamlit custom component from the local directory
_component_func = components.declare_component("cinematic_intro", path=COMPONENT_DIR)


def render_cinematic_intro(key: str = "cinematic_intro"):
    """
    Renders the cinematic particle intro.
    Returns a dict with {"action": "entered"} when the user clicks 'Enter Chatbot'
    or presses Enter.
    """
    return _component_func(key=key, default=None)
