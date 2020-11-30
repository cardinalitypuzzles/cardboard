from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hunts.models import Hunt
from .serializers import HuntSerializer

# Right now IsAuthenticated ensures that only logged-in users
# can use the API, but it does not test permissions beyond that.
# TODO: per-hunt user permissions/authentication


class HuntAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        hunt = get_object_or_404(Hunt, pk=pk)
        serializer = HuntSerializer(hunt)
        return Response(serializer.data)
