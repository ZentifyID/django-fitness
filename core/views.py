from django.shortcuts import render
from members.models import MembershipPlan
from blog.models import Post
from schedule.models import Trainer

def index(request):
    latest_posts = Post.objects.all()[:3]
    trainers = Trainer.objects.all()[:4]
    return render(request, 'index.html', {
        'latest_posts': latest_posts,
        'trainers': trainers
    })

def pricing(request):
    plans = MembershipPlan.objects.all().order_by('price')
    return render(request, 'pricing.html', {'plans': plans})
