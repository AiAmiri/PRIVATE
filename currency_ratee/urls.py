from django.urls import path
from . import views

urlpatterns = [
    # Get all latest rates (detailed format)
    path('rates/', views.CurrencyRateListView.as_view(), name='currency-rates-list'),
    
    # Get latest rate for specific currency (detailed format)
    path('rates/<str:currency_code>/', views.CurrencyRateDetailView.as_view(), name='currency-rate-detail'),
    
    # Simple endpoints
    path('rate/<str:currency_code>/', views.currency_rate_by_code, name='currency-rate-simple'),
    path('latest/', views.all_latest_rates, name='all-latest-rates'),
]
