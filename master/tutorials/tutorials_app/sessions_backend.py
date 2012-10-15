from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore as SessionStoreBase
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError, transaction, router
from django.utils.encoding import force_unicode 
import base64, pickle

class SessionStore(SessionStoreBase):
    """
    Implements database session store without expire_date checking
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

    def load(self):
        try:
            s = Session.objects.get(
                session_key = self.session_key,
#                expire_date__gt=datetime.datetime.now()
            )
            d = self.decode(force_unicode(s.session_data))
            return d
        except (Session.DoesNotExist, SuspiciousOperation):
            self.create()
            return {}

    def decode(self, session_data):
        encoded_data = base64.b64decode(session_data)
        try:
            return pickle.loads(encoded_data)
        except Exception:
            # ValueError, SuspiciousOperation, unpickling exceptions. If any of
            # these happen, just return an empty dictionary (an empty session).
            return {}
