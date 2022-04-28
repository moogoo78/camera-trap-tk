from datetime import datetime
#from bson.objectid import ObjectId

def validate_datetime(datetime_text, datetime_format=''):
    try:
        if datetime_text != datetime.strptime(datetime_text, datetime_format).strftime(datetime_format):
            raise ValueError
        return True
    except ValueError:
        return False
