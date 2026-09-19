"""Finance FAQ page"""
import json

import streamlit as st
from frontend.utils.common import (
  CONFIG_ERROR_MESSAGE,
  FINANCE_ARTICLE_FILES,
  FINANCE_ARTICLE_FILES_CONFIG
)


st.header("FinLit Financial FAQ articles", text_alignment="center")
st.divider()


if FINANCE_ARTICLE_FILES_CONFIG in st.session_state and st.session_state[FINANCE_ARTICLE_FILES_CONFIG] is not None:
  financial_article_files = st.session_state[FINANCE_ARTICLE_FILES_CONFIG]
  articles = []
  for file in financial_article_files:
    with open(file, 'r', encoding='utf-8') as file:
      articles.extend(json.load(file))
  st.dataframe(data=articles)
else:
  if CONFIG_ERROR_MESSAGE in st.session_state:
    st.error(st.session_state[CONFIG_ERROR_MESSAGE])
  st.warning(f"Unable to load financial article files {FINANCE_ARTICLE_FILES}\n {st.session_state}\n")
