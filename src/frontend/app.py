"""Main page of the streamlit application"""
import streamlit as st

from frontend.components.ui_config import UIConfig

assistant_page = st.Page("pages/chat.py", title="Assistant", icon=":material/support_agent:")
finance_faq_page = st.Page("pages/finance_faq.py", title="Financial FAQ", icon=":material/menu_book:")
accounts_page = st.Page("pages/accounts.py", title="Accounts & Trade", icon=":material/account_balance:")
page = st.navigation([assistant_page, finance_faq_page, accounts_page])

ui_config = UIConfig()
ui_config.show_config_sidebar()

page.run()
