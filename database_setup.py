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

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250),  primary_key = True)
    picture = Column(String(250))

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
    category_id = Column(Integer,ForeignKey('categories.id'))
    categories = relationship(Category)
    user_id = Column(Integer,ForeignKey('users.id'))
    users = relationship(User)
    #date_added = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'picture' : self.picture,
            'added by' : self.user_id,
            'date added' : self.date_added
        }
        



engine = create_engine('sqlite:///itemcatalog.db')
 

Base.metadata.create_all(engine)

