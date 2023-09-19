import xlsxwriter

from datetime import datetime

from django.http import HttpResponse
from django.db.models import QuerySet

from app_skud.models import Staffs


def import_data_from_database(request, data: QuerySet):
    date_time = datetime.now().strftime("%d/%m/%y %I/%M/%S")

    response = HttpResponse(content_type='text/xlsx')
    response['Content-Disposition'] = f'attachment; filename=Data {date_time}.xlsx'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:J', 20)

    bold = workbook.add_format({'bold': False})

    worksheet.write('A1','ФИО', bold)
    worksheet.write('B1','ДЕПАРТАМЕНТ', bold)
    worksheet.write('C1','ДАТА', bold)
    worksheet.write('D1','ПРОХОДНАЯ', bold)
    worksheet.write('E1','ВХОД', bold)
    worksheet.write('F1','ВЫХОД', bold)
    worksheet.write('G1','СОБЫТИЕ', bold)
    worksheet.write('H1','КАРТА', bold)
    worksheet.write('I1','ТИП АУТЕТИФИКАЦИЯ', bold)
    worksheet.write('J1','РЕЖИМ РАБ ВРЕМЕНИ', bold)

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
        worksheet.write(row, col+2, dt.split(' ')[0])
        worksheet.write(row, col+3, str(el.checkpoint))
        worksheet.write(row, col+4, dt if direct == 'Вход' else '')
        worksheet.write(row, col+5, dt if direct == 'Выход' else '')
        worksheet.write(row, col+6, 'Доступ разрешен' if el.data_monitor_events['granted'] == 1 else 'Доступ запрешен')
        worksheet.write(row, col+7, str(el.card))
        worksheet.write(row, col+8, 'Двуфакторная' if el.operation_type != 'events' else 'Однофакторная')
        try:
            worksheet.write(row, col+9, el.data_monitor_events['late_status'])
        except:
            worksheet.write(row, col+9, ' --- ')

        row += 1

    worksheet.autofilter(f'A1:J{row}')
    workbook.close()
    
    return response


def import_tabel_from_database(request, data):
    name_file = datetime.now().strftime("%d/%m/%y %I/%M/%S")
    response = HttpResponse(content_type='text/xlsx')
    response['Content-Disposition'] = f'attachment; filename=TABEL {name_file}.xlsx'

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:E', 25)

    bold = workbook.add_format({'bold': False})

    worksheet.write('A1','ДАТА', bold)
    worksheet.write('B1','ФИО', bold)
    worksheet.write('C1','НАЧАЛО РАБ-ГО ДНЯ', bold)
    worksheet.write('D1','КОНЕЦ РАБ-ГО ДНЯ', bold)
    worksheet.write('E1','ОТРАБОТАНО', bold)

    row = 1
    col = 0

    for el in data:
        try:
            name_staff, last_name_staff, patronymic_staff = el.split(' ')
            staff = Staffs.objects.get(last_name=name_staff, first_name=last_name_staff, patronymic=patronymic_staff)
            time_profile_staff = staff.time_profale
            event_list_staff = data[el]
        except Exception as e:
                print(f'--- e ---------->>> {e}')

        event_date = {}
        for i, v in enumerate(event_list_staff):
            key, *_ = v
            value = event_list_staff[i][key]
            key = key.date().strftime('%A')
            if key not in event_date:
                event_date.setdefault(key, [value,])
            else:
                event_date[key].append(value)
        
        for el in event_date:
            event_list_by_day = event_date[el] # события одного дня одного сотрудника
            date_day = event_list_by_day[0].time_created.date()
            
            event_first_by_day = event_list_by_day[0]
            direct_event_first_by_day = event_first_by_day.data_monitor_events["direct"]
            time_event_first_by_day = event_first_by_day.time_created.time()
            
            event_last_by_day = event_list_by_day[-1]
            direct_event_last_by_day = event_last_by_day.data_monitor_events["direct"]
            time_event_last_by_day = event_last_by_day.time_created.time()
            
            if time_profile_staff is None:
                begin_day_by_time_profile = 'нет временного профиля'
                end_day_by_time_profile = 'нет временного профиля'
            else:
                day_now = time_profile_staff.time_profile_data[el.lower()]
                begin_day_by_time_profile = day_now[0]
                end_day_by_time_profile = day_now[1]
            
            if direct_event_first_by_day == 'Вход':
                if str(time_event_first_by_day) < begin_day_by_time_profile:
                    time_of_the_working_day = begin_day_by_time_profile
                else:
                    time_of_the_working_day = str(time_event_first_by_day)
            else:
                time_of_the_working_day = None
                error_flag = 0

            if direct_event_last_by_day == 'Выход':
                if str(time_event_last_by_day) > end_day_by_time_profile:
                    time_end_of_working_day = end_day_by_time_profile
                else:
                    time_end_of_working_day = str(time_event_last_by_day)
            else:
                time_end_of_working_day = None
                error_flag = 1

            try:
                actual_time_at_work = datetime.strptime(time_end_of_working_day, "%H:%M:%S") - datetime.strptime(time_of_the_working_day, "%H:%M:%S")
            except:
                if error_flag == 1:
                    actual_time_at_work = f'был на работе с {time_event_first_by_day}. Время ухода не известно.'
                elif error_flag == 0:
                    actual_time_at_work = f'был на работе до {time_end_of_working_day}. Время входа не известно.'

            try:
                if actual_time_at_work.days < 0:
                    actual_time_at_work = f'Отсутствовал на работе в рабочие часы'
            except:
                pass
            
            worksheet.write(row, col, str(date_day))
            worksheet.write(row, col+1, str(staff))
            worksheet.write(row, col+2, begin_day_by_time_profile)
            worksheet.write(row, col+3, end_day_by_time_profile)
            worksheet.write(row, col+4, str(actual_time_at_work))

            row += 1

    worksheet.autofilter(f'A1:E{row}')
    workbook.close()

    return response
