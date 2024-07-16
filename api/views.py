from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Investor, Bill, CapitalCall
from .serializers import InvestorSerializer, BillSerializer, CapitalCallSerializer
from .utils import generate_bills_for_investor

@api_view(['GET'])
def index(request):
    return Response({'message': 'Welcome to the API!'})

class InvestorViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    @action(detail=True, methods=['post'])
    def generate_bills(self, request, pk=None):
        investor = self.get_object()
        fee_percentage = request.data.get('fee_percentage', 0.01)
        bill_date = timezone.now().date()
        due_date = bill_date + timezone.timedelta(days=30)

        bills = generate_bills_for_investor(investor, fee_percentage, bill_date, due_date)
        
        return Response({'message': f'{len(bills)} bills generated for {investor.name}'}, status=status.HTTP_201_CREATED)

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class CapitalCallViewSet(viewsets.ModelViewSet):
    queryset = CapitalCall.objects.all()
    serializer_class = CapitalCallSerializer

    @action(detail=False, methods=['post'])
    def create_for_investor(self, request):
        investor_id = request.data.get('investor_id')
        bill_ids = request.data.get('bill_ids', [])

        try:
            investor = Investor.objects.get(id=investor_id)
            bills = Bill.objects.filter(id__in=bill_ids, investor=investor)
            
            if not bills:
                return Response({'error': 'No valid bills found for this investor'}, status=status.HTTP_400_BAD_REQUEST)

            total_amount = sum(bill.amount for bill in bills)
            
            capital_call = CapitalCall.objects.create(
                investor=investor,
                total_amount=total_amount,
                iban=request.data.get('iban'),
                status='validated'
            )
            capital_call.bills.set(bills)

            return Response(CapitalCallSerializer(capital_call).data, status=status.HTTP_201_CREATED)
        except Investor.DoesNotExist:
            return Response({'error': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        capital_call = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(CapitalCall.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        capital_call.status = new_status
        capital_call.save()

        return Response(CapitalCallSerializer(capital_call).data)