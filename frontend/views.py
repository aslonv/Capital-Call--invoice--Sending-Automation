# frontend/views.py

from django.shortcuts import render
from django.views import View
from api.models import Investor, Bill, CapitalCall

class IndexView(View):
    def get(self, request):
        investors = Investor.objects.all()
        bills = Bill.objects.all()
        capital_calls = CapitalCall.objects.all()
        return render(request, 'index.html', {
            'investors': investors,
            'bills': bills,
            'capital_calls': capital_calls
        })