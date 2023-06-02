import csv

from datetime import datetime

from django.http import HttpResponse
from django.db.models import QuerySet


def import_data_from_database(request, data: QuerySet):
    date_time = datetime.now().strftime("%d/%m/%y %I/%M/%S")
    column = [
        'ФИО',
        'ДЕПАРТАМЕНТ',
        'ДАТА/ВРЕМЯ',
        'ПРОХОДНАЯ',
        'ВХОД',
        'ВЫХОД',
        'СОБЫТИЕ',
        'КАРТА',
        'ТИП АУТЕТИФИКАЦИЯ',
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=Data {date_time}.csv'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(column)
    
    for i in data:
        dt = i.time_created.strftime("%d/%m/%y %I:%M:%S")
        writer.writerow(
            [
            i.staff,
            i.data_monitor_events['dep'],
            dt,
            i.checkpoint,
            dt if i.data_monitor_events['direct'] == 'Вход' else '',
            dt if i.data_monitor_events['direct'] == 'Выход' else '',
            'Доступ разрешен' if i.data_monitor_events['granted'] == 1 else 'Доступ запрешен',
            str(i.card),
            'Двуфакторная' if i.operation_type != 'events' else 'Однофакторная'
            ]
        )

    return response
