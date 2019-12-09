"""
A stub for the future tag library to address the registered tag issue
that arises with Django 1.10
"""
from __future__ import unicode_literals
from django.template import Library

register = Library()
