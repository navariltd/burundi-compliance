from datetime import datetime, timedelta

def date_time_format(doc):

    formatted_date = f'{doc.posting_date} {doc.posting_time}'
    datetime_obj = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S.%f')

    formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    identity_date=datetime_obj.strftime('%Y%m%d%H%M%S')

    return formatted_date, identity_date

# def date_time_format(doc):
#     # Convert timedelta to hours, minutes, and seconds
#     hours = doc.posting_time.seconds // 3600
#     minutes = (doc.posting_time.seconds % 3600) // 60
#     seconds = doc.posting_time.seconds % 60

#     # Format time components with leading zeros if necessary
#     formatted_time = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

#     # Concatenate posting_date and formatted_time
#     formatted_date = f'{doc.posting_date} {formatted_time}'

#     # Parse formatted_date
#     datetime_obj = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')

#     # Format datetime_obj
#     formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
#     identity_date = datetime_obj.strftime('%Y%m%d%H%M%S')

#     return formatted_date, identity_date


def date_time_format_on_cancel(doc):
    formatted_date = f'{doc.posting_date} {doc.posting_time}'
    datetime_obj = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S.%f')

    # Add 1 second to the datetime object
    datetime_obj += timedelta(seconds=1)

    formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    identity_date = datetime_obj.strftime('%Y%m%d%H%M%S')

    return formatted_date, identity_date
