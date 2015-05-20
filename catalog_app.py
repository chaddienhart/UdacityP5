from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).group_by(Category.name).distinct()
    #items = session.query(Item).filter_by(restaurant_id = restaurant_id)
    return render_template('catalog.html', categories=categories)

@app.route('/catalog/<string:category_name>/items/')
def items(category_name):
    print category_name
    category = session.query(Category).filter_by(name = category_name).first()
    print category.name
    itemgroup = session.query(Item).filter(Item.category_id == category.id).all()
    for i in itemgroup:
        print i.name
    return render_template('items.html', category_name=category_name, items=itemgroup)

if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
