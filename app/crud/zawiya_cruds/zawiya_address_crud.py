from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaAddress

class ZawiyaAddressCrud(CrudBase[ZawiyaAddress]):
    """ Zawiya Address Crud Management """
    def __init__(self):
        super().__init__(ZawiyaAddress)

zawiya_address_crud = ZawiyaAddressCrud()
