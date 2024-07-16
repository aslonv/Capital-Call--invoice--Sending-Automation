import logging
from decimal import Decimal, InvalidOperation
from datetime import date, timedelta

from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.http import JsonResponse

from .models import Investor, Bill, CapitalCall
from .serializers import InvestorSerializer, BillSerializer, CapitalCallSerializer
from .utils import generate_bills_for_investor

logger = logging.getLogger(__name__)

def index(request):
    return JsonResponse({"message": "Welcome to the API"})

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = StandardResultsSetPagination

class InvestorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows investors to be viewed or edited.

    This ViewSet implements caching for individual investor retrieval.
    Investors are cached for 1 hour after being fetched from the database.
    The cache is updated whenever an investor is modified.
    """
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    def get_object(self):
        """
        Retrieve an investor instance.

        This method implements caching. It first tries to get the investor
        from the cache. If not found, it retrieves the investor from the
        database and caches it for 1 hour.
        """
        pk = self.kwargs.get('pk')
        cache_key = f'investor_{pk}'
        
        # Try to get the investor from cache
        investor = cache.get(cache_key)
        
        if not investor:
            # If not in cache, get from database
            investor = super().get_object()
            # Cache the investor for 1 hour
            cache.set(cache_key, investor, timeout=3600)
        
        return investor

    def perform_update(self, serializer):
        """
        Update an investor instance.

        After updating the investor in the database, this method also
        updates the cached version of the investor.
        """
        investor = serializer.save()
        # Update the cache when the investor is updated
        cache_key = f'investor_{investor.id}'
        cache.set(cache_key, investor, timeout=3600)

    @action(detail=True, methods=['post'])
    def generate_bills(self, request, pk=None):
        """
        Generate bills for an investor.
        """
        try:
            investor = self.get_object()
            fee_percentage = request.data.get('fee_percentage')
            if fee_percentage is None:
                return Response({'error': 'Fee percentage is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                fee_percentage = Decimal(fee_percentage)
            except InvalidOperation:
                return Response({'error': 'Invalid fee percentage'}, status=status.HTTP_400_BAD_REQUEST)
            
            if fee_percentage <= 0:
                return Response({'error': 'Fee percentage must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            
            bill_date = date.today()
            due_date = bill_date + timedelta(days=30)
            bills = generate_bills_for_investor(investor, fee_percentage, bill_date, due_date)

            # Update the cached investor after generating bills
            cache_key = f'invest or_{investor.id}'
            cache.set(cache_key, investor, timeout=3600)

            return Response({'message': f'{len(bills)} bills generated for {investor.name}'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error generating bills: {str(e)}")
            return Response({'error': 'An unexpected error occurred while generating bills'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CapitalCallViewSet(viewsets.ModelViewSet):
    queryset = CapitalCall.objects.all()
    serializer_class = CapitalCallSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                capital_call = serializer.save()
                return Response(self.get_serializer(capital_call).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating capital call: {str(e)}")
                return Response({'error': 'An unexpected error occurred while creating the capital call'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        try:
            capital_call = self.get_object()
            new_status = request.data.get('status')
            if new_status not in dict(CapitalCall.Status.choices):
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
            capital_call.status = new_status
            capital_call.save()
            return Response(self.get_serializer(capital_call).data)
        except Exception as e:
            logger.error(f"Error updating capital call status: {str(e)}")
            return Response({'error': 'An unexpected error occurred while updating the status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
