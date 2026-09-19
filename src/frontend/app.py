"""Main page of the streamlit application"""
import streamlit as st

from frontend.components.ui_config import UIConfig

assistant_page = st.Page("pages/chat.py", title="Assistant", icon=":material/support_agent:")
finance_faq_page = st.Page("pages/finance_faq.py", title="Financial FAQ", icon=":material/menu_book:")
page = st.navigation([assistant_page, finance_faq_page])

ui_config = UIConfig()
ui_config.show_config_sidebar()

page.run()
