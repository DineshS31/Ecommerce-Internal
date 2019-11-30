from app.models.user import UserEntries


def is_user_exist(payload):
    user_tbl = UserEntries()
    if user_tbl.retrieve_user_using_email(payload['email']):
        return True
    else:
        return False
