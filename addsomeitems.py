from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
 
from database_setup import Base, Category, Item, User
 
engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

users = ["user1", "user2", "user3"]
categories = ["category1", "category2", "category3"]
items = ["item1", "item2", "item3"]

for u in users:
    user1 = User(name=u, email=u+"@work")
    session.add(user1)
    session.commit()
    for c in categories:
        cat1 = Category(name=c + "_" + u)
        session.add(cat1)
        session.commit()
        for i in items:
            item1 = Item(name =i, description = "description for "+i, categories = cat1, users=user1)
            session.add(item1)
            session.commit()


print "added menu items!"
