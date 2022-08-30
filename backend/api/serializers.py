from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping, Tag)
from users.models import SubscribeAuthor, User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return SubscribeAuthor.objects.filter(user=user, author=obj).exists()


class SubscriptionListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, author):
        return SubscribeAuthor.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=author)
        if limit:
            queryset = queryset[:int(limit)]
        return FavoriteRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeAuthor
        fields = ('user', 'author')

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            get_object_or_404(User, username=data['author'])
            if self.context['request'].user == data['author']:
                raise serializers.ValidationError({
                    'errors': 'На себя подписываться нельзя.'
                })
            if SubscribeAuthor.objects.filter(
                user=self.context['request'].user,
                author=data['author']
            ):
                raise serializers.ValidationError({
                    'errors': 'Вы уже подписаны.'
                })
            return data

        if self.context['request'].user == data['author']:
            raise serializers.ValidationError({
                'errors': 'Нельзя отписаться от самого себя.'
            })
        if SubscribeAuthor.objects.filter(
            user=self.context['request'].user,
            author=data['author']
        ).exists() is False:
            raise serializers.ValidationError({
                'errors': 'Вы не подписаны.'
            })
        return data

    def to_representation(self, instance):
        return SubscriptionListSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if self.context.get('request').method == 'POST':
            if not request or request.user.is_anonymous:
                return False
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError({
                    'errors': 'Уже есть в избранном.'
                })
            return data
        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists() is False:
            raise serializers.ValidationError({
                'errors': 'Избранное не существует.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FavoriteRecipeSerializer(
            instance.recipe, context=context
        ).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['recipe', 'user']
        model = Shopping

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if self.context.get('request').method == 'POST':
            if Shopping.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                raise serializers.ValidationError({
                    'errors': 'Рецепт уже в списке покупок'
                })
            return data
        if Shopping.objects.filter(
                user=request.user, recipe=recipe
        ).exists() is False:
            raise serializers.ValidationError({
                'errors': 'Рецепта нет в списке покупок'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FavoriteRecipeSerializer(instance.recipe, context=context).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.FloatField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'recipe')


class IngredientRecipeAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class IngredientsRecipeAddSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsRecipeAddSerializer(many=True)
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'text', 'ingredients', 'tags',
            'cooking_time', 'image'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients_list = []
        if not data['ingredients']:
            raise serializers.ValidationError(
                'Добавьте ингридиенты')
        for ingredient in data['ingredients']:
            ingredient_db = get_object_or_404(Ingredient, id=ingredient['id'])
            if ingredient_db in ingredients_list:
                raise serializers.ValidationError(
                    f'{ingredient_db} - уже добавлен в рецепт'
                )
            if float(ingredient['amount']) < settings.INGREDIENT_AMOUNT_MIN:
                raise serializers.ValidationError(
                    settings.INGREDIENT_AMOUNT_ERROR
                )
            ingredients_list.append(ingredient_db)

        if not data['tags']:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег'
            )

        if int(data['cooking_time']) < settings.COOKING_TIME_MIN:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше минуты'
            )
        return data

    @staticmethod
    def __create_ingredients(ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.__create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.__create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientRecipeAmountSerializer(
            RecipeIngredient.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        return representation


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'text', 'ingredients', 'tags',
            'cooking_time', 'is_favorited', 'image',
            'is_in_shopping_cart'
        )
        read_only_fields = ('id', 'author',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientRecipeAmountSerializer(
            recipe_ingredients,
            many=True
        ).data
