from django.core.management.base import BaseCommand
from portfolio.etl import load_data_from_excel

class Command(BaseCommand):
    help = 'Carga datos desde el archivo Excel'

    def handle(self, *args, **kwargs):
        file_path = '/app/portfolio/data/datos.xlsx'
        load_data_from_excel(file_path)
        self.stdout.write(self.style.SUCCESS('Datos cargados exitosamente.'))
