from recipes.models import RecipeIngredient
from django.db.models import Sum
from django.http import HttpResponse


def create_shopping_cart(user):
    shopping_list = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amount_total=Sum('amount')
    ).order_by()

    result_string = 'Список покупок: \n '
    for count, ingredient in enumerate(shopping_list, start=1):
        result_string += (
            f'{count}. {ingredient["ingredient__name"]}. '
            f'Кол-во для рецептов {ingredient["amount_total"]} '
            f'{ingredient["ingredient__measurement_unit"]} \n '
        )

    return HttpResponse(result_string, content_type='text/plain')
