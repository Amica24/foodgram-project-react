import django_filters
from rest_framework import filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags',
        lookup_expr='slug'
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags'
        )


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
