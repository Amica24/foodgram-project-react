import os

from csv import DictReader
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print('Ingredient data already loaded...exiting.')
            return

        print('Loading Ingredient data')

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
