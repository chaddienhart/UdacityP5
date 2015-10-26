import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class User(Base):
    __tablename__ = 'users'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(250),  unique=True)
    picture = Column(String(250))
    __table_args__ = {'sqlite_autoincrement': True}
    @property
    def serialize(self):
        return {
            'name' : self.name,
            'email' : self.email,
            'id' : self.id,
            'picture' : self.picture
        }

class Category(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name' : self.name,
            'id' : self.id
        }
    
class Item(Base):
    __tablename__ = 'items'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer,ForeignKey('categories.id', ondelete='CASCADE'))
    categories = relationship(Category)
    user_id = Column(Integer,ForeignKey('users.id', ondelete='CASCADE'))
    users = relationship(User)
    #date_added = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'name' : self.name,
            'description' : self.description,
            'added by' : self.user_id,
            'category' : self.category_id,
            'id' : self.id,
            'picture' : self.picture,
            #'date added' : self.date_added
        }

engine = create_engine('postgres://postgres@/catalog')

Base.metadata.create_all(engine)

