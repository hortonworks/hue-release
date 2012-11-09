from django.contrib.sessions.backends.db import SessionStore as SessionStoreBase
from django.contrib.sessions.models import Session
from django.utils.encoding import force_unicode
from django.core.exceptions import SuspiciousOperation

import base64
import pickle
import datetime

class SessionStore(SessionStoreBase):
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

    def load(self):
        try:
            s = Session.objects.get(
                session_key = self.session_key,
                expire_date__gt=datetime.datetime.now()
            )
            return self.decode(force_unicode(s.session_data))
        except (Session.DoesNotExist, SuspiciousOperation):
            self.create()
            return {}

    def decode(self, session_data):
        encoded_data = base64.b64decode(session_data)
        try:
            return pickle.loads(encoded_data)
        except Exception:
            return {}
