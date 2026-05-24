from logging import getLogger

logger = getLogger(__name__)


def filepath():
    from sgen.get_config import sgen_config
    from sgen.stdlib.path.middleware import PathMiddleware

    if PathMiddleware not in sgen_config.MIDDLEWARE:
        logger.warning("Filepath used but the middleware is not installed.")
        return "FILEPATH"

    return "[[path here]]"
