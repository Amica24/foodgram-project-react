from csv import DictReader
import logging
import os
import sys

from django.core.management import BaseCommand

from recipes.models import Ingredient

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            logger.error('Ingredient data already loaded...exiting.')
            return

        logger.info('Loading Ingredient data')

        path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'static', 'data',
            'ingredients.csv'
        )
        for row in DictReader(open(path)):
            ingredient = Ingredient(
                name=row['name'],
                measurement_unit=row['unit'],
            )
            ingredient.save()
