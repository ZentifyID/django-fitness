from django.shortcuts import render
from members.models import MembershipPlan

def index(request):
    return render(request, 'index.html')

def pricing(request):
    plans = MembershipPlan.objects.all().order_by('price')
    return render(request, 'pricing.html', {'plans': plans})
