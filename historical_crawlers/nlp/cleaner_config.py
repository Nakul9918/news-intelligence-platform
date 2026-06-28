"""
=====================================================
News Content Cleaner Configuration
Version : 2.0
=====================================================
"""

# --------------------------------------------------
# Rules applied to EVERY news source
# --------------------------------------------------

GLOBAL_REMOVE_PHRASES = [

    # Advertisement
    "Advertisement",
    "Advertisements",
    "Sponsored",
    "Sponsored Content",

    # Navigation
    "Read More",
    "Read Next",
    "Continue Reading",
    "More Stories",
    "Latest News",
    "Breaking News",
    "Trending",
    "View All",

    # Social
    "Follow Us",
    "WhatsApp",
    "Facebook",
    "Twitter",
    "Telegram",

    # Login
    "Login",
    "Sign In",
    "Register",
    "Subscribe",
    "Subscribe Now"

]

# --------------------------------------------------
# Newspaper Specific Rules
# --------------------------------------------------

SOURCE_REMOVE_PHRASES = {

    "Economic Times": [

        "Live Events",
        "Reliable and Trusted News Source",
        "Add Now!",
        "Quote of the day",
        "What does the quote mean?",
        "More inspiring quotes"

    ],

    "The Hindu": [

    ],

    "Indian Express": [

    ]

}

# --------------------------------------------------
# Regular Expressions
# --------------------------------------------------

REGEX_PATTERNS = [

    # URLs
    r"https?://\S+",
    r"www\.\S+",

    # Date Example:
    # Jun 18, 2026 05:20 PM IST
    r"[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}.*?IST"

]