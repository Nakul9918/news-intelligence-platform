"""
=========================================================
Newspaper CSS Selectors

Contains CSS selectors used by every newspaper extractor.

Structure
---------
NEWSPAPER_SELECTORS

↓

Field Name

↓

List of CSS Selectors
=========================================================
"""
# =====================================================
# Economic Times
# =====================================================

ET_SELECTORS = {

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    "title": [

        "h1",

        "h1[data-arttitle]",

        ".artTitle",

        ".headline",

        ".article_headline",

        "meta[property='og:title']",

    ],

    # ----------------------------------------------
    # Description
    # ----------------------------------------------

    "description": [

        "meta[name='description']",

        "meta[property='og:description']",

    ],

    # ----------------------------------------------
    # Authors
    # ----------------------------------------------

    "authors": [

        ".authName",

        ".author",

        ".byline",

        ".storyBy",

        "[rel='author']",

    ],

    # ----------------------------------------------
    # Published Date
    # ----------------------------------------------

    "published_date": [

        "meta[property='article:published_time']",

        "meta[name='publishdate']",

        "time",

    ],

    # ----------------------------------------------
    # Article Content
    # ----------------------------------------------

    "content": [

        ".artText p",

        ".artText div",

        ".article_wrap p",

        ".article_wrap div",

        ".article_block p",

        ".article_block div",

        ".Normal",

        ".contentText p",

        ".contentText div",

        "article p",

        "article div",

        "[data-artid] p",

    ],

}
# =====================================================
# The Hindu
# =====================================================

THE_HINDU_SELECTORS = {

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    "title": [

        "h1",

        ".title",

        ".story-title",

        ".article-title",

        "meta[property='og:title']",

    ],

    # ----------------------------------------------
    # Description
    # ----------------------------------------------

    "description": [

        "meta[name='description']",

        "meta[property='og:description']",

    ],

    # ----------------------------------------------
    # Authors
    # ----------------------------------------------

    "authors": [

        ".author-name",

        ".author",

        ".byline",

        ".story-author",

        "[rel='author']",

    ],

    # ----------------------------------------------
    # Published Date
    # ----------------------------------------------

    "published_date": [

        "meta[property='article:published_time']",

        "time",

        ".publish-time",

        ".updated-time",

    ],

    # ----------------------------------------------
    # Article Content
    # ----------------------------------------------

    "content": [

        ".articlebodycontent p",

        ".articlebodycontent div",

        ".article-content p",

        ".article-content div",

        ".story-content p",

        ".story-content div",

        "article p",

        "article div",

    ],

}
# =====================================================
# Indian Express
# =====================================================

INDIAN_EXPRESS_SELECTORS = {

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    "title": [

        "h1",

        ".native_story_title",

        ".story-title",

        ".article-title",

        "meta[property='og:title']",

    ],

    # ----------------------------------------------
    # Description
    # ----------------------------------------------

    "description": [

        "meta[name='description']",

        "meta[property='og:description']",

    ],

    # ----------------------------------------------
    # Authors
    # ----------------------------------------------

    "authors": [

        ".author",

        ".author-name",

        ".editor",

        ".byline",

        ".story-author",

        "[rel='author']",

    ],

    # ----------------------------------------------
    # Published Date
    # ----------------------------------------------

    "published_date": [

        "meta[property='article:published_time']",

        "time",

        ".date",

        ".publish-date",

    ],

    # ----------------------------------------------
    # Article Content
    # ----------------------------------------------

    "content": [

        ".story_details p",

        ".story_details div",

        ".full-details p",

        ".full-details div",

        ".article-content p",

        ".article-content div",

        ".story-content p",

        ".story-content div",

        "article p",

        "article div",

    ],

}
# =====================================================
# Hindustan Times
# =====================================================

HINDUSTAN_TIMES_SELECTORS = {

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    "title": [

        "h1",

        ".hdg1",

        ".story-title",

        ".article-title",

        "meta[property='og:title']",

    ],

    # ----------------------------------------------
    # Description
    # ----------------------------------------------

    "description": [

        "meta[name='description']",

        "meta[property='og:description']",

    ],

    # ----------------------------------------------
    # Authors
    # ----------------------------------------------

    "authors": [

        ".author",

        ".author-name",

        ".storyBy",

        ".byline",

        ".story-author",

        "[rel='author']",

    ],

    # ----------------------------------------------
    # Published Date
    # ----------------------------------------------

    "published_date": [

        "meta[property='article:published_time']",

        "time",

        ".dateTime",

        ".publish-time",

    ],

    # ----------------------------------------------
    # Article Content
    # ----------------------------------------------

    "content": [

        ".storyDetails p",

        ".storyDetails div",

        ".detail p",

        ".detail div",

        ".storyParagraph p",

        ".storyParagraph div",

        ".article-content p",

        ".article-content div",

        ".story-content p",

        ".story-content div",

        "article p",

        "article div",

    ],

}
# =====================================================
# Newspaper Selector Registry
# =====================================================

SELECTOR_REGISTRY = {

    "Economic Times": ET_SELECTORS,

    "The Hindu": THE_HINDU_SELECTORS,

    "Indian Express": INDIAN_EXPRESS_SELECTORS,

    "Hindustan Times": HINDUSTAN_TIMES_SELECTORS,

}