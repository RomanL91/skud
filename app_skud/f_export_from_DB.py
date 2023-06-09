import xlsxwriter

from datetime import datetime

from django.http import HttpResponse
from django.db.models import QuerySet


def import_data_from_database(request, data: QuerySet):
    date_time = datetime.now().strftime("%d/%m/%y %I/%M/%S")

    response = HttpResponse(content_type='text/xlsx')
    response['Content-Disposition'] = f'attachment; filename=Data {date_time}.xlsx'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:I', 20)

    bold = workbook.add_format({'bold': False})

    worksheet.write('A1','ФИО', bold)
    worksheet.write('B1','ДЕПАРТАМЕНТ', bold)
    worksheet.write('C1','ДАТА/ВРЕМЯ', bold)
    worksheet.write('D1','ПРОХОДНАЯ', bold)
    worksheet.write('E1','ВХОД', bold)
    worksheet.write('F1','ВЫХОД', bold)
    worksheet.write('G1','СОБЫТИЕ', bold)
    worksheet.write('H1','КАРТА', bold)
    worksheet.write('I1','ТИП АУТЕТИФИКАЦИЯ', bold)

    row = 1
    col = 0

    for el in data:
        dt = el.time_created.strftime("%d/%m/%y %H:%M:%S")
        try:
            direct = el.data_monitor_events['direct']
        except:
            direct = ' --- '
        worksheet.write(row, col, el.staff)
        worksheet.write(row, col+1, el.data_monitor_events['dep'])
        worksheet.write(row, col+2, dt)
        worksheet.write(row, col+3, str(el.checkpoint))
        worksheet.write(row, col+4, dt if direct == 'Вход' else '')
        worksheet.write(row, col+5, dt if direct == 'Выход' else '')
        worksheet.write(row, col+6, 'Доступ разрешен' if el.data_monitor_events['granted'] == 1 else 'Доступ запрешен')
        worksheet.write(row, col+7, str(el.card))
        worksheet.write(row, col+8, 'Двуфакторная' if el.operation_type != 'events' else 'Однофакторная')

        row += 1

    worksheet.autofilter(f'A1:I{row}')
    workbook.close()
    
    return response
