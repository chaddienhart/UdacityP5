# Udacity Full Stack Web Developer Project 3

# Item Catalog

#### Python and Flask are used to provide the backend web server for this web app.
#### Uses SQLAlchemy to access an SQLite database of categoried items.
#### Bootstrap is used to provide a responsive UI experience and consistent nav bar
#### Cloudinary is used to upload pictures.

#### Users can be signed in after authentication with one of the following OAuth2 service providers:
* Google
* Facebook
* GitHub

#### To use this source:
1. setup Cloudinary by running the following from a shell prompt:
    * sudo pip install cloudinary
2. start the web server by running the following from a shell prompt:
    * /Item_Catalog$ python catalog_app.py
3. open a browser (tested with Chrome) and navigate to
    * http://localhost:5000/
4. You can navigate around the app to view categories and items
5. Sign in and you can add and edit your own items.
6. Support JSON from the following:
    * /catalog/JSON
    * /catalog/category/<int:category_id>/JSON
    * /catalog/viewItem/<int:item_id>/JSON
    * /catalog/myItems/<int:user_id>/JSON

#### Designed for use with:
* SQLite  -- version 3.8.9
* SQLAchemy (http://www.sqlalchemy.org/) -- version 0.8.4
* Python (https://www.python.org/downloads/) -- version 2.7.6
* Flask (http://flask.pocoo.org/) -- version 0.10.1
* Bootstrap (http://getbootstrap.com/) -- version 3.3.4 (included in this repository)
