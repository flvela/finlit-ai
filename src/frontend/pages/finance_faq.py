"""Finance FAQ page"""
import json

import streamlit as st
from frontend.utils.common import FINANCE_ARTICLE_FILES

st.header("FinLit Financial FAQ articles", text_alignment="center")
st.set_page_config(layout="wide")

articles = []
for file in FINANCE_ARTICLE_FILES:
  with open(file, 'r', encoding='utf-8') as file:
    articles.extend(json.load(file))
st.dataframe(data=articles)
