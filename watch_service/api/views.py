from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Watch
from rest_framework import serializers

class WatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watch
        fields = '__all__'

class WatchViewSet(viewsets.ModelViewSet):
    queryset = Watch.objects.all()
    serializer_class = WatchSerializer
