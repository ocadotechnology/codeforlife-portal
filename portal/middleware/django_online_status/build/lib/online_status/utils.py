from online_status.status import OnlineStatus

def encode_json(obj):
    if isinstance(obj, OnlineStatus):
        seen = obj.seen.isoformat()
        user = {'username': obj.user.username, 'first_name': obj.user.first_name, 'last_name': obj.user.last_name,}  
        return {'user': user, 'seen': seen, 'status': obj.status,}
    else:
        raise TypeError(repr(obj) + " is not JSON serializable")
