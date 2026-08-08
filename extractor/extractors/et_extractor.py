

"""
=========================================================
Economic Times Extractor

Extracts article information from
Economic Times news pages.

Responsibilities
----------------
Download HTML
↓

Extract Fields

↓

Return Standard Dictionary

This class DOES NOT update MongoDB.
=========================================================
"""

# =====================================================
# Standard Library
# =====================================================

import logging

# =====================================================
# Base Extractor
# =====================================================

from extractor.extractors.base_extractor import (
    BaseExtractor,
)

# =====================================================
# Common Extractor
# =====================================================

from extractor.common_extractor import (

    extract_title,

    extract_description,

    extract_authors,

    extract_paragraphs,

    extract_published_date,

)

# =====================================================
# Selector Registry
# =====================================================

from extractor.selectors import (
    SELECTOR_REGISTRY,
)

# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(
    "ETExtractor"
)

# =====================================================
# ET Extractor
# =====================================================

class ETExtractor(BaseExtractor):

    """
    Economic Times Extractor
    """

    def __init__(self):

        super().__init__(

            source_name="Economic Times"

        )

        self.selectors = SELECTOR_REGISTRY[
            self.source_name
        ]
    # =================================================
    # Extract Title
    # =================================================

    def _extract_title(
        self,
        soup
    ):
        """
        Extract article title.
        """

        return extract_title(

            soup,

            self.selectors["title"]

        )

    # =================================================
    # Extract Description
    # =================================================

    def _extract_description(
        self,
        soup
    ):
        """
        Extract article description.
        """

        return extract_description(

            soup,

            self.selectors["description"]

        )

    # =================================================
    # Extract Authors
    # =================================================

    def _extract_authors(
        self,
        soup
    ):
        """
        Extract article authors.
        """

        return extract_authors(

            soup,

            self.selectors["authors"]

        )

    # =================================================
    # Extract Published Date
    # =================================================

    def _extract_published_date(
        self,
        soup
    ):
        """
        Extract published date.
        """

        return extract_published_date(

            soup,

            self.selectors["published_date"]

        )

    # =================================================
    # Extract Content
    # =================================================

    def _extract_content(
        self,
        soup
    ):
        """
        Extract article body.
        """

        return extract_paragraphs(

            soup,

            self.selectors["content"]

        )

    # =================================================
    # Build Result
    # =================================================

    def _build_result(
        self,
        soup
    ):
        """
        Build standard extraction dictionary.
        """

        return {

            "title": self._extract_title(
                soup
            ),

            "description": self._extract_description(
                soup
            ),

            "authors": self._extract_authors(
                soup
            ),

            "published_date": self._extract_published_date(
                soup
            ),

            "content": self._extract_content(
                soup
            ),

            "extraction_method": "BeautifulSoup",

        }

    # =================================================
    # Extract Article
    # =================================================

    def extract(
        self,
        article_url
    ):
        """
        Extract Economic Times article.
        """

        soup = self.get_soup(
            article_url
        )

        if soup is None:

            return self.failed(
                "Unable to download article."
            )

        return self.success(

            **self._build_result(
                soup
            )

        )


# =====================================================
# Local Testing
# =====================================================

if __name__ == "__main__":

    TEST_URL = (
        "https://economictimes.indiatimes.com/news/new-updates/what-did-virat-kohli-tell-shubman-gill-during-ipl-final-heated-argument-caught-on-cam/articleshow/131427897.cms"
    )

    logger.info("=" * 70)
    logger.info("Economic Times Extractor Test")
    logger.info("=" * 70)

    extractor = ETExtractor()

    try:

        result = extractor.extract(
            TEST_URL
        )

        print("\n")
        print("=" * 70)
        print("Extraction Result")
        print("=" * 70)

        print(f"Title            : {result['title']}")
        print()

        print(f"Description      : {result['description']}")
        print()

        print(f"Authors          : {result['authors']}")
        print()

        print(f"Published Date   : {result['published_date']}")
        print()

        print(f"Content Length   : {len(result['content'])}")
        print()

        print(f"Extraction Method: {result['extraction_method']}")
        print()

        print("=" * 70)

    except Exception as e:

        logger.exception(e)