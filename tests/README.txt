==============================
Testing with Django-SQLAlchemy
==============================

Tests in Django-SQLAlchemy are implemented using the `Python Nose`_ testing 
framework.

Requirements
------------

* `Python Nose`_

* Django-SQLAlchemy Nose Plugin - included in test/nose-django-sqlalchemy 
  directory

.. _Python Nose: http://code.google.com/p/python-nose/


Installation
------------

Django-SQLAlchemy Nose Plugin must be installed with::

    python setup.py install


Configuration
-------------

To run tests just use::

    nosetests --with-django-sqlalchemy --with-doctests --doctest-extention=test

To make life easy, create the following in a ``.noserc`` or ``nose.cfg`` file
in your home directory. It should contain contents like the following, 
depending on the flags you want set::

	[nosetests]
	with-django-sqlalchemy=1
	with-doctest=1
	doctest-extension=test


About the Test Applications
---------------------------

The test applications are located in the apps directory.  There are several 
different apps set up that have different characteristics so they can be used 
to test different areas of functionality.

* **blog** - This is a standard blog app with ``Post`` and ``Category`` 
  models.  There is a ``ForeignKey`` between ``Post`` and ``Category``, so 
  apps that require testing this functionality without anything else more 
  complicated included should use this app.

* **categories** - The categories application contains a single 
  ``Category`` model that has an adjacency list (self-referntial) 
  relationship.  It also contains a custom manager that overrides the 
  ``get_query_set`` method to return only active items.

* **inventory** - The inventory application contains a ``Product`` and 
  ``Tag`` models, where there is a ``ManyToMany`` relationship between 
  ``Product`` and ``Tag``.  This application has the additional distinction
  of having customized primary keys for both models.

* **news** - The news application contains ``Reporter``, ``Source``, and 
  ``Article`` models.  It has a simple ``ManyToMany`` relationship between
  ``Article`` and ``Source``.  Additionally it has a ``ForeignKey`` 
  relationship between ``Article`` and ``Reporter``.  Finally it also uses
  customized ``related_name`` attributes to define the back reference of 
  the relationship.

* **norelations** - The norelations application is a very basic application
  that contains a single ``Person`` model.  It is the simplest of cases. 

Included in the ``tests/apps`` directory is a ``manage.py`` module that can
be used to test any of the test applications out in the shell, just like
you normally would.  

By default the ``settings.py`` module in that directory
mimics the ``settings.py`` in the main ``tests`` directory with the exception
that the database is set to a regular sqlite database.

Please refrain from committing any temporary databases that you may create in
the course of testing the applications.