from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestorViewSet, BillViewSet, CapitalCallViewSet, index

router = DefaultRouter()
router.register(r'investors', InvestorViewSet)
router.register(r'bills', BillViewSet)
router.register(r'capital-calls', CapitalCallViewSet)

urlpatterns = [
    path('', index, name='api-index'),
    path('', include(router.urls)),
]