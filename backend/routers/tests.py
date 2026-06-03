import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import Test, PersonaResult, Issue, UXScore, User
from backend.services.auth import require_user, get_current_user
from backend.services.crawler import run_all_personas
from backend.services.analyzer import analyze_screenshots
from backend.schemas import CreateTestRequest, TestResponse, TestDetailResponse

router = APIRouter(prefix="/api/tests", tags=["tests"])

_test_tasks = {}

async def _update_persona_callback(test_id: int, persona_name: str, data: dict, db: AsyncSession):
    async with db.begin():
        result = await db.execute(
            select(PersonaResult).where(
                PersonaResult.test_id == test_id,
                PersonaResult.persona_name == persona_name
            )
        )
        pr = result.scalar_one_or_none()
        if pr:
            for key, val in data.items():
                setattr(pr, key, val)

async def _run_test_workflow(test_id: int, url: str):
    from backend.database import async_session
    async with async_session() as db:
        try:
            test = await db.get(Test, test_id)
            if not test:
                return
            test.status = "running"
            await db.commit()

            personas = ["first_time_customer", "confused_grandparent", "power_user",
                       "impatient_gamer", "mobile_user", "potential_buyer"]

            for p_name in personas:
                pr = PersonaResult(test_id=test_id, persona_name=p_name, status="pending")
                db.add(pr)
            await db.commit()

            async def callback(tid, pname, data):
                await _update_persona_callback(tid, pname, data, db)

            results = await run_all_personas(test_id, url, lambda tid, pname, data: callback(tid, pname, data))

            all_issues = []
            persona_data_list = []

            for p_name in personas:
                result = results.get(p_name, ([], [], [], {}, None))
                screenshots, nav_path, issues_found, load_times, video_path = result
                persona_data_list.append({
                    "persona_name": p_name,
                    "status": "completed" if screenshots else "failed",
                    "screenshot_paths": screenshots,
                    "video_path": video_path,
                    "navigation_path": nav_path,
                    "issues_found": issues_found,
                    "load_times": load_times,
                })

                for iss in issues_found:
                    issue = Issue(
                        test_id=test_id,
                        persona_name=p_name,
                        type=iss.get("type", "unknown"),
                        description=iss.get("description", ""),
                        severity=iss.get("severity", "medium"),
                        element=iss.get("element", ""),
                        url=url,
                        suggestion=iss.get("suggestion", ""),
                    )
                    db.add(issue)
                    all_issues.append(iss)

            await db.commit()

            analysis = await analyze_screenshots(test_id, url, persona_data_list, all_issues)
            if analysis:
                score = UXScore(
                    test_id=test_id,
                    overall_score=analysis.get("overall_score", 50),
                    navigation_score=analysis.get("navigation_score", 50),
                    clarity_score=analysis.get("clarity_score", 50),
                    speed_score=analysis.get("speed_score", 50),
                    mobile_score=analysis.get("mobile_score", 50),
                    content_score=analysis.get("content_score", 50),
                    summary=analysis.get("summary", ""),
                    breakdown=analysis.get("breakdown", {}),
                )
                db.add(score)

            test.status = "completed"
            test.completed_at = datetime.utcnow()
            await db.commit()

        except Exception as e:
            try:
                test = await db.get(Test, test_id)
                if test:
                    test.status = "failed"
                    await db.commit()
            except:
                pass
        finally:
            _test_tasks.pop(test_id, None)


@router.post("", response_model=TestResponse)
async def create_test(
    req: CreateTestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user:
        user = User(email=f"anon_{datetime.utcnow().timestamp()}@ghostuser.app", credits=1)
        db.add(user)
        await db.flush()

    if user.credits <= 0:
        raise HTTPException(status_code=402, detail="No credits remaining. Upgrade your plan.")

    test = Test(user_id=user.id, url=req.url, status="queued")
    db.add(test)
    await db.flush()
    await db.commit()

    user.credits -= 1
    await db.commit()

    async def _timed_workflow():
        try:
            await asyncio.wait_for(_run_test_workflow(test.id, req.url), timeout=300)
        except asyncio.TimeoutError:
            async with async_session() as db:
                t = await db.get(Test, test.id)
                if t:
                    t.status = "failed"
                    await db.commit()
    task = asyncio.create_task(_timed_workflow())
    _test_tasks[test.id] = task

    return TestResponse(
        id=test.id,
        url=test.url,
        status="queued",
        created_at=test.created_at,
        completed_at=test.completed_at,
    )


@router.get("", response_model=list[TestResponse])
async def list_tests(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Test)
    if user:
        query = query.where(Test.user_id == user.id)
    query = query.order_by(Test.created_at.desc()).limit(20)
    result = await db.execute(query)
    tests = result.scalars().all()
    return [TestResponse(
        id=t.id, url=t.url, status=t.status,
        created_at=t.created_at, completed_at=t.completed_at
    ) for t in tests]


@router.get("/{test_id}", response_model=TestDetailResponse)
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    stmt = select(Test).where(Test.id == test_id).options(
        selectinload(Test.persona_results),
        selectinload(Test.issues),
        selectinload(Test.ux_score),
    )
    result = await db.execute(stmt)
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    persona_results = []
    for pr in test.persona_results:
        persona_results.append({
            "id": pr.id,
            "persona_name": pr.persona_name,
            "status": pr.status,
            "screenshot_paths": pr.screenshot_paths or [],
            "video_path": pr.video_path,
            "navigation_path": pr.navigation_path or [],
            "issues_found": pr.issues_found or [],
            "load_times": pr.load_times or {},
            "persona_notes": pr.persona_notes,
        })

    issues = [{
        "id": i.id,
        "persona_name": i.persona_name,
        "type": i.type,
        "description": i.description,
        "severity": i.severity,
        "element": i.element,
        "url": i.url,
        "suggestion": i.suggestion,
    } for i in test.issues]

    ux_score = None
    if test.ux_score:
        ux_score = {
            "overall_score": test.ux_score.overall_score,
            "navigation_score": test.ux_score.navigation_score,
            "clarity_score": test.ux_score.clarity_score,
            "speed_score": test.ux_score.speed_score,
            "mobile_score": test.ux_score.mobile_score,
            "content_score": test.ux_score.content_score,
            "summary": test.ux_score.summary,
            "breakdown": test.ux_score.breakdown or {},
        }

    return TestDetailResponse(
        id=test.id,
        url=test.url,
        status=test.status,
        created_at=test.created_at,
        completed_at=test.completed_at,
        persona_results=persona_results,
        issues=issues,
        ux_score=ux_score,
    )
