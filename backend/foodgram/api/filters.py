import django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = django_filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, value):
        if value:
            return queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, value):
        if value:
            return queryset.filter(
                shopping_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
