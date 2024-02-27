"""
Session ID's is outdated, better to use Oath (pub, priv key sigs)
Uses Redis Cache for session management.... like PHP $SESSION var.... lol

"""

import redis
import uuid
from app.SQLClasses import *
from app.SQLsetup import site_roles, hash_password, mysql_conn_str
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import logging
logger = logging.getLogger('general')

cache = redis.Redis(host='orderbookcache', port=6379)

def update_all_roles(user_roles: dict = None) -> bool:
    session = Session(create_engine(mysql_conn_str()).connect())
    for uname,role in user_roles.items():
        if role == "default": # no change
            continue
        logger.info(f"updating role on user {uname}")
        user = session.query(User).filter(User.uname == uname)[0]
        new_role = session.query(Role).filter(Role.name == role)[0]
        logger.info(f"old role {user.role[0].name} to new role {new_role.name}")
        user.role[0] = new_role
        session.add(user)
    session.flush()
    session.commit()


def all_accounts() -> list[dict]:

    session = Session(create_engine(mysql_conn_str()).connect())

    result = session.query(User)

    users = []
    for user in result:
        user_dict = {}
        user_dict["uname"] = user.uname
        user_dict["dateJoined"] = user.dateJoined
        user_dict["role"] = user.role[0].name
        users.append(user_dict)
    return users

def new_user(uname: str=None,
             password: str=None,
             role: Role=None) -> bool:
    """

    """
    user = User(uname=uname, password=hash_password(password))

    user.role.append(role)

    session = Session(create_engine(mysql_conn_str()).connect())

    session.add(user)

    try:
        session.flush()
        session.commit()
    except IntegrityError as ie:
        logger.warning(f"USER ALREADY EXISTS: {uname}")
        return False

    logger.info(f"NEW USER: {uname}")

    return True

def authorize(uname: str=None, sessionid: str=None, roles : [] = None) -> bool:
    """
        @roles is the required roles to be authroized for the requested resource
            leave it as None for any role.
            Any combo of - "admin", "it", "user"
    """

    try:
        if uname_from_sessionid(sessionid) == uname:
            if roles is None: # any role can access
                return True
            else:
                user_roles = [x.decode('utf-8') for x in cache.lrange(f'{uname}-roles', 0, -1)]
                for role in roles:
                    if role in user_roles:
                        return True
                logger.warning("Role does not have access")
                return False
        else:
            return False
            logger.warning("Invalid sessionid")
    except AttributeError as a:
        logger.warning("Session ID does not exists")

def uname_from_sessionid(sessionid: str=None) -> str:
    """
    Throws AttributeError: 'NoneType' object has no attribute 'decode'
    if session id is not found


    """
    return cache.get(sessionid).decode('utf-8')

def sessionid_from_uname(uname: str=None) -> str:
    return cache.get(f"{uname}-sessionid").decode('utf-8')


def authenticate(uname: str=None, password: str=None) -> User|None:

    sqlEngine = create_engine(mysql_conn_str())

    dbConnection = sqlEngine.connect()

    # Use ORM instead of raw sql
    session = Session(dbConnection)

    result = session.query(User).filter(User.uname==uname)

    if result.count() != 1: return None

    user = result[0]

    db_password_hash = user.password

    roles = [role.name for role in user.role]

    if db_password_hash ==  hash_password(password):
        sessionid = str(uuid.uuid4())
        cache.set(f"{uname}-sessionid", sessionid)
        cache.lpush(f"{uname}-roles", *roles)
        cache.set(sessionid, uname)
        return user
    else:
        return None

def log_out(sessionid: str = None, uname: str = None) -> None:
    cache.delete(f"{uname}-sessionid")
    cache.delete(f"{uname}-role")
    cache.delete(sessionid)


