"""
Supervisor Agent.

Orchestrates the subagents using a LangGraph StateGraph.
Pipeline: Research (fetch+classify) -> Trend Analysis -> QA -> Result.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.qa_agent import QAAgent
from app.agents.research_agent import ResearchAgent
from app.agents.trend_agent import TrendAgent
from app.core.logger import logger


class AgentState(TypedDict, total=False):
    """Shared state passed between agents in the graph."""
    topic: str
    queries: list[str]
    fetch_limit: int
    articles: list[dict]
    article_count: int
    trends: dict
    qa_passed: bool
    qa_notes: str
    qa_issues: list[str]


class SupervisorAgent:
    """
    Top-level orchestrator.

    Builds a LangGraph pipeline that routes work through
    ResearchAgent -> TrendAgent -> QAAgent sequentially.
    """

    def __init__(self) -> None:
        self.research = ResearchAgent()
        self.trend = TrendAgent()
        self.qa = QAAgent()
        self.graph = self._build_graph()
        logger.info("SupervisorAgent initialized")

    def _build_graph(self) -> Any:
        graph = StateGraph(AgentState)

        graph.add_node("research", self._research_node)
        graph.add_node("trend_analysis", self._trend_node)
        graph.add_node("qa", self._qa_node)

        graph.set_entry_point("research")
        graph.add_edge("research", "trend_analysis")
        graph.add_edge("trend_analysis", "qa")
        graph.add_edge("qa", END)

        return graph.compile()

    def _research_node(self, state: AgentState) -> AgentState:
        return self.research.run(state)

    def _trend_node(self, state: AgentState) -> AgentState:
        return self.trend.run(state)

    def _qa_node(self, state: AgentState) -> AgentState:
        return self.qa.run(state)

    def run(self, topic: str) -> AgentState:
        """Run the full agent pipeline for a given topic."""
        logger.info("SupervisorAgent starting pipeline for topic: %s", topic)
        initial_state: AgentState = {"topic": topic}
        result = self.graph.invoke(initial_state)
        logger.info("SupervisorAgent pipeline complete")
        return result
