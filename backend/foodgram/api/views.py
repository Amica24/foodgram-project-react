from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite, Follow, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag, User
)
from .serializers import (
    CropRecipeSerializer, FollowSerializer, IngredientSerializer,
    RecipeGetSerializer, RecipeSerializer, TagSerializer,
    UserCreateProfileSerializer, UserProfileSerializer
)
from .utils import create_shopping_list


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserCreateProfileSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__follower=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST, DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            Follow.objects.create(
                follower=request.user,
                author=author,
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        Follow.objects.filter(
            follower=request.user,
            author=author,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(Sum('amount'))
        shopping_list = create_shopping_list(ingredients)
        response = HttpResponse(
            shopping_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="ShoppingCart.txt"'
        )
        return response

    @staticmethod
    def _post_delete_method(request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists():
                return Response(
                    {'Рецепт уже добавлен'},
                    status=status.HTTP_404_NOT_FOUND
                )
            model.objects.create(
                user=request.user,
                recipe=recipe,
            )
            serializer = CropRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if model.objects.filter(
                user=request.user,
                recipe=recipe,
        ).exists():
            model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self._post_delete_method(request, pk, model=ShoppingCart)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._post_delete_method(request, pk, Favorite)
