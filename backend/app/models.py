# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)                  # "male", "female", etc.
    traits = Column(ARRAY(Text), nullable=True)              # список черт характера NPC
    attitude = Column(String(100), nullable=True)            # отношение к игроку (напр. "дружелюбный")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    # связь с локацией (один-ко-многим)
    location = relationship("Location", back_populates="characters")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    reputation_levels = Column(ARRAY(Text), nullable=True)   # список описаний уровней репутации
    points_of_interest = Column(ARRAY(Text), nullable=True)  # список достопримечательностей/особенностей локации
    # связь с персонажами (многие-к-одному)
    characters = relationship("Character", back_populates="location")

class Lore(Base):
    __tablename__ = "lore"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)   # текст глобального лора/сюжет
    # В таблице предполагается одна запись (id=1)

class Dialogue(Base):
    __tablename__ = "dialogue"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    role = Column(String(10), nullable=False)    # "user" или "assistant"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Опционально: связь с Character, если нужен доступ к данным персонажа
    character = relationship("Character")
