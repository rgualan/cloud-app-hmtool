# appengine_config.py
# Include lib folder that contains required libraries in appengine path

from google.appengine.ext import vendor
import os

# vendor.add('lib')
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
