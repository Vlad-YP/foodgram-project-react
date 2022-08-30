from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag
from users.models import SubscribeAuthor
from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveViewSet
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeGetSerializer,
                          RecipeSerializer, SubscriptionListSerializer,
                          SubscriptionSerializer, TagSerializer)
from .utils import create_shopping_cart

User = get_user_model()


class UserViewSet(UserViewSet):
    pagination_class = CustomPagination

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=('POST', 'DELETE')
    )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={
                    'user': request.user.id,
                    'author': get_object_or_404(User, id=id).id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = SubscriptionSerializer(
            data={
                'user': request.user.id,
                'author': get_object_or_404(User, id=id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        subscription = get_object_or_404(
            SubscribeAuthor,
            author=get_object_or_404(User, id=id),
            user=request.user
        )
        self.perform_destroy(subscription)
        return Response(
            'Вы успешно отписались',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=('GET',)
    )
    def subscriptions(self, request):
        subscriptions = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = SubscriptionListSerializer(
            subscriptions, many=True, context={'request': request}
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
        return Response(
            'Успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )

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

    @staticmethod
    def __add_object_action(request, pk, serializer_in_view):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_in_view(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def __del_object_action(request, pk, serializer_in_view, model):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_in_view(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(
            model,
            user=request.user,
            recipe=recipe
        )
        model_instance.delete()
        return Response(
            'Успешно удалено',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=('POST',),)
    def favorite(self, request, pk):
        return self.__add_object_action(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.__del_object_action(
            request,
            pk,
            FavoriteSerializer,
            Favorite
        )

    @action(detail=True, methods=('POST',),)
    def shopping_cart(self, request, pk):
        return self.__add_object_action(request, pk, CartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.__del_object_action(
            request,
            pk,
            CartSerializer,
            Shopping
        )

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        return create_shopping_cart(user=request.user)
