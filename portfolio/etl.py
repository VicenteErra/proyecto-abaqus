import pandas as pd
from portfolio.models import Asset, Weight, Price, Portfolio, Quantity
from django.utils import timezone

def load_data_from_excel(file_path):

    Portfolio.objects.get_or_create(name='Portafolio 1', initial_value=1000000000)
    Portfolio.objects.get_or_create(name='Portafolio 2', initial_value=1000000000)

    # Leer los datos del archivo Excel
    weights_df = pd.read_excel(file_path, sheet_name='weights')
    prices_df = pd.read_excel(file_path, sheet_name='Precios')

    # Poblar el modelo Asset
    for index, row in weights_df.iterrows():
        asset_name = row['activos']
        asset_description = '' 
        # Crear o obtener el activo
        asset, created = Asset.objects.get_or_create(name=asset_name, defaults={'description': asset_description})

        weight_portfolio1 = row['portafolio 1']
        weight_portfolio2 = row['portafolio 2']
        
        portfolio1 = Portfolio.objects.get(id=1)
        portfolio2 = Portfolio.objects.get(id=2)
        
        # Crear o actualizar los pesos
        Weight.objects.update_or_create(portfolio=portfolio1, asset=asset, defaults={'weight': weight_portfolio1})
        Weight.objects.update_or_create(portfolio=portfolio2, asset=asset, defaults={'weight': weight_portfolio2})

    # Poblar el modelo Price
    for index, row in prices_df.iterrows():
        date = row['Dates']
        for asset_name in prices_df.columns[1:]:  # Saltar la primera columna que es 'Dates'
            price_value = row[asset_name]
            # Crear o actualizar el precio
            asset = Asset.objects.get(name=asset_name)
            Price.objects.update_or_create(asset=asset, date=date, defaults={'value': price_value})

    # Calcular y cargar cantidades iniciales
    initial_date = pd.to_datetime('2022-02-15')
    initial_value = 1000000000

    for index, row in weights_df.iterrows():
        asset_name = row['activos']
        asset = Asset.objects.get(name=asset_name)
        
        # Obtener el precio inicial del activo
        initial_price = Price.objects.get(asset=asset, date=initial_date).value
        
        # Calcular y almacenar las cantidades para cada portafolio
        weight1 = row['portafolio 1']
        quantity1 = (initial_value * weight1) / float(initial_price)
        Quantity.objects.update_or_create(portfolio=portfolio1, asset=asset, defaults={'quantity': quantity1})
        
        weight2 = row['portafolio 2']
        quantity2 = (initial_value * weight2) / float(initial_price)
        Quantity.objects.update_or_create(portfolio=portfolio2, asset=asset, defaults={'quantity': quantity2})