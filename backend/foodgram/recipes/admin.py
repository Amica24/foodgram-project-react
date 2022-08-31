from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite, Follow, Ingredient, IngredientRecipe,
    Recipe, RecipeTag, ShoppingCart, Tag, User
)


class CustomUserAdmin(UserAdmin):
    list_filter = ('first_name', 'email')


class IngredientAmount(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites__count')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients',)
    inlines = [IngredientAmount,]

    @admin.display(description='В избранном')
    def favorites__count(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'measurement_unit')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(RecipeTag)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
