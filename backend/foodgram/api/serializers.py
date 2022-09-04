from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, User)
from rest_framework import serializers


class UserCreateProfileSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        read_only_fields = ('id',)


class UserProfileSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = ('id', 'username')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Follow.objects.filter(
            follower=current_user,
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.FloatField()

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    author = UserProfileSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_tags(self, obj):
        tags = Tag.objects.filter(recipe=obj)
        return TagSerializer(tags, many=True).data

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=current_user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=current_user,
            recipe=obj
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, allow_null=True
    )
    ingredients = IngredientRecipeSerializer(many=True)
    author = UserProfileSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить игредиенты'
            )
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            ingredient_item = get_object_or_404(
                Ingredient,
                id=ingredient_id
            )
            if ingredient_item in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными'
                )
            ingredients_list.append(ingredient_item)
            amount = ingredient.get('amount')
            if int(amount) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента указано неверно или'
                    'значние равняется нулю'
                )
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Необходимо выбрать теги'
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэги должны быть уникальными!'
                )
            tags_list.append(tag)
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовление указано неверно!'
            )

        data['ingredients'] = ingredients
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    @staticmethod
    def create_tags(recipe, tags_data):
        tags = []
        for name in tags_data:
            tag = get_object_or_404(Tag, name=name.name)
            tags.append(tag)
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_tags(recipe=recipe, tags_data=tags_data)
        self.create_ingredients(recipe=recipe, ingredients=ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        tags = validated_data.get('tags')
        self.create_tags(recipe=instance, tags_data=tags)
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        return instance
        # return super().update(instance, validated_data)

    def to_representation(self, recipe):
        data = RecipeGetSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data
        return data


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        follower = self.context.get('request').user
        follow = Follow.objects.filter(
            follower=follower,
            author=author
        )
        if self.context.get('request').method == 'POST':
            if follow.exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора!'
                )
            elif follower == author:
                raise serializers.ValidationError(
                    'Вы не можете подписаться на самого себя!'
                )
        elif self.context.get('request').method == 'DELETE':
            if not follow.exists():
                raise serializers.ValidationError(
                    'Вы еще не подписаны на этого автора!'
                )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes.all()[:int(limit)]
        return CropRecipeSerializer(
            recipes,
            context={'request': request},
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return CropRecipeSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return CropRecipeSerializer(
            instance.recipe,
            context=context
        ).data
