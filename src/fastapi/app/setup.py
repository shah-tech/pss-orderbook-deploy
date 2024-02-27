# setup DB with middleware (called before each request)
from SQLsetup import create_tables, create_admin,create_roles,upsert_stock_data, get_roles

import logging
logger = logging.getLogger('general')


try:
    create_tables()
    create_roles()
    roles = get_roles() # set global roles
    create_admins(roles['admin'])
    upsert_stock_data() # download data
except:
    logger.info("DB already setup")


