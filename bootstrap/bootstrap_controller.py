"""
Bootstrap Controller

Coordinates the complete bootstrap workflow.

Workflow
--------
Bootstrap Producer
        ↓
Collect Articles
        ↓
Store in MongoDB
"""

import logging
import time

from bootstrap.bootstrap_producer import run_bootstrap
from config import LOG_SEPARATOR

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "Bootstrap_Controller"

)

# =====================================================
# Configuration
# =====================================================

CONTROLLER_VERSION = "1.0.0"
# =====================================================
# Main
# =====================================================

def main():

    logger.info(LOG_SEPARATOR)

    logger.info("Bootstrap Controller Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    try:

        # ----------------------------------------
        # Run Bootstrap
        # ----------------------------------------

        run_bootstrap()

        duration = round(

            time.perf_counter()

            - started,

            3

        )

        logger.info(LOG_SEPARATOR)

        logger.info(

            "Bootstrap Completed Successfully"

        )

        logger.info(LOG_SEPARATOR)

        logger.info(

            f"Controller Version : {CONTROLLER_VERSION}"

        )

        logger.info(

            f"Execution Time     : {duration:.2f} sec"

        )

        logger.info(LOG_SEPARATOR)

    except KeyboardInterrupt:

        logger.warning("=" * 80)

        logger.warning(

            "Bootstrap Interrupted By User"

        )

        logger.warning("=" * 80)

    except Exception:

        logger.exception(

            "Bootstrap Failed"

        )

        raise

    finally:

        logger.info(LOG_SEPARATOR)

        logger.info(

            "Bootstrap Controller Exited"

        )

        logger.info(LOG_SEPARATOR)


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    main()