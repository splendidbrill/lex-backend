from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..marketing_agents import (
    run_market_research,
    create_business_plan_and_score,
    generate_daily_content,
)
from ..supabase_client import insert_user_artifact, get_latest_artifact

router = APIRouter(prefix="/marketing", tags=["marketing"])


class ResearchRequest(BaseModel):
    company: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    target_markets: List[str] = Field(default_factory=list)


class ResearchResponse(BaseModel):
    user_id: str
    insights: str
    question: str = Field(default="Do you want a business plan for that?")
    next_action: str = Field(default="POST /marketing/plan/confirm with {\"answer\":\"yes\"}")


@router.post("/research", response_model=ResearchResponse)
async def research(payload: ResearchRequest, x_user_id: Optional[str] = Header(default=None)) -> ResearchResponse:
    user_id = x_user_id or "dev_user"
    result = run_market_research(payload.company, payload.product, payload.target_markets)
    insert_user_artifact("marketing_research", user_id, {
        "company": payload.company,
        "product": payload.product,
        "target_markets": payload.target_markets,
        "insights": result.insights,
    })
    return ResearchResponse(user_id=user_id, insights=result.insights)


class PlanRequest(BaseModel):
    company: str
    product: str
    research_insights: Optional[str] = None


class PlanResponse(BaseModel):
    user_id: str
    plan: str
    score: int


@router.post("/plan", response_model=PlanResponse)
async def plan(payload: PlanRequest, x_user_id: Optional[str] = Header(default=None)) -> PlanResponse:
    user_id = x_user_id or "dev_user"
    research_text = (payload.research_insights or "").strip()
    if not research_text:
        last = get_latest_artifact("marketing_research", user_id)
        if not last or not last.get("insights"):
            raise HTTPException(status_code=400, detail="No research provided and none found for user.")
        research_text = str(last["insights"])  # type: ignore[index]
    result = create_business_plan_and_score(payload.company, payload.product, research_text)
    insert_user_artifact("marketing_plan", user_id, {
        "company": payload.company,
        "product": payload.product,
        "plan": result.plan,
        "score": result.score,
    })
    return PlanResponse(user_id=user_id, plan=result.plan, score=result.score)


class PlanConfirmRequest(BaseModel):
    answer: str = Field(..., description="yes/no")


class PlanConfirmResponse(BaseModel):
    user_id: str
    confirmed: bool
    message: Optional[str] = None
    plan: Optional[str] = None
    score: Optional[int] = None


@router.post("/plan/confirm", response_model=PlanConfirmResponse)
async def plan_confirm(payload: PlanConfirmRequest, x_user_id: Optional[str] = Header(default=None)) -> PlanConfirmResponse:
    user_id = x_user_id or "dev_user"
    if payload.answer.strip().lower() not in ("yes", "y"): 
        return PlanConfirmResponse(user_id=user_id, confirmed=False, message="Skipped creating business plan.")

    last = get_latest_artifact("marketing_research", user_id)
    if not last:
        raise HTTPException(status_code=400, detail="No saved research found for user.")

    company = str(last.get("company") or "")
    product = str(last.get("product") or "")
    research_text = str(last.get("insights") or "")
    if not company or not product or not research_text:
        raise HTTPException(status_code=400, detail="Saved research is incomplete. Please run research again.")

    result = create_business_plan_and_score(company, product, research_text)
    insert_user_artifact("marketing_plan", user_id, {
        "company": company,
        "product": product,
        "plan": result.plan,
        "score": result.score,
    })
    return PlanConfirmResponse(user_id=user_id, confirmed=True, plan=result.plan, score=result.score)


class ContentRequest(BaseModel):
    company: str
    product: str
    plan: str
    platforms: Optional[List[str]] = Field(default_factory=lambda: ["LinkedIn", "Facebook", "Blog"])


class ContentResponse(BaseModel):
    user_id: str
    content: str


@router.post("/content", response_model=ContentResponse)
async def content(payload: ContentRequest, x_user_id: Optional[str] = Header(default=None)) -> ContentResponse:
    user_id = x_user_id or "dev_user"
    text = generate_daily_content(payload.company, payload.product, payload.plan, payload.platforms or [])
    insert_user_artifact("marketing_content", user_id, {
        "company": payload.company,
        "product": payload.product,
        "plan": payload.plan,
        "platforms": payload.platforms,
        "content": text,
    })
    return ContentResponse(user_id=user_id, content=text)
