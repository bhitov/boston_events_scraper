from datetime import datetime


def parse_soap_date(soap_date):
    data = {}
    for field in ['year', 'day', 'hour', 'minute', 'month']:
        data[field] = int(getattr(soap_date, field)[0])
    return datetime(**data)