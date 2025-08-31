from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import CurrencyRate
from .serializers import CurrencyRateSerializer
from Core.models import Currency


class CurrencyRateListView(generics.ListAPIView):
    """Get all latest currency rates"""
    serializer_class = CurrencyRateSerializer
    
    def get_queryset(self):
        # Get the latest rate for each currency
        latest_rates = []
        currencies = CurrencyRate.objects.values_list('currency_code', flat=True).distinct()
        
        for currency in currencies:
            latest_rate = CurrencyRate.objects.filter(
                currency_code=currency
            ).order_by('-date_fetched').first()
            if latest_rate:
                latest_rates.append(latest_rate)
        
        return latest_rates


class CurrencyRateDetailView(generics.ListAPIView):
    """Get latest rate for a specific currency"""
    serializer_class = CurrencyRateSerializer
    
    def get_queryset(self):
        currency_code = self.kwargs.get('currency_code', '').upper()
        return CurrencyRate.objects.filter(
            currency_code=currency_code
        ).order_by('-date_fetched')[:1]


@api_view(['GET'])
def currency_rate_by_code(request, currency_code):
    """Get latest rate for a specific currency with English and Farsi names"""
    try:
        latest_rate = CurrencyRate.objects.filter(
            currency_code=currency_code.upper()
        ).order_by('-date_fetched').first()
        
        if not latest_rate:
            return Response(
                {'error': f'Currency {currency_code.upper()} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get currency details from Core.Currency model
        currency_details = Currency.objects.filter(code=currency_code.upper()).first()
        
        response_data = {
            'currency_code': latest_rate.currency_code,
            'rate': latest_rate.rate,
            'base_currency': latest_rate.base_currency,
            'bank_name': latest_rate.bank_name,
            'country_code': latest_rate.country_code,
            'date_fetched': latest_rate.date_fetched,
        }
        
        # Add currency names if available
        if currency_details:
            response_data.update({
                'name': currency_details.name,
                'name_english': currency_details.name_english,
                'name_farsi': currency_details.name_farsi,
                'symbol': currency_details.symbol
            })
        
        return Response(response_data)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def all_latest_rates(request):
    """Get all latest rates with English and Farsi names"""
    try:
        # Get latest rate for each currency
        currencies = CurrencyRate.objects.values_list('currency_code', flat=True).distinct()
        rates_data = {}
        
        for currency in currencies:
            latest_rate = CurrencyRate.objects.filter(
                currency_code=currency
            ).order_by('-date_fetched').first()
            
            if latest_rate:
                # Get currency details from Core.Currency model
                currency_details = Currency.objects.filter(code=currency).first()
                
                rate_info = {
                    'rate': float(latest_rate.rate),
                    'base_currency': latest_rate.base_currency,
                    'bank_name': latest_rate.bank_name,
                    'last_updated': latest_rate.date_fetched
                }
                
                # Add currency names if available
                if currency_details:
                    rate_info.update({
                        'name': currency_details.name,
                        'name_english': currency_details.name_english,
                        'name_farsi': currency_details.name_farsi,
                        'symbol': currency_details.symbol
                    })
                
                rates_data[currency] = rate_info
        
        return Response({
            'success': True,
            'rates': rates_data,
            'total_currencies': len(rates_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
