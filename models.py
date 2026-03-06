from sqlalchemy import Column, Integer, String
from database import Base
import secrets
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean


# Modelo de base de datos
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    users = relationship("User", back_populates="institution")
    visitors = relationship("Visitor", back_populates="institution")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")

    institution_id = Column(Integer, ForeignKey("institutions.id"))
    institution = relationship("Institution", back_populates="users")


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    institution_id = Column(Integer, ForeignKey("institutions.id"))
    institution = relationship("Institution", back_populates="visitors")

    class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    message = Column(String)
    response = Column(String)

    department = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    institution_id = Column(Integer, ForeignKey("institutions.id"))