# Generated by Django 4.1 on 2022-08-28 16:44

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Наименование ингридиента')),
                ('measurement_unit', models.CharField(max_length=55, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование рецепта')),
                ('text', models.TextField(verbose_name='Текст рецепта')),
                ('image', models.ImageField(null=True, upload_to='static/recipe/', verbose_name='Изображение')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное время приготовления 1 мин.')], verbose_name='Время приготовления, мин')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True, verbose_name='Наименование тега')),
                ('color', models.CharField(max_length=7, unique=True, verbose_name='Код цвета тега')),
                ('slug', models.SlugField(max_length=55, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Shopping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='Список покупок')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок пользователя')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.1, message='Ингредиент не может быть пустым')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.recipe')),
            ],
            options={
                'verbose_name': 'Кол-во ингридиента',
                'verbose_name_plural': 'Кол-во ингредиентов',
                'ordering': ('-id',),
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.RecipeIngredient', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.tag', verbose_name='Теги рецепта'),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Рецепт в избранном')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Избранное пользователя')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
            },
        ),
        migrations.AddConstraint(
            model_name='shopping',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_cart_user_recipes'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_recipes'),
        ),
    ]
