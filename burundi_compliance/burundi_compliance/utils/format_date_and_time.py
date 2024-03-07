from datetime import datetime

def date_time_format(doc):

    formatted_date = f'{doc.posting_date} {doc.posting_time}'
    datetime_obj = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S.%f')

    formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    identity_date=datetime_obj.strftime('%Y%m%d%H%M%S')

    return formatted_date, identity_date
