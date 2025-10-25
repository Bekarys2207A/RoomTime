from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def get_rooms(request):
    return JsonResponse({"message": "Rooms API is working correctly!"})