"""
=====================================================
News Content Cleaner Configuration
Version : 6.0
Production Ready
=====================================================
"""

# =====================================================
# Global Boilerplate
# =====================================================

GLOBAL_REMOVE_PHRASES = [

    # ---------------------------------------------
    # Advertisements
    # ---------------------------------------------
    "Advertisement",
    "Advertisements",
    "Sponsored",
    "Sponsored Content",

    # ---------------------------------------------
    # Navigation
    # ---------------------------------------------
    "Read More",
    "Read Next",
    "Continue Reading",
    "More Stories",
    "Latest News",
    "Breaking News",
    "Trending",
    "View All",

    # ---------------------------------------------
    # Related Content
    # ---------------------------------------------
    "Related Stories",
    "Related News",
    "Recommended Stories",
    "Recommended Articles",

    # ---------------------------------------------
    # Website Sections
    # ---------------------------------------------
    "Must Read",
    "Editor's Pick",
    "Explained",
    "Opinion",
    "Photo Gallery",
    "Videos",
    "Live Blog",
    "Live Updates",
    "Live Events",

    # ---------------------------------------------
    # Subscription
    # ---------------------------------------------
    "Subscribe",
    "Subscribe Now",
    "Newsletter",

    # ---------------------------------------------
    # Login
    # ---------------------------------------------
    "Login",
    "Log in",
    "Sign In",
    "Register",

    # ---------------------------------------------
    # Social
    # ---------------------------------------------
    "Follow Us",
    "Join our WhatsApp",
    "WhatsApp Channel",
    "Telegram Channel",
    "Download App",
]

# =====================================================
# Source Specific Boilerplate
# =====================================================

SOURCE_REMOVE_PHRASES = {

    "Economic Times": [

        "Reliable and Trusted News Source",
        "Add Now!",
        "Economic Times WhatsApp Channel",
        "You can now subscribe",

        "Synopsis",

        # ET Prime
        "ET Prime",
        "ETPrime",
        "Prime Member",
        "Prime Membership",
        "Prime credentials",
        "Premium Story",
        "Member benefits",
        "Enjoy member benefits",

        # Login
        "Already a member",
        "Current logged-in account",
        "Logged-in account",

        # Subscription
        "Unlock this story",
        "Unlock premium content",

        # Navigation
        "Continue Reading",
        "Read Full Story",
    ],

    "ET": [

        "Reliable and Trusted News Source",
        "Add Now!",
        "Economic Times WhatsApp Channel",
        "You can now subscribe",

        "Synopsis",

        "ET Prime",
        "ETPrime",
        "Prime Member",
        "Prime Membership",
        "Prime credentials",
        "Premium Story",
        "Member benefits",
        "Enjoy member benefits",

        "Already a member",
        "Current logged-in account",
        "Logged-in account",

        "Unlock this story",
        "Unlock premium content",

        "Continue Reading",
        "Read Full Story",
    ],

    "The Hindu": [],

    "Indian Express": [],

    "Hindustan Times": [],

    "BBC": [],

    "Reuters": [],
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
    r"You can now subscribe[^\n]*",
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
    # ET Prime
    # -----------------------------------------
    r"ETPrime.*",
    r"Prime credentials.*",
    r"Member benefits.*",
    r"Enjoy member benefits.*",
    r"Current logged-in account.*",
    r"Logged-in account.*",
    r"Already a member.*",
    r"Unlock.*",
    r"Read Full Story.*",
    r"Continue Reading.*",

    # -----------------------------------------
    # Copyright
    # -----------------------------------------
    r"©.*",
    r"All rights reserved.*",
]