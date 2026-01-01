from app.crud import CrudBase
from app.models import StreamAnalytics


# ---------- Analytics ----------
class StreamAnalyticsCrud(CrudBase[StreamAnalytics]):
    def __init__(self):
        super().__init__(StreamAnalytics)

analytics_crud = StreamAnalyticsCrud()
