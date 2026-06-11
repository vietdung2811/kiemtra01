from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Camera
from rest_framework import serializers

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
