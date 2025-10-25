from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def get_users(request):
    return JsonResponse({"message": "Users API is working correctly!"})