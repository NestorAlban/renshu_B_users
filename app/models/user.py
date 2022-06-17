from sqlalchemy import (
    Column, 
    ForeignKey, 
    String, 
    Integer, 
    DateTime, 
    Boolean,
    func
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user_password"

    id = Column(
        Integer, 
        primary_key = True
    )
    name = Column(
        String, 
        nullable = False, 
        unique = True
    )
    email = Column(
        String, 
        nullable = False, 
        unique = True
    )
    password = Column(
        String, 
        nullable = False, 
        unique = True
    )
    is_active = Column(
        Boolean(), 
        default = True, 
        nullable = False
    )
    created_at = Column(
        DateTime, 
        default = func.now(), 
        nullable = False
    )
    updated_at = Column(
        DateTime, 
        default = func.now(), 
        nullable = False, 
        onupdate = func.now()
    )
