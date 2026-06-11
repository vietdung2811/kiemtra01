from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Gaming
from rest_framework import serializers

class GamingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gaming
        fields = '__all__'

class GamingViewSet(viewsets.ModelViewSet):
    queryset = Gaming.objects.all()
    serializer_class = GamingSerializer
