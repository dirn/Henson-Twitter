==============
Henson-Twitter
==============

A library for consuming Tweets through Henson.

Installation
============

.. code::

    $ python -m pip install Henson-Twitter

Quickstart
==========

.. code::

    from henson import Application
    from henson_twitter import Twitter

    app = Application('tweeter')
    twitter = Twitter(app)
