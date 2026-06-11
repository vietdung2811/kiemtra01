from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Networking
from rest_framework import serializers

class NetworkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Networking
        fields = '__all__'

class NetworkingViewSet(viewsets.ModelViewSet):
    queryset = Networking.objects.all()
    serializer_class = NetworkingSerializer
