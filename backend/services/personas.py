PERSONAS = [
    {
        "name": "first_time_customer",
        "label": "First-Time Visitor",
        "description": "New to the site. Reads everything, looks for trust signals, takes their time.",
        "viewport": {"width": 1440, "height": 900},
        "slow_mo": 150,
        "actions": [
            {"type": "navigate", "url": "", "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 500, "wait": 1200},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 1000},
            {"type": "find_and_click", "intent": "pricing", "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 600, "wait": 1000},
            {"type": "find_and_click", "intent": "signup", "wait": 2500},
            {"type": "scroll", "direction": "down", "amount": 300, "wait": 800},
            {"type": "go_back", "wait": 1200},
            {"type": "find_and_click", "intent": "features", "wait": 2000},
        ]
    },
    {
        "name": "confused_grandparent",
        "label": "Elderly Beginner",
        "description": "Not tech-savvy. Clicks wrong things, needs clear labels, gives up easily.",
        "viewport": {"width": 1280, "height": 800},
        "slow_mo": 350,
        "actions": [
            {"type": "navigate", "url": "", "wait": 3000},
            {"type": "scroll", "direction": "down", "amount": 200, "wait": 2000},
            {"type": "click_random_nonlink", "wait": 1500},
            {"type": "scroll", "direction": "down", "amount": 300, "wait": 1800},
            {"type": "find_and_click", "intent": "help", "wait": 2500},
            {"type": "go_back", "wait": 2000},
            {"type": "find_and_click", "intent": "home", "wait": 1800},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 1500},
            {"type": "find_and_click", "intent": "contact", "wait": 2500},
        ]
    },
    {
        "name": "power_user",
        "label": "Power User",
        "description": "Keyboard-driven, scans fast, expects advanced options.",
        "viewport": {"width": 1920, "height": 1080},
        "slow_mo": 40,
        "actions": [
            {"type": "navigate", "url": "", "wait": 600},
            {"type": "find_and_click", "intent": "features", "wait": 800},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 500},
            {"type": "find_and_click", "intent": "docs", "wait": 1000},
            {"type": "navigate", "url": "", "wait": 400},
            {"type": "find_and_click", "intent": "pricing", "wait": 700},
            {"type": "scroll", "direction": "down", "amount": 600, "wait": 400},
            {"type": "find_and_click", "intent": "signup", "wait": 800},
            {"type": "fill_first", "selectors": ["input[type='email']", "input[name='email']", "input[placeholder*='email']"], "value": "power.user@demo.com", "wait": 300},
        ]
    },
    {
        "name": "impatient_gamer",
        "label": "Speed Runner",
        "description": "Zero patience. Rapid scrolls, rage clicks, leaves if slow.",
        "viewport": {"width": 1440, "height": 900},
        "slow_mo": 25,
        "actions": [
            {"type": "navigate", "url": "", "wait": 400},
            {"type": "scroll", "direction": "down", "amount": 800, "wait": 200},
            {"type": "scroll", "direction": "up", "amount": 800, "wait": 150},
            {"type": "find_and_click", "intent": "pricing", "wait": 400},
            {"type": "find_and_click", "intent": "cta", "wait": 500},
            {"type": "go_back", "wait": 300},
            {"type": "find_and_click", "intent": "blog", "wait": 400},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 200},
        ]
    },
    {
        "name": "mobile_user",
        "label": "Phone User",
        "description": "On a phone with slow internet. Thumb-scrolling, hates tiny buttons.",
        "viewport": {"width": 375, "height": 812},
        "is_mobile": True,
        "has_touch": True,
        "slow_mo": 180,
        "actions": [
            {"type": "navigate", "url": "", "wait": 2800},
            {"type": "scroll", "direction": "down", "amount": 300, "wait": 1800},
            {"type": "find_and_click", "intent": "pricing", "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 1500},
            {"type": "find_and_click", "intent": "features", "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 1200},
            {"type": "find_and_click", "intent": "signup", "wait": 2500},
        ]
    },
    {
        "name": "potential_buyer",
        "label": "Cautious Buyer",
        "description": "Ready to pay but needs convincing. Compares plans, reads reviews, checks FAQ.",
        "viewport": {"width": 1440, "height": 900},
        "slow_mo": 120,
        "actions": [
            {"type": "navigate", "url": "", "wait": 1500},
            {"type": "find_and_click", "intent": "pricing", "wait": 1800},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 1500},
            {"type": "go_back", "wait": 1000},
            {"type": "find_and_click", "intent": "testimonials", "wait": 2000},
            {"type": "go_back", "wait": 1000},
            {"type": "find_and_click", "intent": "faq", "wait": 1800},
            {"type": "go_back", "wait": 1000},
            {"type": "find_and_click", "intent": "signup", "wait": 2500},
            {"type": "fill_first", "selectors": ["input[type='email']", "input[name='email']", "input[placeholder*='email']"], "value": "buyer@example.com", "wait": 500},
        ]
    }
]

INTENT_PATTERNS = {
    "signup": ["sign up", "signup", "register", "get started", "start free", "create account", "join", "try free", "free trial", "sign up free", "get instant access", "sign up now", "create free account"],
    "pricing": ["pricing", "plans", "prices", "subscribe", "subscription", "upgrade", "see plans", "compare plans", "view pricing"],
    "features": ["features", "benefits", "capabilities", "what we do", "how it works", "product", "solutions", "tour", "demo", "explore"],
    "help": ["help", "support", "faq", "questions", "documentation", "docs", "guide", "knowledge base", "help center", "assistance", "learn more"],
    "contact": ["contact", "contact us", "get in touch", "reach out", "email us", "talk to us", "support", "chat", "message"],
    "about": ["about", "about us", "company", "team", "who we are", "our story", "mission"],
    "blog": ["blog", "news", "articles", "resources", "insights", "updates", "stories"],
    "testimonials": ["testimonials", "reviews", "customers", "case studies", "success stories", "clients", "what people say", "customer stories"],
    "faq": ["faq", "questions", "common questions", "answers", "help"],
    "home": ["home", "homepage", "back", "main"],
    "login": ["login", "sign in", "log in"],
    "docs": ["docs", "documentation", "api", "reference", "developers", "sdk"],
    "cta": ["get started", "sign up", "start", "try", "join", "begin", "launch"],
}


def get_persona(name: str):
    for p in PERSONAS:
        if p["name"] == name:
            return p
    return PERSONAS[0]
