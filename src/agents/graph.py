"""defines the FinLit AI Graph"""
from langchain_chroma import Chroma
from langchain.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from agents.context_schema import ContextSchema
from agents.finance_faq import finance_faq_node, finance_faq_should_continue
from agents.market_analyzer import market_analysis_agent_node, market_analysis_agent_should_continue
from agents.portfolio_analyzer import portfolio_agent_node, portfolio_agent_should_continue
from agents.router import router_node, route_decision
from agents.state import (
  FINANCE_FAQ,
  FINANCE_FAQ_TOOLS,
  GRAPH_END,
  MARKET_ANALYSIS,
  MARKET_ANALYSIS_TOOLS,
  MESSAGES_FIELD,
  PORTFOLIO_AGENT_TOOLS,
  PORTFOLIO_ANALYSIS,
  FinLitState
)
from tools.market_manager import MarketManager
from tools.portfolio_manager import PortfolioManager

FINANCE_FAQ_NODE = "finance_faq_node"
FINANCE_FAQ_TOOL_NODE = "finance_faq_tool_node"
PORTFOLIO_AGENT_NODE = "portfolio_agent_node"
PORTFOLIO_AGENT_TOOL_NODE = "portfolio_agent_tool_node"
MARKET_ANALISYS_AGENT_NODE = "market_analysis_agent_node"
MARKET_ANALISYS_AGENT_TOOL_NODE = "market_analysis_agent_tool_node"
ROUTER_NODE = "router_node"


def build_graph(finance_article_collection: Chroma, llm: BaseChatModel, portfolio_manager: PortfolioManager,
                market_manager: MarketManager):
  """defines and builds the FinLit AI LangGraph"""
  context = ContextSchema(article_collection=finance_article_collection, llm=llm,
                          portfolio_manager=portfolio_manager, market_manager=market_manager)
  builder = StateGraph(FinLitState)

  # create tool nodes
  finance_faq_tool_node = ToolNode(tools=context.llm_tools.financial_faq_tools, messages_key=MESSAGES_FIELD)
  portfolio_agent_tool_node = ToolNode(tools=context.llm_tools.portfolio_tools, messages_key=MESSAGES_FIELD)
  market_analysis_agent_tool_node = ToolNode(tools=context.llm_tools.market_analysis_tools, messages_key=MESSAGES_FIELD)

  # add nodes
  builder.add_node(ROUTER_NODE, router_node)
  builder.add_node(FINANCE_FAQ_NODE, finance_faq_node)
  builder.add_node(FINANCE_FAQ_TOOL_NODE, finance_faq_tool_node)
  builder.add_node(PORTFOLIO_AGENT_NODE, portfolio_agent_node)
  builder.add_node(PORTFOLIO_AGENT_TOOL_NODE, portfolio_agent_tool_node)
  builder.add_node(MARKET_ANALISYS_AGENT_NODE, market_analysis_agent_node)
  builder.add_node(MARKET_ANALISYS_AGENT_TOOL_NODE, market_analysis_agent_tool_node)

  # add edges
  # router node edges
  builder.add_edge(START, ROUTER_NODE)
  builder.add_conditional_edges(ROUTER_NODE, route_decision, {
    FINANCE_FAQ: FINANCE_FAQ_NODE,
    PORTFOLIO_ANALYSIS: PORTFOLIO_AGENT_NODE,
    MARKET_ANALYSIS: MARKET_ANALISYS_AGENT_NODE
  })

  # financial faq edges
  builder.add_conditional_edges(FINANCE_FAQ_NODE, finance_faq_should_continue, {
    FINANCE_FAQ_TOOLS: FINANCE_FAQ_TOOL_NODE,
    GRAPH_END: END
  })

  # financial faq tool edges
  builder.add_edge(FINANCE_FAQ_TOOL_NODE, FINANCE_FAQ_NODE)

  # portfolio edges
  builder.add_conditional_edges(PORTFOLIO_AGENT_NODE, portfolio_agent_should_continue, {
    PORTFOLIO_AGENT_TOOLS: PORTFOLIO_AGENT_TOOL_NODE,
    GRAPH_END: END
  })

  # portfolio node tool edges
  builder.add_edge(PORTFOLIO_AGENT_TOOL_NODE, PORTFOLIO_AGENT_NODE)

  # market analyzer edges
  builder.add_conditional_edges(MARKET_ANALISYS_AGENT_NODE, market_analysis_agent_should_continue, {
    MARKET_ANALYSIS_TOOLS: MARKET_ANALISYS_AGENT_TOOL_NODE,
    GRAPH_END: END
  })

  # portfolio node tool edges
  builder.add_edge(MARKET_ANALISYS_AGENT_TOOL_NODE, MARKET_ANALISYS_AGENT_NODE)

  memory = InMemorySaver()
  return builder.compile(checkpointer=memory), context
