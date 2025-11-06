"""
TripPilot Travel Agent - Using DeepSeek LLM with LangGraph
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import operator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import Config


# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    destination: str
    budget: float
    travel_plan: str
    next_action: str


class TravelAgent:
    """Travel planning agent using DeepSeek LLM"""

    def __init__(self):
        # Initialize DeepSeek LLM (using LangChain's OpenAI-compatible interface)
        self.llm = ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            openai_api_key=Config.DEEPSEEK_API_KEY,
            openai_api_base=Config.DEEPSEEK_BASE_URL,
            temperature=0.7,
            max_tokens=2000
        )

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("search_destinations", self._search_destinations)
        workflow.add_node("plan_itinerary", self._plan_itinerary)
        workflow.add_node("estimate_budget", self._estimate_budget)
        workflow.add_node("generate_response", self._generate_response)

        # Set entry point
        workflow.set_entry_point("analyze_query")

        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self._route_query,
            {
                "search": "search_destinations",
                "plan": "plan_itinerary",
                "budget": "estimate_budget",
                "direct": "generate_response"
            }
        )

        # Add edges
        workflow.add_edge("search_destinations", "generate_response")
        workflow.add_edge("plan_itinerary", "generate_response")
        workflow.add_edge("estimate_budget", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _analyze_query(self, state: AgentState) -> AgentState:
        """Analyze user query to determine intent"""
        user_query = state["user_query"]

        prompt = f"""Analyze the following user query and determine the primary intent:
User query: {user_query}

Please determine if the user wants to:
1. search - Search for destination information
2. plan - Plan a detailed itinerary
3. budget - Understand budget estimation
4. direct - Directly answer a general question

Return only one word: search, plan, budget, or direct"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        intent = response.content.strip().lower()

        state["next_action"] = intent if intent in ["search", "plan", "budget", "direct"] else "direct"
        state["messages"] = state.get("messages", []) + [
            HumanMessage(content=user_query),
            AIMessage(content=f"Understanding your need: {intent}")
        ]

        return state

    def _route_query(self, state: AgentState) -> str:
        """Route to different nodes based on analysis result"""
        return state.get("next_action", "direct")

    def _search_destinations(self, state: AgentState) -> AgentState:
        """Search for destination information"""
        user_query = state["user_query"]

        prompt = f"""The user wants to search for travel destination information: {user_query}

Please provide detailed information about the destination, including:
- Main attractions
- Best time to visit
- Cultural highlights
- Transportation options
- Visa requirements (if applicable)

Please respond in a friendly and professional tone."""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
        state["travel_plan"] = response.content

        return state

    def _plan_itinerary(self, state: AgentState) -> AgentState:
        """Plan detailed itinerary"""
        user_query = state["user_query"]
        destination = state.get("destination", "destination")

        prompt = f"""The user needs itinerary planning: {user_query}

Please create a detailed travel plan for {destination}, including:
1. Daily itinerary
2. Recommended attractions and activities
3. Accommodation suggestions
4. Dining recommendations
5. Transportation arrangements
6. Practical tips

Please ensure the itinerary is reasonable, feasible, and considers time and budget factors."""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
        state["travel_plan"] = response.content

        return state

    def _estimate_budget(self, state: AgentState) -> AgentState:
        """Estimate travel budget"""
        user_query = state["user_query"]
        destination = state.get("destination", "destination")

        prompt = f"""The user needs budget estimation: {user_query}

Please provide a detailed budget estimate for travel to {destination}, including:
1. Transportation costs (flights/trains/cars, etc.)
2. Accommodation costs (different tiers)
3. Dining costs
4. Attraction tickets
5. Other expenses (shopping, insurance, etc.)

Please provide reference budgets for low, medium, and high tiers."""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
        state["travel_plan"] = response.content

        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final response"""
        # If travel_plan already exists, return directly
        if state.get("travel_plan"):
            return state

        # Otherwise generate general response
        user_query = state["user_query"]

        prompt = f"""As TripPilot travel assistant, please answer the user's question: {user_query}

Please provide helpful and friendly answers. If the question is travel-related, provide practical advice and information."""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
        state["travel_plan"] = response.content

        return state

    def process_query(self, user_query: str, destination: str = "", budget: float = 0) -> dict:
        """
        Process user query

        Args:
            user_query: User's query content
            destination: Destination (optional)
            budget: Budget (optional)

        Returns:
            Dictionary containing response and status
        """
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "destination": destination,
            "budget": budget,
            "travel_plan": "",
            "next_action": ""
        }

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        return {
            "response": final_state.get("travel_plan", "Sorry, I cannot process your request."),
            "action_taken": final_state.get("next_action", "unknown"),
            "messages": final_state.get("messages", [])
        }


# Usage example
if __name__ == "__main__":
    # Test Agent
    agent = TravelAgent()

    # Test queries
    test_queries = [
        "I want to travel to Japan, any recommended places?",
        "Help me plan a 5-day Tokyo itinerary",
        "How much budget do I need for a trip to Paris?"
    ]

    for query in test_queries:
        print(f"\nUser query: {query}")
        print("-" * 50)
        result = agent.process_query(query)
        print(f"Response: {result['response']}")
        print(f"Action taken: {result['action_taken']}")
        print("=" * 50)