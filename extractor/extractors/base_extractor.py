"""
=========================================================
Base Extractor

Parent class for all newspaper extractors.

Every newspaper extractor must inherit this class.

Responsibilities
----------------
Download Article
↓

Extract Fields

↓

Return Standard Dictionary
=========================================================
"""

# =====================================================
# Standard Library
# =====================================================

from abc import (
    ABC,
    abstractmethod,
)

# =====================================================
# Common Extractor
# =====================================================

from extractor.common_extractor import (

    download_article,

    build_result,

)

# =====================================================
# Base Extractor
# =====================================================

class BaseExtractor(ABC):

    """
    Parent class for every newspaper extractor.
    """

    def __init__(

        self,

        source_name

    ):

        self.source_name = source_name

    # =================================================
    # Download
    # =================================================

    def download(

        self,

        article_url

    ):

        return download_article(

            article_url

        )

    # =================================================
    # Extract
    # =================================================

    @abstractmethod

    def extract(

        self,

        article_url

    ):

        """
        Extract article.

        Must return build_result().
        """

        pass

    # =================================================
    # Empty Result
    # =================================================

    def empty_result(

        self

    ):

        return build_result()

# =====================================================
# Validate URL
# =====================================================

    def validate_url(
        self,
        article_url
    ):
        """
        Validate article URL.
        """

        if not article_url:

            raise ValueError(
                "Article URL is empty."
            )

        if not isinstance(
            article_url,
            str
        ):

            raise TypeError(
                "Article URL must be string."
            )

        return article_url.strip()

    # =================================================
    # Download Soup
    # =================================================

    def get_soup(
        self,
        article_url
    ):
        """
        Validate URL and download HTML.
        """

        article_url = self.validate_url(
            article_url
        )

        soup = self.download(
            article_url
        )

        if soup is None:

            raise RuntimeError(
                "Unable to download article."
            )

        return soup

    # =================================================
    # Success Result
    # =================================================

    def success(
        self,
        **kwargs
    ):
        """
        Return successful extraction.
        """

        return build_result(
            **kwargs
        )

    # =================================================
    # Failed Result
    # =================================================

    def failed(
        self,
        message=""
    ):
        """
        Return empty extraction result.
        """

        result = build_result()

        result["error"] = message

        return result