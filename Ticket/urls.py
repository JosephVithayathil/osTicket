# Rest api urls file.
from rest_framework.routers import SimpleRouter
from .import api
# from .api_collection import virtual_operations



urlpatterns = [
]

router = SimpleRouter(trailing_slash=False)
router.register(r'get_ticket_details', api.GetTicketDetails, "GetTicketDetails"),
router.register(r'get_os_ticket_status',api.GetOsTicketStatus,"GetOsTicketStatus")
router.register(r'get_status_of_list_of_ticket_id',api.GetStatusOfListOfTicketId,"GetStatusOfListOfTicketId")
router.register(r'update_ticket',api.UpdateTicket,"UpdateTicket")
router.register(r'get_all_help_topic',api.GetAllHelpTopic,"GetAllHelpTopic")
router.register(r'get_all_details_of_help_topic',api.GetAllDetailsOfHelpTopic,"GetAllDetailsOfHelpTopic")

urlpatterns += router.urls
