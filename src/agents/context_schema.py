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
  get_treasury_yield,
  get_us_finance_sector_data,
  get_us_market_indices,
  search_finance_market_news
)
from tools.articles import search_finance_articles
from tools.market_manager import MarketManager
from tools.portfolio_manager import PortfolioManager


@dataclass
class ContextLLMTools:
  """contains LLM tools for context schema"""
  # the financial faq tools
  financial_faq_tools: List[BaseTool]
  # portfolio tools
  portfolio_tools: List[BaseTool]
  # market analysis tools
  market_analysis_tools: List[BaseTool]


@dataclass
class ContextLLMs:
  """contains the different LLMs for context schema"""
  # the llm used to process/generate data
  llm: BaseChatModel
  # the financial faq llm
  financial_faq_llm: BaseChatModel
  # portfolio llm
  portfolio_llm: BaseChatModel
  # market analysis llm
  market_analysis_llm: BaseChatModel


@dataclass
class ContextSchema:
  """Graph Runtime Context Schema"""
  # the financial article chroma collection
  article_collection: Chroma
  # the llm used to process/generate data
  llms: ContextLLMs
  # llm tools used by agents
  llm_tools: ContextLLMTools
  # portfolio manager
  portfolio_manager: PortfolioManager
  # market manager
  market_manager: MarketManager

  def __init__(self, article_collection: Chroma, llm: BaseChatModel, portfolio_manager: PortfolioManager,
               market_manager: MarketManager):
    self.article_collection = article_collection
    financial_faq_tools = [search_finance_articles]
    portfolio_tools = [get_time_series_daily, get_global_quote, get_treasury_yield,
                       get_ticker_overview, get_portfolio_summary]
    maker_analysis_tools = [get_ticker_overview, get_us_market_indices, search_finance_market_news,
                            get_us_finance_sector_data]
    self.llm_tools = ContextLLMTools(financial_faq_tools=financial_faq_tools,
                                     portfolio_tools=portfolio_tools,
                                     market_analysis_tools=maker_analysis_tools)
    financial_faq_llm = llm.bind_tools(self.llm_tools.financial_faq_tools)
    portfolio_llm = llm.bind_tools(self.llm_tools.portfolio_tools)
    market_analysis_llm = llm.bind_tools(self.llm_tools.market_analysis_tools)
    self.llms = ContextLLMs(llm=llm,
                            financial_faq_llm=financial_faq_llm,
                            portfolio_llm=portfolio_llm,
                            market_analysis_llm=market_analysis_llm)
    self.portfolio_manager = portfolio_manager
    self.market_manager = market_manager
