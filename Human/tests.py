import json
import os

from django.test import TestCase

# Create your tests here.
from Human.constants import STATIC_FOLDER

j = json.load(file(os.path.join(STATIC_FOLDER, 'data/cities.json')))

print j["People's Republic of China"]

