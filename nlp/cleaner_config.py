"""
=====================================================
News Content Cleaner Configuration
Version : 4.0
=====================================================
"""

# =====================================================
# Global Boilerplate
# =====================================================

GLOBAL_REMOVE_PHRASES = [

    # Advertisements
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

    # Related Content
    "Related Stories",
    "Related News",
    "Recommended Stories",
    "Recommended Articles",

    # Website Sections
    "Must Read",
    "Editor's Pick",
    "Explained",
    "Opinion",
    "Photo Gallery",
    "Videos",
    "Live Blog",
    "Live Updates",
    "Live Events",

    # Subscription
    "Subscribe",
    "Subscribe Now",
    "Newsletter",

    # Login
    "Login",
    "Sign In",
    "Register",

    # Social
    "Follow Us",
    "Join our WhatsApp",
    "WhatsApp Channel",
    "Telegram Channel",
    "Download App"

]

# =====================================================
# Source Specific Boilerplate
# =====================================================

SOURCE_REMOVE_PHRASES = {

    "Economic Times": [

        "Reliable and Trusted News Source",

        "Add Now!",

        "Economic Times WhatsApp Channel",

        "You can now subscribe"

    ],

    "ET": [

        "Reliable and Trusted News Source",

        "Add Now!",

        "Economic Times WhatsApp Channel",

        "You can now subscribe"

    ],

    "The Hindu": [

    ],

    "Indian Express": [

    ],

    "Hindustan Times": [

    ]

}

# =====================================================
# Regular Expressions
# =====================================================

REGEX_PATTERNS = [

    # -----------------------------------------
    # URLs
    # -----------------------------------------

    r"https?://\S+",

    r"www\.\S+",

    # -----------------------------------------
    # Social Promotion
    # -----------------------------------------

    r"You can now subscribe.*",

    r"Join our WhatsApp.*",

    r"Follow us on.*",

    r"Follow our.*",

    r"Subscribe to our.*",

    r"Download our app.*",

    r"Click here.*",

    r"Share this article.*",

    # -----------------------------------------
    # Newsletter
    # -----------------------------------------

    r"Sign up for.*newsletter.*",

    # -----------------------------------------
    # Copyright
    # -----------------------------------------

    r"©.*",

    r"All rights reserved.*"

]