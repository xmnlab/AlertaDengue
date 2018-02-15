from django.apps import apps
from django.test import TestCase
from datetime import datetime, timedelta

import os
import django
import numpy as np
import unittest

from .. import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gis.settings")
django.setup()

from ..models import SatelliteClimate
from dados.dbdata import db_engine

City = apps.get_model('dados', 'City')


class TestSatelliteClimate(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with db_engine.connect() as conn:
            path = os.path.dirname(settings.BASE_DIR)
            path = os.path.join(
                path, 'sql', 'create_table_satellite_climate.sql'
            )

            with open(path) as f:
                conn.execute(f.read())

    def setUp(self):
        pass

    def test_save(self):
        dt = datetime.now()
        city = City.objects.get(geocode=3304557)

        ndvi = np.random.random()
        precipitation = np.random.random()
        temperature_max = np.random.random()
        temperature_min = np.random.random()
        relative_humidity = np.random.random()
        specific_humidity = np.random.random()

        v = True

        while v:
            v = SatelliteClimate.objects.filter(
                city=city, images_date=dt
            ).exists()

            dt = dt + timedelta(days=1)

        SatelliteClimate.objects.create(
            city=city,  # MRJ
            images_date=dt,
            ndvi=ndvi,
            precipitation=precipitation,
            temperature_max=temperature_max,
            temperature_min=temperature_min,
            relative_humidity=relative_humidity,
            specific_humidity=specific_humidity
        )

        m = SatelliteClimate.objects.get(
            city=city, images_date=dt
        )

        np.testing.assert_almost_equal(m.ndvi, ndvi)
        np.testing.assert_almost_equal(m.precipitation, precipitation)
        np.testing.assert_almost_equal(m.temperature_max, temperature_max)
        np.testing.assert_almost_equal(m.temperature_min, temperature_min)
        np.testing.assert_almost_equal(m.relative_humidity, relative_humidity)
        np.testing.assert_almost_equal(m.specific_humidity, specific_humidity)


if __name__ == '__main__':
    unittest.main()
