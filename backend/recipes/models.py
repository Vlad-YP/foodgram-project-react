from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=55
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField(
        'Наименование тега',
        max_length=55,
        unique=True
    )
    color = models.CharField(
        'Код цвета тега',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'Slug',
        max_length=55,
        unique=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipe'
    )
    name = models.CharField(
        'Наименование рецепта',
        max_length=255
    )
    text = models.TextField(
        'Текст рецепта'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='static/recipe/',
        blank=False,
        null=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин',
        validators=(
            validators.MinValueValidator(
                settings.COOKING_TIME_MIN, message=settings.COOKING_TIME_ERROR
            ),
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        'ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.FloatField(
        validators=(
            validators.MinValueValidator(
                settings.INGREDIENT_AMOUNT_MIN,
                message=settings.INGREDIENT_AMOUNT_ERROR
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Кол-во ингредиента'
        verbose_name_plural = 'Кол-во ингредиентов'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredient'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранное пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipes'
            )
        ]


class Shopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Список покупок пользователя',
        related_name='shopping_cart'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipes'
            )
        ]
