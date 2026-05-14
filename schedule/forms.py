from django import forms
from .models import TrainerReview

class TrainerReviewForm(forms.ModelForm):
    class Meta:
        model = TrainerReview
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш отзыв...'}),
        }
