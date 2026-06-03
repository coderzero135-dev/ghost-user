import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from playwright.async_api import async_playwright
from backend.services.personas import get_persona, PERSONAS
from backend.config import SCREENSHOTS_DIR, VIDEOS_DIR

_SELECTOR_LABELS = {
    "pricing": "pricing page",
    "signup": "signup page",
    "register": "registration page",
    "get-started": "Get Started link",
    "cta": "call-to-action button",
    "feature": "features page",
    "api": "API documentation",
    "integrat": "integrations page",
    "docs": "documentation",
    "blog": "blog",
    "testimonial": "testimonials",
    "review": "reviews",
    "faq": "FAQ page",
    "help": "help page",
    "support": "support page",
    "contact": "contact page",
    "about": "about page",
    "Home": "homepage link",
    "Pricing": "Pricing link",
    "Features": "Features link",
    "Get Started": "Get Started link",
    "Sign Up": "Sign Up link",
    "Buy": "Buy/purchase link",
    "Checkout": "checkout page",
    "FAQ": "FAQ link",
    "Contact": "Contact link",
    "About": "About link",
    "Blog": "Blog link",
    "Help": "Help link",
    "Support": "Support link",
    "Testimonials": "Testimonials link",
    "Reviews": "Reviews link",
    "Questions": "Questions/FAQ link",
    "email": "email input field",
}

_PERSONA_LABELS = {
    "first_time_customer": "First-Time Customer",
    "confused_grandparent": "Confused Grandparent",
    "power_user": "Power User",
    "impatient_gamer": "Impatient Gamer",
    "mobile_user": "Mobile User",
    "potential_buyer": "Potential Buyer",
}

def _human_issue(selectors, persona_name):
    hints = []
    for s in selectors:
        for key, label in _SELECTOR_LABELS.items():
            if key.lower() in s.lower():
                hints.append(label)
                break
    if hints:
        desc = f"Could not find the {' or '.join(set(hints))} on the page"
    else:
        desc = "A link or button the persona was looking for was missing"
    persona = _PERSONA_LABELS.get(persona_name, persona_name)
    return f"{persona} expected to find: {desc}"

def _human_action(action_type, error):
    labels = {
        "navigate": "page navigation (page may be slow or unreachable)",
        "click_first": "clicking a link or button (element may be missing or hidden)",
        "scroll": "scrolling the page",
        "go_back": "going back to the previous page",
        "fill_first": "filling in a form field (field may be missing or hidden)",
        "click_random_nonlink": "clicking a non-interactive element",
    }
    return labels.get(action_type, action_type)

async def run_persona_test(test_id: int, base_url: str, persona_name: str, update_callback):
    persona = get_persona(persona_name)
    session_id = str(uuid.uuid4())[:8]
    screenshot_dir = os.path.join(SCREENSHOTS_DIR, f"test_{test_id}", persona_name)
    video_dir = os.path.join(VIDEOS_DIR, f"test_{test_id}")
    os.makedirs(screenshot_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    screenshots = []
    navigation_path = []
    load_times = {}
    issues_found = []
    step = 0

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage", "--disable-gpu",
                    "--single-process", "--no-zygote",
                ]
            )

            context_options = {
                "viewport": persona["viewport"],
                "device_scale_factor": persona.get("device_scale_factor", 1),
                "user_agent": _get_user_agent(persona_name),
            }

            if persona.get("is_mobile"):
                context_options["is_mobile"] = True
                context_options["has_touch"] = True

            context = await browser.new_context(**context_options)
            page = await context.new_page()

            if persona.get("slow_mo"):
                page.set_default_timeout(30000)

            start_time = time.time()

            for action in persona["actions"]:
                step += 1
                action_type = action.get("type")
                wait_time = action.get("wait", 1000)

                try:
                    if action_type == "navigate":
                        url = action.get("url", "")
                        full_url = base_url.rstrip("/") + "/" + url.lstrip("/") if url else base_url
                        nav_start = time.time()
                        await page.goto(full_url, wait_until="domcontentloaded", timeout=15000)
                        nav_end = time.time()
                        load_times[f"step_{step}_load"] = round(nav_end - nav_start, 2)
                        navigation_path.append({"step": step, "action": "navigate", "url": full_url})
                        await asyncio.sleep(min(wait_time / 1000, 2))

                    elif action_type == "scroll":
                        direction = action.get("direction", "down")
                        amount = action.get("amount", 500)
                        if amount == "max":
                            amount = await page.evaluate("document.body.scrollHeight")
                        if direction == "down":
                            await page.evaluate(f"window.scrollBy(0, {amount})")
                        else:
                            await page.evaluate(f"window.scrollBy(0, -{amount})")
                        navigation_path.append({"step": step, "action": f"scroll_{direction}", "amount": amount})
                        await asyncio.sleep(min(wait_time / 1000, 1.5))

                    elif action_type == "click_first":
                        selectors = action.get("selectors", [])
                        clicked = False
                        for selector in selectors:
                            try:
                                el = await page.wait_for_selector(selector, timeout=3000)
                                if el:
                                    await el.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await el.click()
                                    clicked = True
                                    navigation_path.append({"step": step, "action": "click", "selector": selector})
                                    break
                            except:
                                continue
                        if not clicked:
                            navigation_path.append({"step": step, "action": "click_failed", "selectors": selectors})
                            issues_found.append({
                                "type": "missing_element",
                                "description": _human_issue(selectors, persona_name),
                                "severity": "medium"
                            })
                        await asyncio.sleep(min(wait_time / 1000, 2))

                    elif action_type == "go_back":
                        await page.go_back()
                        navigation_path.append({"step": step, "action": "go_back"})
                        await asyncio.sleep(min(wait_time / 1000, 1.5))

                    elif action_type == "fill_first":
                        selectors = action.get("selectors", [])
                        value = action.get("value", "")
                        filled = False
                        for selector in selectors:
                            try:
                                el = await page.wait_for_selector(selector, timeout=2000)
                                if el:
                                    await el.fill(value)
                                    filled = True
                                    navigation_path.append({"step": step, "action": "fill", "selector": selector})
                                    break
                            except:
                                continue
                        await asyncio.sleep(min(wait_time / 1000, 1))

                    elif action_type == "click_random_nonlink":
                        try:
                            elements = await page.query_selector_all("p, h1, h2, h3, h4, div:not(:has(a))")
                            import random
                            if elements:
                                el = random.choice(elements[:5])
                                await el.click()
                                navigation_path.append({"step": step, "action": "click_random_nonlink"})
                        except:
                            pass
                        await asyncio.sleep(min(wait_time / 1000, 1.5))

                    screenshot_path = os.path.join(screenshot_dir, f"step_{step}.png")
                    await page.screenshot(path=screenshot_path, full_page=False)
                    screenshots.append(f"uploads/screenshots/test_{test_id}/{persona_name}/step_{step}.png")

                except Exception as e:
                    issues_found.append({
                        "type": "navigation_error",
                        "description": f"Error during {action_type}: {_human_action(action_type, str(e))}",
                        "severity": "medium"
                    })
                    try:
                        screenshot_path = os.path.join(screenshot_dir, f"step_{step}_error.png")
                        await page.screenshot(path=screenshot_path, full_page=False)
                        screenshots.append(f"uploads/screenshots/test_{test_id}/{persona_name}/step_{step}_error.png")
                    except:
                        pass

            try:
                await page.close()
            except:
                pass
            try:
                await context.close()
            except:
                pass
            try:
                await browser.close()
            except:
                pass

            analysis = {
                "pages_visited": len(set(p.get("url", "") for p in navigation_path if "url" in p)),
                "actions_performed": len(navigation_path),
                "load_times": load_times,
                "issues_detected": issues_found,
                "screenshot_count": len(screenshots),
            }

            status = "completed" if screenshots else "failed"
            await update_callback(test_id, persona_name, {
                "status": status,
                "screenshot_paths": screenshots,
                "video_path": video_path,
                "navigation_path": navigation_path,
                "issues_found": issues_found,
                "load_times": load_times,
                "persona_notes": json.dumps(analysis),
            })

            return screenshots, navigation_path, issues_found, load_times, None

    except Exception as e:
        await update_callback(test_id, persona_name, {
            "status": "failed",
            "screenshot_paths": screenshots or [],
            "video_path": None,
            "navigation_path": navigation_path,
            "issues_found": issues_found + [{"type": "crawler_error", "description": str(e), "severity": "critical"}],
            "load_times": load_times,
            "persona_notes": f"Crawler failed: {str(e)}",
        })
        return screenshots, navigation_path, issues_found, load_times, None

def _get_user_agent(persona_name: str):
    agents = {
        "first_time_customer": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "confused_grandparent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/110.0.0.0 Safari/537.36",
        "power_user": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "impatient_gamer": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "mobile_user": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        "potential_buyer": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    }
    return agents.get(persona_name, agents["first_time_customer"])

async def run_all_personas(test_id: int, url: str, update_callback):
    results = {}
    for persona in PERSONAS:
        try:
            result = await run_persona_test(test_id, url, persona["name"], update_callback)
            results[persona["name"]] = result
        except Exception as e:
            results[persona["name"]] = ([], [], [{"type": "fatal", "description": str(e), "severity": "critical"}], {}, None)
    return results
