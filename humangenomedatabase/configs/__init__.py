from humangenomedatabase.configs.config import Local, Production, Staging
import os


config_space = os.getenv('CONFIG_SPACE','LOCAL')
if config_space:
    if config_space == 'LOCAL':
        auto_config = Local
    elif config_space == 'STAGING':
        auto_config = Staging
    elif config_space == 'PRODUCTION':
        auto_config = Production
    else:
        auto_config = None
        raise EnvironmentError(f'CONFIG_SPACE is unexpected value: {config_space}')
else:
    raise EnvironmentError('CONFIG_SPACE environment variable is not set!')