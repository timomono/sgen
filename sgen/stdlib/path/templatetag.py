from logging import getLogger

logger = getLogger(__name__)


def filepath():
    from sgen.get_config import sgen_config
    from sgen.stdlib.path.middleware import PathMiddleware

    for middleware in sgen_config.MIDDLEWARE:
        if isinstance(middleware, PathMiddleware):
            return "[[path here]]"

    logger.warning("Filepath used but the middleware is not installed.")
    return "FILEPATH"
