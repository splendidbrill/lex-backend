from dataclasses import dataclass
from typing import List
import re

from crewai import Agent, Crew, Task, LLM

from .agents import _get_llm


@dataclass
class ResearchResult:
	insights: str


@dataclass
class PlanResult:
	plan: str
	score: int


# Very simple heuristic scorer that can be extended later
_DEF_TREND_KEYWORDS = [
	"AI", "LLM", "GenAI", "sustainability", "climate", "privacy", "security",
	"short-form", "video", "TikTok", "Reels", "SEO", "SEM", "influencer",
	"B2B", "B2C", "omnichannel", "CAC", "LTV", "retention", "churn", "AR",
]


def _score_plan_heuristic(plan_text: str, research_text: str) -> int:
	text = (plan_text + "\n" + research_text).lower()
	score = 50
	# Reward structure/metrics
	if re.search(r"kpi|metric|milestone|okrs?", text):
		score += 10
	# Reward channels mix
	if re.search(r"linkedin|facebook|tiktok|youtube|blog|seo|sem|email", text):
		score += 10
	# Reward pricing/positioning mentions
	if re.search(r"pricing|positioning|competitor|segment|persona", text):
		score += 10
	# Reward trend keywords
	for kw in _DEF_TREND_KEYWORDS:
		if kw.lower() in text:
			score += 1
	# Penalize if too short
	if len(plan_text.split()) < 150:
		score -= 10
	# Clamp 0..100
	return max(0, min(100, score))


def run_market_research(company: str, product: str, target_markets: List[str]) -> ResearchResult:
	llm: LLM = _get_llm()
	researcher = Agent(
		role="Market Research Analyst",
		goal=(
			f"Analyze the market for {company}'s {product} across {', '.join(target_markets)}."
		),
		backstory=(
			"You specialize in competitive analysis, audience segmentation, and trend identification."
		),
		llm=llm,
		verbose=False,
	)
	research_task = Task(
		description=(
			"Provide a succinct market research brief: audience segments, competitors, pricing, "
			"channels, and top 5 actionable insights."
		),
		expected_output="A concise research brief with 5 insights.",
		agent=researcher,
	)
	crew = Crew(agents=[researcher], tasks=[research_task], verbose=False)
	insights = str(crew.kickoff())
	return ResearchResult(insights=insights)


def create_business_plan_and_score(company: str, product: str, research: str) -> PlanResult:
	llm: LLM = _get_llm()
	planner = Agent(
		role="Go-To-Market Planner",
		goal=(
			f"Create a 3-month GTM plan for {company}'s {product} using provided research."
		),
		backstory=(
			"You are a strategic planner focusing on achievable, measurable marketing plans."
		),
		llm=llm,
		verbose=False,
	)
	plan_task = Task(
		description=(
			"Draft a 3-month marketing plan with weekly milestones, KPIs, and channels. "
			"Return the plan."
			f"\n\nResearch input:\n{research}"
		),
		expected_output=(
			"A plan with measurable milestones."
		),
		agent=planner,
	)
	crew = Crew(agents=[planner], tasks=[plan_task], verbose=False)
	raw = str(crew.kickoff())
	score = _score_plan_heuristic(raw, research)
	return PlanResult(plan=raw, score=score)


def generate_daily_content(company: str, product: str, plan: str, platforms: List[str]) -> str:
	llm: LLM = _get_llm()
	creator = Agent(
		role="Content Strategist",
		goal=(
			"Generate LinkedIn, Facebook, and Blog posts based on the plan and current trends."
		),
		backstory=(
			"You create compelling copy aligned with brand voice and timely trends."
		),
		llm=llm,
		verbose=False,
	)
	content_task = Task(
		description=(
			"Produce platform-specific posts for the next 1 day using the business plan. "
			"Include: \n- LinkedIn post\n- Facebook post\n- Blog post outline (H2s + bullet points)."
			f"\n\nPlan:\n{plan}\n\nPlatforms: {', '.join(platforms)}"
		),
		expected_output="Distinct sections for LinkedIn, Facebook, Blog.",
		agent=creator,
	)
	crew = Crew(agents=[creator], tasks=[content_task], verbose=False)
	return str(crew.kickoff())
