import datetime


def date_sql(input_date, sql_type='sqlite'):
    if sql_type=='MSSQL':
        return input_date
    x=input_date.split('-')
    if sql_type=='sqlite':
        return datetime.date(int(x[0]), int(x[1]), int(x[2]))
    else:
        return str(input_date)

def datetime_sql(input_datetime, sql_type='sqlite'):
    if sql_type=='MSSQL':
        return input_datetime
    x=input_datetime.split(" ")
    x_date=x[0].split('-')
    x_time=x[1].split(':')
    if sql_type=='sqlite':
        return datetime.datetime(int(x_date[0]), int(x_date[1]), int(x_date[2]), int(x_time[0]), int(x_time[1]), int(x_time[2]))
    else:
        return str(input_datetime)
        
def datetime_converter(input_datetime):
    if input_datetime is None:
        return ''
    else:
        input_datetime=input_datetime.strftime("%m-%d-%Y %H:%M:%S")
        mod='PM'
        date_string=input_datetime.split(' ')[0].strip()
        time_string=input_datetime.split(' ')[1].strip()
        year=date_string.split('-')[2]
        month=date_string.split('-')[0]
        day=date_string.split('-')[1]
        if int(time_string.split(':')[0]) == 0:
            hour = '12'
            mod='AM'
        elif int(time_string.split(':')[0]) < 12:
            hour = str(int(time_string.split(':')[0]))
            mod='AM'
        elif int(time_string.split(':')[0]) == 12:
            hour = '12'
        else:
            hour = str(int(time_string.split(':')[0])-12)
        minutes= str(time_string.split(':')[1])
        if int(time_string.split(':')[2])<10:
            seconds='0'+str(int(time_string.split(':')[2]))
        else:
            seconds= str(int(time_string.split(':')[2]))
        clean_datetime=''
        clean_datetime += month + '-' + day + '-' + year + '<br>' + hour + ':' + minutes + ':' + seconds + ' ' + mod
        return clean_datetime
        
def date_converter(input_date):
    if input_date is None:
        return ''
    else:
        input_date=str(input_date)
        year=input_date.split('-')[0]
        month=input_date.split('-')[1]
        day=input_date.split('-')[2]
        return month + '-' + day + '-' + year