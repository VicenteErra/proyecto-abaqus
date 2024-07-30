from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from portfolio.models import Portfolio, Asset, Price, Quantity
from django.db.models import Sum, F
from decimal import Decimal
import datetime
import requests
import plotly.graph_objects as go

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


def compare_portfolios(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        return render(request, 'compare.html', {'error': 'Debe proporcionar fecha_inicioo y fecha_fin'})

    # Llamar a la API
    response = requests.get(f'http://localhost:8000/portfolio-data?start_date={start_date}&end_date={end_date}')
    data = response.json()
    
    # Preparar los datos para los gráficos
    dates = []
    weights_data = {}
    values_data = {}
    
    for portfolio in data:
        portfolio_id = portfolio['portfolio']
        for entry in portfolio['data']:
            dates.append(entry['date'])
            V_t = entry['V_t']
            if portfolio['portfolio'] not in values_data:
                values_data[portfolio['portfolio']] = []
            values_data[portfolio['portfolio']].append(V_t)
            
            for weight in entry['weights']:
                asset = weight['asset']
                if asset not in weights_data:
                    weights_data[asset] = []
                weights_data[asset].append(weight['weight'])
    
    # Crear gráfico de áreas apiladas para los pesos
    fig_weights = go.Figure()
    
    for asset, weights in weights_data.items():
        fig_weights.add_trace(go.Scatter(
            x=dates,
            y=weights,
            mode='lines+markers',
            name=asset,
            stackgroup='one'  # Áreas apiladas
        ))
    
    fig_weights.update_layout(title='Evolución de los Pesos de los Activos',
                               xaxis_title='Fecha',
                               yaxis_title='Peso',
                               hovermode='x unified')
    
    # Crear gráfico de líneas para V_t
    fig_values = go.Figure()
    
    for portfolio, values in values_data.items():
        fig_values.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=portfolio
        ))
    
    fig_values.update_layout(title='Evolución del Valor de los Portafolios',
                              xaxis_title='Fecha',
                              yaxis_title='Valor ($)',
                              hovermode='x unified')

    # Convertir figuras a HTML
    weights_graph = fig_weights.to_html(full_html=False)
    values_graph = fig_values.to_html(full_html=False)
    
    return render(request, 'compare.html', {
        'weights_graph': weights_graph,
        'values_graph': values_graph
    })
