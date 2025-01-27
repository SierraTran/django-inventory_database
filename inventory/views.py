from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
# @login_required
def items(request):
    return HttpResponse('Hello. This is the items page.')

# @login_required
def more_info(request):
    return HttpResponse('Information about the item will be shown here.')