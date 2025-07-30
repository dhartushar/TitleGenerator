from django.urls import path
from .views import SuggestTitlesView, HealthCheckView

urlpatterns = [
    path('suggest-titles/', SuggestTitlesView.as_view(), name='suggest-titles'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]