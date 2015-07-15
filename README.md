Udacity Full Stack Web Developer Project 3

Item Catalog

Python and Flask are used to provide the backend web server for this web app.
Uses SQLAlchemy to access an SQLite database of categoried items.
Bootstrap is used to provide a responsive UI experience and consistent nav bar
Cloudinary is used to upload pictures.
Users can be signed in after authentication with one of the following OAuth2 service providers:
    Google
    Facebook
    GitHub

To use this source:
1. setup the database by running the following from a shell prompt:
    /Item_Catalog$ python database_setup.python
2. setup Cloudinary by running the following from a shell prompt:
    sudo pip install cloudinary
3. start the web server by running the following from a shell prompt:
    /Item_Catalog$ python catalog_app.py
4. open a browser (tested with Chrome) and navigate to http://localhost:5000/
5. You can navigate around the app to view categories and items
6. Sign in and you can add and edit your own items.
