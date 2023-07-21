import xlsxwriter

from datetime import datetime, date

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
        worksheet.write(row, col+9, el.data_monitor_events['late_status'])

        row += 1

    worksheet.autofilter(f'A1:I{row}')
    workbook.close()
    
    return response


def import_tabel_from_database(request, data):
    for el in data:
        # записать фио
        try:
            # получаем сотрудника и его профиль доступа по времени
            # {'friday': ['00:00:01', '23:59:59'], 'monday': ['18:00:00', '20:00:00'], 'sunday': ['00:00:01', '23:59:59'], 'tuesday': ['10:00:00', '22:00:00'], 'saturday': ['00:00:01', '23:59:59'], 'thursday': ['11:30:00', '15:00:00'], 'wednesday': ['15:00:00', '19:00:00']}
            name_staff, last_name_staff, patronymic_staff = el.split(' ')
            staff = Staffs.objects.get(last_name=name_staff, first_name=last_name_staff, patronymic=patronymic_staff)
            time_profile_staff = staff.time_profale
            event_list_staff = data[el]
            # print(f'staff ----->>>>> {staff}')
            # print(f'time_profile_staff ----->>>>> {time_profile_staff}')
            # print(f'time_profile_staff.time_profile_data ----->>>>> {time_profile_staff.time_profile_data}')
        except Exception as e:
                print(f'--- e ---------->>> {e}')

        event_date = {}
        # получаем события сотрудника по дням, ключ - день, значение - список событий
        # event_date ----->>>> {'Wednesday': [<MonitorEvents: TEST_NAME TEST_SECOND_NAME >, <MonitorEvents: TEST_NAME TEST_SECOND_NAME >, <MonitorEvents: TEST_NAME TEST_SECOND_NAME >, <MonitorEvents: TEST_NAME TEST_SECOND_NAME >, <MonitorEvents: TEST_NAME TEST_SECOND_NAME >]}
        for i, v in enumerate(event_list_staff):
            key, *_ = v
            value = event_list_staff[i][key]
            key = key.date().strftime('%A')
            if key not in event_date:
                event_date.setdefault(key, [value,])
            else:
                event_date[key].append(value)
        
        
        for el in event_date:
            print(f'='*88)
            event_list_by_day = event_date[el] # события одного дня одного сотрудника
            print(f'event_list_by_day --->>> {event_list_by_day}')
            # нужно взять 1 событие дня и поледнее
            # у этих событий определить направление и время
            
            event_first_by_day = event_list_by_day[0]
            direct_event_first_by_day = event_first_by_day.data_monitor_events["direct"]
            time_event_first_by_day = event_first_by_day.time_created
            print(f'event_first_by_day --->>> {event_first_by_day}')
            print(f'direct_event_first_by_day --->>> {direct_event_first_by_day}')
            print(f'time_event_first_by_day --->>> {time_event_first_by_day} === {type(time_event_first_by_day)}')

            
            event_last_by_day = event_list_by_day[-1]
            direct_event_last_by_day = event_last_by_day.data_monitor_events["direct"]
            time_event_last_by_day = event_last_by_day.time_created
            print(f'event_last_by_day --->>> {event_last_by_day}')
            print(f'direct_event_last_by_day --->>> {direct_event_last_by_day}')
            print(f'time_event_last_by_day --->>> {time_event_last_by_day} === {type(time_event_last_by_day)}')

            
            # нужно достать профиль дня и его часы для оценки
            day_now = time_profile_staff.time_profile_data[el.lower()]
            begin_day_by_time_profile = day_now[0]
            end_day_by_time_profile = day_now[1]
            print(f'day_now --->>> {day_now}')
            print(f'begin_day_by_time_profile --->>> {begin_day_by_time_profile}')
            print(f'end_day_by_time_profile --->>> {end_day_by_time_profile}')

            # if direct_event_first_by_day == 'Вход' and 
            # time_of_the_working_day = 

            print(f'='*88)
            print(' ')




            # for el in event_list_by_day:
            #     print('='*88)
            #     print(f'el ----->>>>> {el}')
            #     print(f'el.staff ---->>>> {el.staff}')
            #     print(f'el.time_created ---->>>> {el.time_created}')
            #     print(f'el.data_monitor_events ---->>>> {el.data_monitor_events["direct"]}')
            #     print('='*88)


        


