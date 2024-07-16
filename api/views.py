import logging
from datetime import date, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import Investor, Bill, CapitalCall
from .serializers import InvestorSerializer, BillSerializer, CapitalCallSerializer
from .utils import generate_bills_for_investor
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def index(request):
    return JsonResponse({"message": "Welcome to the API"})

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class InvestorViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    @action(detail=True, methods=['post'])
    def generate_bills(self, request, pk=None):
        try:
            investor = self.get_object()
            fee_percentage = request.data.get('fee_percentage')
            if fee_percentage is None:
                return Response({'error': 'Fee percentage is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            bill_date = date.today()
            due_date = bill_date + timedelta(days=30)
            
            bills = generate_bills_for_investor(investor, fee_percentage, bill_date, due_date)
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
            if new_status not in dict(CapitalCall.STATUS_CHOICES):
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
            capital_call.status = new_status
            capital_call.save()
            return Response(self.get_serializer(capital_call).data)
        except Exception as e:
            logger.error(f"Error updating capital call status: {str(e)}")
            return Response({'error': 'An unexpected error occurred while updating the status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)