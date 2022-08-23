from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping, Tag)
from users.models import SubscribeAuthor
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .pagination import CustomPagination
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipeSerializer, SubscriptionRecipeSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)


class UserViewSet(UserViewSet):
    pagination_class = CustomPagination

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if SubscribeAuthor.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = SubscribeAuthor.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if SubscribeAuthor.objects.filter(user=user, author=author).exists():
            follow = get_object_or_404(
                SubscribeAuthor,
                user=user,
                author=author
            )
            follow.delete()
            return Response(
                'Вы успешно отписались',
                status=status.HTTP_204_NO_CONTENT
            )
        if user == author:
            return Response(
                {'errors': 'Нельзя отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def subscriptions(self, request):
        user = request.user
        queryset = SubscribeAuthor.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response('Успешно удален',
                        status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action != 'create':
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'],)
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            data = SubscriptionRecipeSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, pk=pk)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            return Response(
                'Избранное успешно удалено',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'errors': 'Избранное не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['POST', 'DELETE'],)
    def shopping_cart(self, request, pk):
        if self.request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Shopping.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Shopping.objects.get_or_create(user=request.user, recipe=recipe)
            data = SubscriptionRecipeSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, pk=pk)
        if Shopping.objects.filter(user=request.user, recipe=recipe).exists():
            shopping = get_object_or_404(
                Shopping,
                user=request.user,
                recipe=recipe
            )
            shopping.delete()
            return Response(
                'Из списка покупок успешно удалено',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'errors': 'Рецепта нет в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
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
