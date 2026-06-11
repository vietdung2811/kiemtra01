from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Tablet
from rest_framework import serializers

class TabletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tablet
        fields = '__all__'

class TabletViewSet(viewsets.ModelViewSet):
    queryset = Tablet.objects.all()
    serializer_class = TabletSerializer
