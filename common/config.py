import configparser
import logging
from pathlib import Path

DEFAULT_CONFIG_FILE = './config.ini'

logger = logging.getLogger(__name__)


class ConfigUtil():
    def __init__(self):
        logger.debug('start:ConfigUtil:init')
        self.config = configparser.SafeConfigParser()
        self.config.read(Path(DEFAULT_CONFIG_FILE))
        logger.debug('start:ConfigUtil:init')


_util = ConfigUtil()


def get(section, key):
    logger.debug(f'ConfigUtil:get:section->{section}, key->{key}')
    return _util.config.get(section, key)


if __name__ == '__main__':
    print(get('user_info', 'CorporationId'))
