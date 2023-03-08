from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet

from common.serializers import StatusMixinSerializer


# from common.constants import roles
# from common.serializers.mixins import DictMixinSerializer


class ExtendedGenericViewSet(GenericViewSet):
    pass


class ListViewSet(ExtendedGenericViewSet, mixins.ListModelMixin):
    pass


class UpdateViewSet(ExtendedGenericViewSet, mixins.UpdateModelMixin):
    pass


class LCRUViewSet(
    ExtendedGenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    pass


class LCRUDViewSet(LCRUViewSet, mixins.DestroyModelMixin):
    pass


class StatusListMixinView(ListViewSet):
    serializer_class = StatusMixinSerializer
    pagination_class = None
    # model = None

    # def get_queryset(self):
    #     assert self.model, (
    #         '"%s" should either include attribute `model`' % self.__class__.__name__
    #     )
    #     return self.model.objects.filter(is_active=True)


#
#

#
#
# class LCUViewSet(ExtendedGenericViewSet,
#                  mixins.ListModelMixin,
#                  mixins.CreateModelMixin,
#                  mixins.UpdateModelMixin, ):
#     pass
#
#
# class LCDViewSet(ExtendedGenericViewSet,
#                  mixins.ListModelMixin,
#                  mixins.CreateModelMixin,
#                  mixins.DestroyModelMixin, ):
#     pass
#
#
# class ExtendedGenericAPIView(ExtendedView, GenericAPIView):
#     pass
#
#
# class ExtendedRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
#                                     mixins.UpdateModelMixin,
#                                     ExtendedGenericAPIView,
#                                     ):
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)
#
#
# class ExtendedCRUAPIView(mixins.RetrieveModelMixin,
#                          mixins.CreateModelMixin,
#                          mixins.UpdateModelMixin,
#                          ExtendedGenericAPIView):
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
