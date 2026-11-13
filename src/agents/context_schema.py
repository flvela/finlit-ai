"""Shared context schema definition for the LangGraph runtime"""

from dataclasses import dataclass
from typing import List

from langchain.chat_models import BaseChatModel
from langchain.tools import BaseTool
from langchain_chroma import Chroma

from agents.analysis_tools import (
  get_global_quote,
  get_portfolio_summary,
  get_ticker_overview,
  get_time_series_daily,
  get_treasury_yield
)
from tools.articles import search_finance_articles
from tools.market_manager import MarketManager
from tools.portfolio_manager import PortfolioManager


@dataclass
class LLMTools:
  """contains LLM tools for context schema"""
  # the financial faq tools
  financial_faq_tools: List[BaseTool]
  # portfolio tools
  portfolio_tools: List[BaseTool]


@dataclass
class ContextSchema:
  """Graph Runtime Context Schema"""
  # the financial article chroma collection
  article_collection: Chroma
  # the llm used to process/generate data
  llm: BaseChatModel
  # llm tools used by agents
  llm_tools: LLMTools
  # the financial faq llm
  financial_faq_llm: BaseChatModel
  # portfolio manager
  portfolio_manager: PortfolioManager
  # portfolio llm
  portfolio_llm: BaseChatModel
  # market manager
  market_manager: MarketManager

  def __init__(self, article_collection: Chroma, llm: BaseChatModel, portfolio_manager: PortfolioManager,
               market_manager: MarketManager):
    self.article_collection = article_collection
    self.llm = llm
    financial_faq_tools = [search_finance_articles]
    portfolio_tools = [get_time_series_daily, get_global_quote, get_treasury_yield,
                       get_ticker_overview, get_portfolio_summary]
    self.llm_tools = LLMTools(financial_faq_tools=financial_faq_tools, portfolio_tools=portfolio_tools)
    self.financial_faq_llm = llm.bind_tools(self.llm_tools.financial_faq_tools)
    self.portfolio_manager = portfolio_manager
    self.portfolio_llm = llm.bind_tools(self.llm_tools.portfolio_tools)
    self.market_manager = market_manager
