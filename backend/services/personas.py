PERSONAS = [
    {
        "name": "first_time_customer",
        "label": "First-Time Customer",
        "emoji": "🆕",
        "description": "A new visitor seeing the site for the first time. Cautious, reads everything, looks for trust signals.",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1,
        "slow_mo": 100,
        "actions": [
            {"type": "navigate", "url": "", "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 600, "wait": 1500},
            {"type": "scroll", "direction": "up", "amount": 300, "wait": 1000},
            {"type": "click_first", "selectors": ["a[href*='pricing']", "a[href*='price']", "a:has-text('Pricing')", "nav a:nth-child(2)"], "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 800, "wait": 1500},
            {"type": "click_first", "selectors": ["a[href*='signup']", "a[href*='register']", "a[href*='get-started']", "a:has-text('Get Started')", "a:has-text('Sign Up')", "a[href*='cta']"], "wait": 3000},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 1000},
            {"type": "go_back", "wait": 1500},
            {"type": "click_first", "selectors": ["a[href*='feature']", "a:has-text('Features')", "nav a:nth-child(1)"], "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": 500, "wait": 1000},
        ]
    },
    {
        "name": "confused_grandparent",
        "label": "Confused Grandparent",
        "emoji": "👴",
        "description": "Elderly user unfamiliar with modern web patterns. Slow, hesitant, clicks the wrong things.",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1.25,
        "slow_mo": 400,
        "actions": [
            {"type": "navigate", "url": "", "wait": 3000},
            {"type": "scroll", "direction": "down", "amount": 200, "wait": 2000},
            {"type": "click_random_nonlink", "wait": 1500},
            {"type": "scroll", "direction": "down", "amount": 300, "wait": 2000},
            {"type": "click_first", "selectors": ["a:has-text('Help')", "a:has-text('FAQ')", "a:has-text('Support')", "a[href*='help']", "a[href*='faq']"], "wait": 2500},
            {"type": "go_back", "wait": 2000},
            {"type": "click_first", "selectors": ["a:has-text('Home')", "a[href='/']", "a[href='']", "nav a:first-child"], "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 2000},
            {"type": "click_first", "selectors": ["a:has-text('Contact')", "a:has-text('About')", "a[href*='contact']"], "wait": 2500},
        ]
    },
    {
        "name": "power_user",
        "label": "Power User",
        "emoji": "⚡",
        "description": "Experienced user who wants efficiency. Uses keyboard, moves fast, looks for advanced features.",
        "viewport": {"width": 1920, "height": 1080},
        "device_scale_factor": 1,
        "slow_mo": 30,
        "actions": [
            {"type": "navigate", "url": "", "wait": 500},
            {"type": "click_first", "selectors": ["a[href*='feature']", "a:has-text('Features')", "a[href*='docs']", "a:has-text('Docs')"], "wait": 800},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 500},
            {"type": "click_first", "selectors": ["a[href*='api']", "a:has-text('API')", "a[href*='integrat']", "a:has-text('Integrations')"], "wait": 1000},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 500},
            {"type": "navigate", "url": "", "wait": 300},
            {"type": "click_first", "selectors": ["a[href*='pricing']", "a:has-text('Pricing')"], "wait": 800},
            {"type": "scroll", "direction": "down", "amount": 600, "wait": 500},
            {"type": "click_first", "selectors": ["a[href*='signup']", "a[href*='register']", "a:has-text('Get Started')"], "wait": 1000},
            {"type": "fill_first", "selectors": ["input[type='email']", "input[name='email']", "input[placeholder*='email']"], "value": "power.user@demo.com", "wait": 300},
        ]
    },
    {
        "name": "impatient_gamer",
        "label": "Impatient Gamer",
        "emoji": "🎮",
        "description": "Zero patience. Wants everything now. Aggressive clicking, rapid scrolling, easily frustrated.",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1,
        "slow_mo": 20,
        "actions": [
            {"type": "navigate", "url": "", "wait": 500},
            {"type": "scroll", "direction": "down", "amount": 900, "wait": 200},
            {"type": "scroll", "direction": "down", "amount": 900, "wait": 200},
            {"type": "scroll", "direction": "up", "amount": 1800, "wait": 100},
            {"type": "click_first", "selectors": ["a[href*='pricing']", "a:has-text('Pricing')", "nav a:nth-child(3)"], "wait": 300},
            {"type": "click_first", "selectors": ["a[href*='buy']", "a[href*='checkout']", "a[href*='purchase']", "a[href*='signup']", "a:has-text('Get Started')"], "wait": 500},
            {"type": "scroll", "direction": "down", "amount": 500, "wait": 200},
            {"type": "go_back", "wait": 300},
            {"type": "click_first", "selectors": ["a[href*='blog']", "a:has-text('Blog')", "nav a:nth-child(4)"], "wait": 500},
        ]
    },
    {
        "name": "mobile_user",
        "label": "Mobile User (Slow Internet)",
        "emoji": "📱",
        "description": "Browsing on a phone with 3G connection. Touch targets need to be large, pages need to be lightweight.",
        "viewport": {"width": 375, "height": 812},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "slow_mo": 200,
        "actions": [
            {"type": "navigate", "url": "", "wait": 3000},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 2000},
            {"type": "click_first", "selectors": ["a[href*='pricing']", "a:has-text('Pricing')", "nav a:nth-child(2)"], "wait": 2500},
            {"type": "scroll", "direction": "down", "amount": 600, "wait": 2000},
            {"type": "click_first", "selectors": ["a[href*='feature']", "a:has-text('Features')", "nav a:nth-child(1)"], "wait": 2500},
            {"type": "scroll", "direction": "down", "amount": 500, "wait": 1500},
            {"type": "click_first", "selectors": ["a[href*='signup']", "a[href*='get-started']", "a:has-text('Get Started')"], "wait": 3000},
        ]
    },
    {
        "name": "potential_buyer",
        "label": "Potential Buyer",
        "emoji": "💰",
        "description": "Ready to purchase but wants to compare plans, read reviews, and feel confident before committing.",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1,
        "slow_mo": 150,
        "actions": [
            {"type": "navigate", "url": "", "wait": 1500},
            {"type": "scroll", "direction": "down", "amount": 400, "wait": 1000},
            {"type": "click_first", "selectors": ["a[href*='pricing']", "a:has-text('Pricing')"], "wait": 2000},
            {"type": "scroll", "direction": "down", "amount": "max", "wait": 2000},
            {"type": "scroll", "direction": "up", "amount": 500, "wait": 1000},
            {"type": "click_first", "selectors": ["a[href*='testimonial']", "a:has-text('Testimonials')", "a:has-text('Reviews')", "section:has-text('Testimonials') a", "a[href*='review']"], "wait": 2000},
            {"type": "go_back", "wait": 1000},
            {"type": "click_first", "selectors": ["a[href*='faq']", "a:has-text('FAQ')", "a:has-text('Questions')"], "wait": 2000},
            {"type": "go_back", "wait": 1000},
            {"type": "click_first", "selectors": ["a[href*='signup']", "a[href*='get-started']", "a:has-text('Get Started')", "a:has-text('Buy')", "a[href*='checkout']"], "wait": 3000},
            {"type": "fill_first", "selectors": ["input[type='email']", "input[name='email']", "input[placeholder*='email']"], "value": "buyer@example.com", "wait": 500},
        ]
    }
]

def get_persona(name: str):
    for p in PERSONAS:
        if p["name"] == name:
            return p
    return PERSONAS[0]
