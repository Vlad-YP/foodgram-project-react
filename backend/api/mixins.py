from rest_framework.permissions import AllowAny
from rest_framework import mixins, viewsets


class ListRetrieveViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
