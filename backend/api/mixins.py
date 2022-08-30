from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
