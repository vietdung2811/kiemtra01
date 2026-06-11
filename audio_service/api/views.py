from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Audio
from rest_framework import serializers

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = '__all__'

class AudioViewSet(viewsets.ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
