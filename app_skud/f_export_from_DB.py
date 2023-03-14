import csv

from datetime import datetime

from django.http import HttpResponse
from django.db.models import QuerySet


def import_data_from_database(request, data: QuerySet):
    date_time = datetime.now().strftime("%d/%m/%y %I/%M/%S")
    column = [
        'operation_type',
        'time_created',
        'card',
        'staff',
        'controller',
        'checkpoint',
        'granted',
        'event',
        'flag',
        'data_monitor_events',
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=Data {date_time}.csv'

    writer = csv.writer(response)
    writer.writerow(column)
    
    for i in data:
        writer.writerow(
            [
            i.operation_type,
            i.time_created,
            i.card,
            i.staff,
            i.controller,
            i.checkpoint,
            i.granted,
            i.event,
            i.flag,
            i.data_monitor_events,
            ]
        )

    return response
