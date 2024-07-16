default_app_config = 'api.apps.ApiConfig'

def get_models():
    from .models import Investor, Bill, CapitalCall
    return Investor, Bill, CapitalCall

def get_views():
    from .views import InvestorViewSet, BillViewSet, CapitalCallViewSet
    return InvestorViewSet, BillViewSet, CapitalCallViewSet

def get_serializers():
    from .serializers import InvestorSerializer, BillSerializer, CapitalCallSerializer
    return InvestorSerializer, BillSerializer, CapitalCallSerializer

def get_utils():
    from .utils import calculate_membership_fee, calculate_upfront_fee, calculate_yearly_fee
    return calculate_membership_fee, calculate_upfront_fee, calculate_yearly_fee