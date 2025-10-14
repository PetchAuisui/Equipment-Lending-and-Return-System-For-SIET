from app.services.admin_return_service import AdminReturnService

class AdminReturnController:
    """Controller สำหรับเชื่อม Blueprint กับ Service"""

    @staticmethod
    def get_all_returns():
        service = AdminReturnService()
        return service.list_pending_returns()

    @staticmethod
    def confirm_return(rent_id):
        service = AdminReturnService()
        return service.confirm_return(rent_id)
