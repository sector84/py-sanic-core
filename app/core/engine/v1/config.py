import yaml
try:
    conf_file = yaml.load(open('app-config.yml'))
except:
    conf_file = {}

PG_CONF = {
    'host': conf_file.get('storage_postgres', {}).get('host', 'postgres'),
    'port': conf_file.get('storage_postgres', {}).get('port', 5432),
    'user': conf_file.get('storage_postgres', {}).get('user', 'postgres'),
    'pass': conf_file.get('storage_postgres', {}).get('pass', 'postgres'),
    'dbname': conf_file.get('storage_postgres', {}).get('dbname', '')
}

MC_CONF = {
    'host': conf_file.get('storage_memcache', {}).get('host', 'memcache'),
    'port': conf_file.get('storage_memcache', {}).get('port', '11211'),
}

# todo: добавить mongo для кэширования

# 1: logging.CRITICAL,
# 2: logging.ERROR,
# 3: logging.WARNING,
# 4: logging.INFO,
# 5: logging.DEBUG
DEBUG_LEVEL = conf_file.get('debug_level', 3)
