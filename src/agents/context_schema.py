"""Shared context schema definition for the LangGraph runtime"""

from dataclasses import dataclass
from typing import List

from langchain.chat_models import BaseChatModel
from langchain.tools import BaseTool
from langchain_chroma import Chroma
from tools.articles import search_finance_articles


@dataclass
class ContextSchema:
  """Graph Runtime Context Schema"""
  # the financial article chroma collection
  article_collection: Chroma
  # the llm used to process/generate data
  llm: BaseChatModel
  # the financial faq llm
  financial_faq_llm: BaseChatModel
  # the financial faq tools
  financial_faq_tools: List[BaseTool]

  def __init__(self, article_collection: Chroma, llm: BaseChatModel):
    self.article_collection = article_collection
    self.llm = llm
    self.financial_faq_tools = [search_finance_articles]
    self.financial_faq_llm = llm.bind_tools(self.financial_faq_tools)
