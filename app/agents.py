from functools import lru_cache
import os

from crewai import Agent, Crew, Task, LLM

from .config import get_settings


@lru_cache(maxsize=1)
def _get_llm() -> LLM:
	settings = get_settings()
	# Ensure environment variables are set for LiteLLM/OpenAI under the hood
	os.environ.setdefault("AZURE_API_KEY", settings.azure_openai_api_key)
	os.environ.setdefault("AZURE_API_BASE", settings.azure_openai_endpoint)
	os.environ.setdefault("AZURE_API_VERSION", settings.azure_openai_api_version)
	# Some clients still read OPENAI_* even for Azure
	os.environ.setdefault("OPENAI_API_KEY", settings.azure_openai_api_key)
	os.environ.setdefault("OPENAI_BASE_URL", settings.azure_openai_endpoint)

	return LLM(
		model=f"azure/{settings.azure_openai_deployment}",
		api_key=settings.azure_openai_api_key,
		base_url=settings.azure_openai_endpoint,
		api_version=settings.azure_openai_api_version,
		temperature=0.2,
	)


def get_chat_response(user_message: str) -> str:
	llm = _get_llm()

	agent = Agent(
		role="Helpful Chat Assistant",
		goal="Provide concise, accurate, and friendly responses to user questions.",
		backstory=(
			"You are a helpful AI assistant. You answer clearly and briefly unless "
			"the user asks for more details."
		),
		llm=llm,
		verbose=False,
	)

	task = Task(
		description=(
			"Respond helpfully to the user's message. Keep it under 120 words unless "
			"more detail is requested.\n\nUser message: " + user_message
		),
		expected_output="A concise, helpful reply to the user.",
		agent=agent,
	)

	crew = Crew(agents=[agent], tasks=[task], verbose=False)
	result = crew.kickoff()
	return str(result)
