"""common components used by multiple pages"""
from datetime import datetime

import streamlit as st
import pandas as pd

# news response keys
FEED_KEY = "feed"
NEWS_PAGINATION_KEY = "news_pagination"
TITLE_KEY = "title"
URL_KEY = "link"
TIME_PUBLISHED_KEY = "providerPublishTime"
PUBLISHER_KEY = "publisher"
RELATED_TICKERS_KEY = "relatedTickers"


def create_news_page_container(news_slot_container, news_df):
  """creates the container to display news page data"""
  table_data = []
  for _, row in news_df.iterrows():
    related_tickers = " ".join(f":gray-badge[{ticker}]" for ticker in row[RELATED_TICKERS_KEY])
    link_markdown = f"[{row[TITLE_KEY]}]({row[URL_KEY]})\n\n{related_tickers}"
    datetime.fromtimestamp(row[TIME_PUBLISHED_KEY])
    published_date = datetime.fromtimestamp(row[TIME_PUBLISHED_KEY]).strftime("%b %d, %Y %H:%M")
    source_date = f"\n\n:gray[{row[PUBLISHER_KEY]}]\n\n{published_date}"
    table_data.append((link_markdown, source_date))
  news_slot_container.table(table_data, border="horizontal", width="stretch")


def create_news_feed_df_container(news_feed_df: pd.DataFrame, news_per_page: int, unique_key: str):
  """creates the news feed container from given data frame. A unique key must be provided for pagination component"""
  total_pages = (len(news_feed_df) + news_per_page - 1)//news_per_page
  news_container = st.container(width="stretch")
  with st.container(horizontal_alignment="right", width="stretch"):
    page = st.pagination(key=f"{NEWS_PAGINATION_KEY}_{unique_key}", num_pages=total_pages)

  start_idx = (page - 1) * news_per_page
  end_idx = start_idx + news_per_page
  create_news_page_container(news_container, news_feed_df.iloc[start_idx: end_idx])
