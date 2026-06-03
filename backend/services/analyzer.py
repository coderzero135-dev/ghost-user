import json
import os
import httpx
from backend.config import OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY, LLM_PROVIDER

_http_client = httpx.AsyncClient(timeout=30)

async def analyze_screenshots(test_id: int, url: str, persona_results: list[dict], all_issues: list[dict]):
    provider = LLM_PROVIDER or "offline"

    if provider == "gemini" and GEMINI_API_KEY:
        return await _analyze_gemini(url, persona_results, all_issues)
    elif provider == "groq" and GROQ_API_KEY:
        return await _analyze_groq(url, persona_results, all_issues)
    elif provider == "openai" and OPENAI_API_KEY:
        return await _analyze_openai(url, persona_results, all_issues)
    else:
        return _generate_offline_analysis(url, persona_results, all_issues)


def _build_prompt(url: str, persona_results: list[dict], all_issues: list[dict]):
    system = """You are a UX expert. Analyze the test results and return JSON:
{
  "overall_score": 0-100,
  "navigation_score": 0-100,
  "clarity_score": 0-100,
  "speed_score": 0-100,
  "mobile_score": 0-100,
  "content_score": 0-100,
  "summary": "2-3 sentence summary",
  "breakdown": {
    "strengths": [string list],
    "weaknesses": [string list],
    "recommendations": [string list]
  }
}
Be honest, critical, and specific."""
    user = f"""Website: {url}

Personas:
{json.dumps([{
    "persona": p.get("persona_name"),
    "status": p.get("status"),
    "steps": len(p.get("navigation_path", [])),
    "screenshots": len(p.get("screenshot_paths", [])),
    "issues": p.get("issues_found", []),
    "load_times": p.get("load_times", {})
} for p in persona_results], indent=2)}

Issues found:
{json.dumps(all_issues, indent=2) if all_issues else "None"}

Return the JSON analysis."""
    return system, user


async def _analyze_openai(url, persona_results, all_issues):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    system, user = _build_prompt(url, persona_results, all_issues)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0.3, max_tokens=1000,
        )
        return json.loads(resp.choices[0].message.content)
    except:
        return _generate_offline_analysis(url, persona_results, all_issues)


async def _analyze_gemini(url, persona_results, all_issues):
    system, user = _build_prompt(url, persona_results, all_issues)
    prompt = f"{system}\n\n{user}"
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}",
                    json={"contents": [{"parts": [{"text": prompt}]}],
                          "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000}},
                )
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip()
                if text.startswith("```"):
                    idx = text.find("\n")
                    if idx > 0:
                        text = text[idx+1:]
                    if text.endswith("```"):
                        text = text[:-3].strip()
                    elif text.endswith("``"):
                        text = text[:-2].strip()
                text = text.strip()
                return json.loads(text)
        except Exception as e:
            if attempt == 1:
                print(f"[Gemini] Error: {e}")
    return _generate_offline_analysis(url, persona_results, all_issues)


async def _analyze_groq(url, persona_results, all_issues):
    system, user = _build_prompt(url, persona_results, all_issues)
    try:
        resp = await _http_client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.3, "max_tokens": 1000,
                "response_format": {"type": "json_object"},
            }
        )
        data = resp.json()
        return json.loads(data["choices"][0]["message"]["content"])
    except:
        return _generate_offline_analysis(url, persona_results, all_issues)


def _generate_offline_analysis(url: str, persona_results: list[dict], all_issues: list[dict]):
    total_issues = len(all_issues)
    completed_personas = sum(1 for pr in persona_results if pr.get("status") == "completed")

    severity_weights = {"critical": 10, "high": 5, "medium": 3, "low": 1}
    weighted_score = sum(severity_weights.get(i.get("severity", "low"), 1) for i in all_issues)

    base_score = 85
    penalty = min(weighted_score * 3, 60)
    overall = max(15, min(98, base_score - penalty))

    breakdown = {"strengths": [], "weaknesses": [], "recommendations": []}

    if completed_personas >= 4:
        breakdown["strengths"].append("Tested successfully across multiple personas")
    if total_issues == 0:
        breakdown["strengths"].append("No critical issues detected automatically")

    for issue in all_issues[:5]:
        if issue.get("severity") in ("critical", "high"):
            breakdown["weaknesses"].append(issue.get("description", "Unknown issue"))

    breakdown["recommendations"] = [
        "Review screenshots for visual clarity and layout issues",
        "Check navigation flow for each persona path",
        "Ensure mobile responsiveness and touch-friendly targets",
        "Verify page load times are under 3 seconds",
        f"Run another test after fixing detected issues ({total_issues} found)"
    ]

    return {
        "overall_score": round(overall, 1),
        "navigation_score": round(max(10, overall - 5), 1),
        "clarity_score": round(max(10, overall + 3), 1),
        "speed_score": round(max(10, overall - 8), 1),
        "mobile_score": round(max(10, overall - 10), 1),
        "content_score": round(max(10, overall + 5), 1),
        "summary": f"Tested {url} with {completed_personas} personas. Found {total_issues} potential issues. Overall UX score: {round(overall)}/100.",
        "breakdown": breakdown,
    }
