from datetime import datetime, timedelta


from datetime import datetime

def date_time_format(doc):
    if doc.doctype == 'Sales Invoice':
        formatted_date = f'{doc.posting_date} {doc.posting_time}'
    else:
        formatted_date = f'{doc.posting_date} {get_now_time()}'
    
    # Check if microseconds are present in the formatted_date
    if '.' in formatted_date:
        format_str = '%Y-%m-%d %H:%M:%S.%f'
    else:
        format_str = '%Y-%m-%d %H:%M:%S'

    datetime_obj = datetime.strptime(formatted_date, format_str)
    formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    identity_date = datetime_obj.strftime('%Y%m%d%H%M%S')
    return formatted_date, identity_date


def date_time_format_on_cancel(doc):
    formatted_date = f'{doc.posting_date} {get_now_time()}'
    datetime_obj = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S.%f')

    # Add 1 second to the datetime object
    datetime_obj += timedelta(seconds=2)

    formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    identity_date = datetime_obj.strftime('%Y%m%d%H%M%S')

    return formatted_date, identity_date

def get_now_time():
    currentDT = datetime.now()
    current_time = currentDT.strftime("%H:%M:%S")
    return current_time
