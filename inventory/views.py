from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def items(request):
    return HttpResponse('Hello. This is the items page.')