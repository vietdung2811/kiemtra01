from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import HomeAppliance
from rest_framework import serializers

class HomeApplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeAppliance
        fields = '__all__'

class HomeApplianceViewSet(viewsets.ModelViewSet):
    queryset = HomeAppliance.objects.all()
    serializer_class = HomeApplianceSerializer
