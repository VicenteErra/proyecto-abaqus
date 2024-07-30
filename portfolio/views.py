from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from portfolio.models import Portfolio, Asset, Price, Quantity
from django.db.models import Sum, F
from decimal import Decimal
import datetime

class PortfolioDataAPIView(APIView):
    def get(self, request):
        start_date, end_date = self.get_date_range(request)

        if start_date is None or end_date is None:
            return Response({'error': 'Debe proporcionar fecha de inicio y fin'}, status=status.HTTP_400_BAD_REQUEST)

        portfolios = Portfolio.objects.all()
        results = [self.get_portfolio_data(portfolio, start_date, end_date) for portfolio in portfolios]

        return Response(results, status=status.HTTP_200_OK)


    def get_date_range(self, request):

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return None, None

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            return start_date, end_date
        except ValueError:
            return None, None


    def get_portfolio_data(self, portfolio, start_date, end_date):
        
        portfolio_data = {'portfolio': portfolio.name, 'data': []}
        quantities = Quantity.objects.filter(portfolio=portfolio)

        for date in self.date_range(start_date, end_date):
            V_t, weights = self.calculate_portfolio_metrics(quantities, date)
            portfolio_data['data'].append({
                'date': date,
                'V_t': V_t,
                'weights': weights
            })

        return portfolio_data

    def date_range(self, start_date, end_date):

        return (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days + 1))

    def calculate_portfolio_metrics(self, quantities, date):

        prices = Price.objects.filter(asset__in=[quantity.asset for quantity in quantities], date=date)
        V_t = sum(quantity.quantity * price.value for quantity in quantities for price in prices if quantity.asset == price.asset)

        weights = [
            {
                'asset': quantity.asset.name,
                'weight': self.calculate_weight(quantity, prices, V_t)
            }
            for quantity in quantities
        ]

        return V_t, weights

    def calculate_weight(self, quantity, prices, V_t):
        
        price = prices.get(asset=quantity.asset)
        x_i_t = quantity.quantity * price.value if price else 0
        return x_i_t / V_t if V_t != 0 else 0

