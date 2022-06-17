import logging
from fastapi import (
    Body,
    HTTPException, 
    Path, 
    Depends,
    status
)
from fastapi.security import (
    OAuth2PasswordBearer, 
    OAuth2PasswordRequestForm
)

import os
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import true as sa_true
from sqlalchemy.exc import IntegrityError

from app.models.user import User

from typing import Final
from typing import List
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation

from passlib.context import CryptContext
from .hash_pass import Hash_Password
from .token import Token
from .oauth import GetCurrentUsers

from app.schemas import UserData

from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.level = logger.setLevel(logging.INFO)
DATABASE_CONNECTION_ERROR: Final = "Error while connecting to PostgreSQL"
CLOSED_DATABASE_MESSAGE: Final = "PostgreSQL connection is closed"
CONNECTING_DB_MESSAGE: Final = "Connecting PostgreSQL database======"
DELETED_USER: Final = False
ACTIVE_USER: Final = True

@dataclass(frozen=True)
class UserDomain:
    id: int
    name: str
    email: str
    password: str
    is_active: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

@dataclass(frozen=True)
class CleanUserDomain:
    id: int
    name: str
    email: str
    is_active: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

# pwd_cxt = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

class DataBase:
    def __init__(self) -> None:
        self.database_user = os.getenv("DATABASE_USER")
        self.database_password = os.getenv("DATABASE_PASSWORD")
        self.database_host = os.getenv("DATABASE_HOST")
        self.database_port = os.getenv("DATABASE_PORT")
        self.database_name = os.getenv("DATABASE_NAME")
        self.engine = create_engine(
            f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}",
            echo=True,
            future=True,
        )
        Session = sessionmaker(self.engine)
        self.session = Session()

    #Login

    @staticmethod
    def login_user_domain(user):
        user_domain = UserDomain(
            user.name, 
            user.email,
            user.password,
            user.is_active, 
            user.created_at, 
            user.updated_at
        )
        return user_domain

    def login_user(
        self, 
        name: str, 
        password: str
    ):
        user = None
        token_value = None
        token_type = None
        user = self.session.query(
            User
        ).filter(
            User.name == name
        ).first()
        if user:
            user_domain= DataBase.create_user_domain(user)
            print("============================")
            print(user_domain.password)
            print(password)
            print(Hash_Password.bcrypt(password))
            print("============================")
            
            if Hash_Password.verify_pass(
                user_domain.password,
                password
            ):
                access_token = Token.create_access_token(
                    data={"sub": user_domain.name}
                )
                token_value = access_token
                token_type = "bearer"
            else:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = f"Incorrect password"
                )
        
        self.session.close()
        return {"user": user, "token": (token_value, token_type)}


    ##Users

    @staticmethod
    def create_user_domain(user):
        user_domain = UserDomain(
            user.id, 
            user.name, 
            user.email, 
            user.password,
            user.is_active, 
            user.created_at, 
            user.updated_at
        )
        return user_domain


    def create_user(
        self, 
        name: str, 
        email: str, 
        password: str
    ):
        user_domain = None
        user = User(
            name = name, 
            email = email, 
            password = Hash_Password.bcrypt(password)
        )
        try:
            if user:
                self.session.add(user)
                self.session.commit()
                user_domain = DataBase.create_user_domain(user)
                print("============================")
                print(user_domain.id)
                print("============================")
        except IntegrityError as e:
            assert isinstance(e.orig, UniqueViolation)
        self.session.close()
        return user_domain

    def get_user_id(
        self, 
        id: int, 
        get_current_user: UserData = Depends(GetCurrentUsers.get_current_user)
    ):
        user = None
        user = self.session.query(
            User
        ).filter(
            User.id == id
        ).first()
        self.session.close()
        return user





