Tests are implemented using the Python Nose testing framework.

Requirements: 

  Python Nose - http://code.google.com/p/python-nose/
  Django-SQLAlchemy Nose Plugin - included in nose-django-sqlalchemy directory

Installation:

Django-SQLAlchemy Nose Plugin must be installed with:

python setup.py install


Configuration:

To run tests just use:

nosetests --with-django-sqlalchemy --with-doctests --doctest-extention=test

To make life easy, create the following in a .noserc or nose.cfg file in your home directory:

[nosetests]
with-django-sqlalchemy=1
with-doctest=1
doctest-extension=test
