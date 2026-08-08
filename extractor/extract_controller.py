"""
Extractor Controller

Coordinates the complete extraction workflow.

Workflow

Extract Worker
        ↓
Extract Content
        ↓
Store in MongoDB
"""

import logging
import time

from extractor.extract_worker import main as run_extractor
# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "Extract_Controller"

)

# =====================================================
# Configuration
# =====================================================

CONTROLLER_VERSION = "1.0.0"

# =====================================================
# Main
# =====================================================

def main():

    logger.info("=" * 80)

    logger.info("Extractor Controller Started")

    logger.info("=" * 80)

    started = time.perf_counter()

    try:

        # ----------------------------------------
        # Run Extract Worker
        # ----------------------------------------

        run_extractor()

        duration = round(

            time.perf_counter()

            - started,

            3

        )

        logger.info("=" * 80)

        logger.info(

            "Extraction Completed Successfully"

        )

        logger.info("=" * 80)

        logger.info(

            f"Controller Version : {CONTROLLER_VERSION}"

        )

        logger.info(

            f"Execution Time     : {duration:.2f} sec"

        )

        logger.info("=" * 80)

    except KeyboardInterrupt:

        logger.warning("=" * 80)

        logger.warning(

            "Extraction Interrupted By User"

        )

        logger.warning("=" * 80)

    except Exception:

        logger.exception(

            "Extraction Failed"

        )

        raise

    finally:

        logger.info("=" * 80)

        logger.info(

            "Extractor Controller Exited"

        )

        logger.info("=" * 80)
# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    main()