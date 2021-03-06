from datetime import datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        try:
            return (obj - datetime(1970, 1, 1)).total_seconds() * 1000  # return unix timestamp in milliseconds
        except Exception as e:
            print (str(e))
    raise TypeError("Type not serializable")
