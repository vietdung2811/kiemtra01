from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Accessory
from rest_framework import serializers

class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessory
        fields = '__all__'

class AccessoryViewSet(viewsets.ModelViewSet):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
