from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def get_bookings(request):
    return JsonResponse({"message": "Bookings API is working correctly!"})