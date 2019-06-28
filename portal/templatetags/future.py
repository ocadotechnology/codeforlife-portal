"""
A stub for the future tag library to address the registered tag issue
that arises with Django 1.10
"""
from django.template import Library
from django.template.defaulttags import cycle as cycle_original

register = Library()
