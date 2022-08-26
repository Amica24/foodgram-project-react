from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    TagsViewSet, IngredientsViewSet,
    RecipesViewSet, CustomUserViewSet
)

router = SimpleRouter()

router.register(
    'tags', TagsViewSet, basename='tags'
)
router.register(
    'ingredients', IngredientsViewSet, basename='ingredients'
)
router.register(
    'recipes', RecipesViewSet, basename='recipes'
)

urlpatterns = [
    path('users/subscriptions/', CustomUserViewSet.as_view(
        {'get': 'subscriptions', })
         ),
    path('users/<int:id>/subscribe/', CustomUserViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'})
         ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
