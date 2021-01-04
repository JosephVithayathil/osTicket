# Rest apis file.
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework import viewsets, permissions
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import ldap
import json
import datetime
from .ldap_server_connection import get_ldap_connection
from .status_codes import StatusCode
from .models import StakeHolder, PermissionGroups, TrackingStatus,\
    ResourcesRequired, DeletedUsers, PriorityLevels, FeedBack, BroadcastMessage, \
    BroadcastMessageRecivers, ScreenStatistics, Referals, Tweet, RMSCategories, RMSRequest, WorkMeal, \
    StakeHolderRMSGroups, SkillData, Skills, DashBoardScreens, ModuleLeaders, ModuleTypeEnum, \
    LeaderModuleChangeHistory, LeaderManagerChangeHistory, LeaveBalanceHistory
from ideabox.models import IdeaBoxModel
from .smcc_enums import Designations, RMSRequestStatus, MealTime, MealTypes
from .permission_handler import PermissionHandler
from django.core.files.storage import FileSystemStorage
from .mail import Mail
import os
from .api_collection.notifications import NotificationManager, NotificationCategory

DEFAULT_PASSWORD = "@changepassword"

class TrackApis(object):
    """Track apis."""

    def track_screen(self, stakeholder, screen_enum, stakeholder_type="stakeholder"):
        try:
            if stakeholder_type != "stakeholder":
                stakeholder=StakeHolder.objects.get(user=stakeholder)
            today = datetime.date.today()
            try:
                screen_stat = ScreenStatistics.objects.get(
                    stakeholder=stakeholder, date__date=today, page_enum=screen_enum
                )
            except ScreenStatistics.MultipleObjectsReturned:
                ScreenStatistics.objects.filter(
                    stakeholder=stakeholder, date__date=today, page_enum=screen_enum
                ).delete()
                screen_stat = ScreenStatistics.objects.create(
                    stakeholder=stakeholder,page_enum=screen_enum
                )
            except ScreenStatistics.DoesNotExist:
                screen_stat = ScreenStatistics.objects.create(
                    stakeholder=stakeholder,page_enum=screen_enum
                )
            screen_stat.count = screen_stat.count + 1
            screen_stat.save()
        except Exception as e:
            print("ESC = ", e)
            pass


@permission_classes((permissions.AllowAny,))
class TrakScreenApi(viewsets.ViewSet):
    """Api to track api api."""

    def create(self, request):
        track_obj = TrackApis()
        request_data = request.data
        stakeholder=StakeHolder.objects.get(user=request.user)
        track_obj.track_screen(stakeholder, request_data["sc_enm"])
        return Response({"st": StatusCode.OK})

@permission_classes((permissions.AllowAny,))
class TestApis(viewsets.ViewSet):
    """Test api."""

    def list(self, request):
        """Creating an organisation."""
        print("request data", request.data)
        
        mail = Mail()
        mail.send({"recipients": "joseph.vithayathil@nslhub.com", "content": "TEST <h1>CONENT</h1> ....", "subject":" Testingg the new function."})
        return Response({"st": StatusCode.OK})

    def create(self, request):
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.AllowAny,))
class LoginApi(viewsets.ViewSet):
    """Login API."""

    def create(self, request):
        """Post method."""
        username = request.data["u_n"]
        if username.endswith("@nslhub.com"):
            username = username[:-11]
        print("USER NAME = ", username)
        password = request.data["pwd"]
        user = None
        if not request.data["google_login"]:
            user = authenticate(username=username, password=password)
        else:
            
            from google.oauth2 import id_token
            from google.auth.transport import requests

            # (Receive token by HTTPS POST)
            # ...

            try:
                token = password
                CLIENT_ID = "288022822413-c3a9hmkbmvq2lnfm379iv5rrknic9jie.apps.googleusercontent.com"
                # Specify the CLIENT_ID of the app that accesses the backend:
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
                print("INFO ===========", idinfo)
                # Or, if multiple clients access the backend server:
                # idinfo = id_token.verify_oauth2_token(token, requests.Request())
                # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
                #     raise ValueError('Could not verify audience.')

                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')

                # If auth request is from a G Suite domain:
                # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
                #     raise ValueError('Wrong hosted domain.')
                username = idinfo["email"][:-11]
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return Response({"st": StatusCode.STAKEHOLDER_NOT_IN_DATABASE})

                # ID token is valid. Get the user's Google Account ID from the decoded token.
                userid = idinfo['sub']
            except ValueError:
                # Invalid token
                print("ERRROR ===================================")
                pass
        if user is None:
            return Response({"st": StatusCode.INVALID_CREDENTIALS})
            # con = get_ldap_connection()
            # base_dn = "dc=nslhub,dc=com"
            # search_filter = "uid="+username
            # try:
            #     # result = con.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, None)
            #     # user_dn = result[0][0]
            #     # print("USERE DN = ", user_dn)
            #     user_dn = "uid="+username+",ou=Users,dc=nslhub,dc=com"
            #     con.simple_bind_s(user_dn, password)
            # except ldap.INVALID_CREDENTIALS:
            #     con.unbind()
            #     return Response({"st": StatusCode.INVALID_CREDENTIALS})
            # except ldap.SERVER_DOWN:
            #     return Response({"st": StatusCode.AUTHENTICATION_SERVER_NOT_AVAILABLE})
            # except ldap.INSUFFICIENT_ACCESS:
            #     return Response({"st": StatusCode.STAKEHOLDER_NOT_IN_DATABASE})
            # # except IndexError:
            # #     return Response({"st": "OK", "dt": 'Username not found'})
            # con.unbind()
        try:
            stakeholder = StakeHolder.objects.get(user__username=username)
        except StakeHolder.DoesNotExist:
            return Response({"st": StatusCode.STAKEHOLDER_NOT_IN_DATABASE})
        try:
            token_key = Token.objects.get(user=stakeholder.user).key
        except Exception as exp:
            token_key = Token.objects.create(user=stakeholder.user).key
            # print("EXPECPITOMN = ", exp)
            # return Response({"st": "ErrorCode.AUTH_FAILED"})
        response_data = {}
        response_data["st"] = StatusCode.OK
        response_data["dt"] = GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(stakeholder)
        response_data["dt"]["scrt_key"] = token_key
        # user_grps_data = []
        # for user_grp in stakeholder.permission_grp.all():
        #     user_grps_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
        # user_grp = PermissionGroups.objects.get(name="StakeHolder")
        # user_grps_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
        # response_data["dt"]["user_grps"] = user_grps_data
        response_data["dt"]["first_time"] = True if password == DEFAULT_PASSWORD else False
        # print("ASDFASDF=", response_data["dt"]["first_time"])
        return Response(response_data)


@permission_classes((permissions.IsAuthenticated,))
class LogoutApi(viewsets.ViewSet):
    """Test api."""

    def create(self, request):
        """Creating an organisation."""
        print("request data", request.data)
        user = request.user
        self.logout(user)
        return Response({"st": StatusCode.OK})
    
    @staticmethod
    def logout(user):
        Token.objects.filter(user=user).delete()


@permission_classes((permissions.IsAuthenticated,))
class CreateStakeholder(viewsets.ViewSet):
    """Create new stakeholder api."""

    def create(self, request):
        """Creating a new stakeholder."""
        email = request.data["email"]
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        emp_id = request.data["emp_id"]
        leaves_credited = request.data["leaves_credited"]
        leaves_credited_on = request.data["leaves_credited_on"]
        leaves_credited_on = datetime.datetime.strptime(leaves_credited_on, '%Y-%m-%d')
        leaves_credited_datetime = datetime.datetime.combine(leaves_credited_on, datetime.datetime.min.time())
        leaves_credited_datetime = leaves_credited_datetime + datetime.timedelta(hours=8)
        doj = request.data["doj"]
        print(leaves_credited, leaves_credited_on, leaves_credited_datetime)
        # return Response({"st": StatusCode.ERROR, "dt": "User name already exists"})
        if email.endswith("@nslhub.com"):
            username = email[:-11]
        else:
            return Response({"st": StatusCode.ERROR, "dt": "Email not ending with nslhub.com"})
        stakeholder = LDAPSyncUsers.create_users(username, email, first_name, last_name, emp_id)
        if stakeholder is None:
            return Response({"st": StatusCode.ERROR, "dt": "User name already exists"})
        stakeholder.extra_data["doj"] = doj
        UpdateStakeHolderOfficialData.update_doj(stakeholder)
        stakeholder.save()
        from .api_collection.leave_management import CreateLeaveRecord
        CreateLeaveRecord.credit_leave(stakeholder, leaves_credited, "MONTHLY LEAVE ADDITION", leaves_credited_datetime)
        data = GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(stakeholder)
        print("STAKE ATA = ", data)
        return Response({"st": StatusCode.OK, "dt": data})

@permission_classes((permissions.AllowAny,))
class LDAPSyncUsers(viewsets.ViewSet):
    """SyncUsers API."""

    def create(self, request):
        """Post method."""
        con = get_ldap_connection()
        base_dn = "dc=nslhub,dc=com"
        try:
            res = con.search_s(base_dn, ldap.SCOPE_SUBTREE, '(objectClass=person)')
            print("RESPONSE = ", res)
            for dn, entry in res:
                username, email, first_name, last_name = str(entry["uid"][0].decode("utf-8")), str(entry["mail"][0].decode("utf-8")), str(entry["givenName"][0].decode("utf-8")), str(entry["sn"][0].decode("utf-8"))
                print("GO =========", username, email, first_name, last_name)
                LDAPSyncUsers.create_users(username, email, first_name, last_name)
        except User.DoesNotExist:
            pass
        return Response({"st": StatusCode.OK})
    
    @staticmethod
    def create_users(username, email, first_name, last_name, emp_id):
        username = username.lower()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=DEFAULT_PASSWORD
                )
            stakeholder = StakeHolder.objects.create(user=user, employee_id=emp_id)
            return stakeholder



@permission_classes((permissions.IsAuthenticated,))
class GetAllStakeHolders(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        """Post method."""
        detailed = request.data.get("detailed", False)
        filters = request.data.get("filters", {})
        fields = request.data.get("fieldList", ["all"])
        select_related_fields = ["user"]
        if "manager" in fields or "all" in fields:
            select_related_fields += ['manager', 'manager__user']

        stakeholders = StakeHolder.objects.filter(**filters).select_related(*select_related_fields).order_by("employee_id")
        stakeholders_dt = []
        for stakeholder in stakeholders:
            if detailed:
                info = GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(stakeholder, fields)
            else:
                info = GetStakeHolderDetailedInfo.get_stakeholder_basic_info(stakeholder)
                # {
                #     "id": stakeholder.id,
                #     "username": stakeholder.user.username
                # }
            stakeholders_dt.append(info)
        return Response({"st": StatusCode.OK, "dt": stakeholders_dt})




@permission_classes((permissions.IsAuthenticated,))
class GetStakeHolderDetailedInfo(viewsets.ViewSet):
    """Get all details of stakeholder API."""

    def create(self, request):
        """Post method."""
        stakeholder_id = request.data["id"]
        stakeholder = StakeHolder.objects.get(id=stakeholder_id)
        return Response({"st": StatusCode.OK, "dt": self.get_stakeholder_detailed_info(stakeholder)})
    
    @staticmethod
    def get_stakeholder_detailed_info(stakeholder, fields=["all"]):
        if "all" in fields:
            fields = ["basic", "skills", "modules", "module_change_history", "manager", "user_grps", "leave_balance"]
        info = GetStakeHolderDetailedInfo.get_stakeholder_basic_info(stakeholder)
        if "basic" in fields:
            info.update({
                "entity_id": stakeholder.entity_id,
                "user_type": stakeholder.user_type,
                "designation": str(stakeholder.designation),
                "extra_data": stakeholder.extra_data,
                "role_id": stakeholder.role_id,
                "role_type_id": stakeholder.role_type_id
            })
        if "leave_balance" in fields:
            from .api_collection.leave_management import CreateLeaveRecord
            info.update(CreateLeaveRecord.get_leave_balance(stakeholder))
        if "skills" in fields:
            skills = []
            skills_dt = SkillData.objects.filter(stakeholder=stakeholder).select_related("skill").order_by("-proficiency")
            for skill in skills_dt:
                skills.append({
                    "name": skill.skill.name,
                    "proficiency": skill.proficiency,
                    "extra_data": skill.extra_data,
                    "skill_preference": skill.skill_preference
                })
            info["skills"] = skills
        if "modules" in fields:
            stack_list = []
            modules = ModuleLeaders.objects.filter(stakeholder=stakeholder, module__module_type__enum=ModuleTypeEnum.MODULE)
            module_dt = []
            module_leaders = []
            for module in modules:
                module_dt.append({
                    "id": module.module.id,
                    "name": module.module.name
                })
                module_leaders_objs = ModuleLeaders.objects.filter(module=module.module, leader=True)
                for module_leader in module_leaders_objs:
                    module_leaders.append(GetStakeHolderDetailedInfo.get_stakeholder_basic_info(module_leader.stakeholder)["full_name"])
                
                if module.module.parent_module.parent_module.name not in stack_list:
                    stack_list.append(module.module.parent_module.parent_module.name)
            grp_modules = ModuleLeaders.objects.filter(stakeholder=stakeholder, module__module_type__enum=ModuleTypeEnum.GROUP_MODULE)
            grp_module_dt = []
            grp_module_leaders = []
            for module in grp_modules:
                grp_module_dt.append({
                    "id": module.module.id,
                    "name": module.module.name
                })
                grp_module_leaders_objs = ModuleLeaders.objects.filter(module=module.module, leader=True)
                for grp_module_leader in grp_module_leaders_objs:
                    grp_module_leaders.append(GetStakeHolderDetailedInfo.get_stakeholder_basic_info(grp_module_leader.stakeholder)["full_name"])
                if module.module.parent_module.name not in stack_list:
                    stack_list.append(module.module.parent_module.name)
            
            work_modules = ModuleLeaders.objects.filter(stakeholder=stakeholder, module__module_type__enum=ModuleTypeEnum.WORK_MODULE)
            work_module_dt = []
            work_module_leaders = []
            for module in work_modules:
                work_module_dt.append({
                    "id": module.module.id,
                    "name": module.module.name
                })
            info.update({
                "modules": module_dt,
                "module_leaders": module_leaders,
                "grp_modules": grp_module_dt,
                "grp_module_leaders": grp_module_leaders,
                "work_modules": work_module_dt,
                "stacks": stack_list
            })
        if "module_change_history" in fields:
            info.update(GetStakeHolderDetailedInfo.get_change_history(stakeholder))
        if "manager" in fields:
            if stakeholder.manager is not None:
                info["manager"] = GetStakeHolderDetailedInfo.get_stakeholder_basic_info(stakeholder.manager)
            else:
                info["manager"] = {
                    "id": None,
                    "username": None,
                    "full_name": None
                }
        # user_grps_data = []
        # for user_grp in stakeholder.permission_grp.all().exclude(name="StakeHolder"):
        #     user_grps_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
        # user_grp = PermissionGroups.objects.get(name="StakeHolder")
        # user_grps_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
        if "user_grps" in fields:
            user_grps = PermissionHandler.get_user_permission_groups(stakeholder)
            user_grps_data = []
            for user_grp in user_grps:
                user_grps_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
            info["user_grps"] = user_grps_data
        return info
    
    # @staticmethod
    # def get_leave_balance(stakeholder):
    #     data = {}
    #     # time_stamp = datetime.datetime.now()
    #     # history = LeaveBalanceHistory.objects.filter(stakeholder=stakeholder, date_time__lte=time_stamp).order_by("date_time").last()
    #     # leave_balance = 0
    #     # if history is not None: 
    #     #     leave_balance = history.closinging_leave_balance
    #     history = LeaveBalanceHistory.objects.filter(stakeholder=stakeholder).order_by("date_time", "id").last()
    #     leave_balance = 0
    #     if history is not None: 
    #         leave_balance = history.closinging_leave_balance
    #     data["estimated_leave_balance"] = leave_balance
    #     data["leave_balance"] = leave_balance
    #     return data
    
    @staticmethod
    def get_stakeholder_basic_info(stakeholder):
        if stakeholder is None: return None
        middle_name = "" if stakeholder.extra_data.get("middle_name", None) is None else stakeholder.extra_data["middle_name"]
        return {
            "id": stakeholder.id,
            "username": stakeholder.user.username,
            "first_name": stakeholder.user.first_name,
            "middle_name":  middle_name,
            "last_name": stakeholder.user.last_name,
            "full_name": stakeholder.full_name,
            "email": stakeholder.user.email,
            "emp_id": stakeholder.employee_id,
            "profile_img": stakeholder.profile_img
        }
    
    @staticmethod
    def get_change_history(stakeholder):
        manager_change_history = LeaderManagerChangeHistory.objects.filter(stakeholder=stakeholder)
        response_dt={
            "manager_change_history": [],
            "module_change_history": [],
            "grp_module_change_history": []
        }
        for change in manager_change_history:
            info = {
                    "date": change.created_on
                }
            if change.old_manager is not None:
                info["old"]= GetStakeHolderDetailedInfo.get_stakeholder_basic_info(change.old_manager)["full_name"]
            if change.new_manager is not None:
                info["new"]= GetStakeHolderDetailedInfo.get_stakeholder_basic_info(change.new_manager)["full_name"]
            response_dt["manager_change_history"].append(info)

        module_change_history = LeaderModuleChangeHistory.objects.filter(stakeholder=stakeholder)
        for change in module_change_history:
            info = {
                    "date": change.created_on
                }
            work_module_flag = False
            if change.old_module is not None:
                info["old"]= change.old_module.name
                if change.old_module.module_type.enum == ModuleTypeEnum.GROUP_MODULE:
                    work_module_flag = True
            if change.new_module is not None:
                info["new"]= change.new_module.name
                if change.new_module.module_type.enum == ModuleTypeEnum.GROUP_MODULE:
                    work_module_flag = True
            if work_module_flag:
                response_dt["grp_module_change_history"].append(info)
            else:
                response_dt["module_change_history"].append(info)
        return response_dt


@permission_classes((permissions.IsAuthenticated,))
class UpdateStakeHolderOfficialData(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(id=request.data["id"])
        stakeholder.designation = request.data["designation"]
        print(request.data["manager"])
        if stakeholder.manager_id != request.data["manager"]["id"]:
            LeaderManagerChangeHistory.objects.create(old_manager=stakeholder.manager, 
                                                      new_manager_id=request.data["manager"]["id"], stakeholder=stakeholder)
            if request.data["manager"]["id"] is not None:
                stakeholder.manager = StakeHolder.objects.get(id=request.data["manager"]["id"])
            else:
                stakeholder.manager = None
        # LogoutApi.logout(stakeholder.user)
        print("SAVIGN GDATA")
        extra_data = request.data["extra_data"]
        stakeholder.user.first_name = request.data["first_name"]
        stakeholder.user.last_name = request.data["last_name"]
        stakeholder.profile_img = request.data["profile_img"]
        stakeholder.entity_id = request.data["entity_id"]
        stakeholder.user_type = request.data["user_type"]

        stakeholder.role_id = request.data["role_id"]
        stakeholder.role_type_id = request.data["role_type_id"]
        stakeholder.user.save()
        print(request.data["skills"])
        for skill_dt in request.data["skills"]:
            if skill_dt["name"].strip() != "":
                try:
                    skill = Skills.objects.get(name__iexact=skill_dt["name"])
                except Skills.DoesNotExist:
                    skill = Skills.objects.create(name=skill_dt["name"])
                skilldata = SkillData.objects.get_or_create(skill=skill, stakeholder=stakeholder)[0]
                skilldata.proficiency = skill_dt["proficiency"]
                skilldata.skill_preference = skill_dt["skill_preference"]
                skilldata.extra_data = skill_dt["extra_data"]
            skilldata.save()
        if "deleted_skills" in request.data:
            for deleted_skill in request.data["deleted_skills"]:
                deleted_skill_objs = SkillData.objects.filter(skill__name=deleted_skill["name"], stakeholder=stakeholder)
                deleted_skill_objs.delete()
        stakeholder.extra_data = extra_data
        self.update_doj(stakeholder)
        stakeholder.save()
        self.update_stakeholder_modules(stakeholder, request.data)
        response_data = GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(stakeholder)
        return Response({"st": StatusCode.OK, "dt": response_data})

    @staticmethod
    def update_doj(stakeholder):
        if stakeholder.extra_data["doj"] is not None:
            date_str = stakeholder.extra_data["doj"]
            try:
                doj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except:
                doj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
            stakeholder.date_of_joining = doj
            stakeholder.extra_data["doj"] = doj.strftime("%m/%d/%Y")
        else:
            stakeholder.date_of_joining = None
            stakeholder.extra_data["doj"] = None
    
    @staticmethod
    def update_stakeholder_modules(stakeholder, data):
        for module_stack_dict in [{"type": ModuleTypeEnum.GROUP_MODULE, "keyword": "grp_modules"}, 
                                  {"type": ModuleTypeEnum.MODULE, "keyword": "modules"},
                                  {"type": ModuleTypeEnum.WORK_MODULE, "keyword": "work_modules"}]:
            leader_grp_modules_id = list(ModuleLeaders.objects.filter(stakeholder=stakeholder, 
                                        module__module_type__enum=module_stack_dict["type"]).values_list('module_id', flat=True))
            for module_dict in data[module_stack_dict["keyword"]]:
                if module_dict["id"] not in leader_grp_modules_id:
                    ModuleLeaders.objects.get_or_create(stakeholder=stakeholder, module_id=module_dict["id"])
                    LeaderModuleChangeHistory.objects.create(new_module_id=module_dict["id"], stakeholder=stakeholder)
                else:
                    leader_grp_modules_id.remove(module_dict["id"])
            print(leader_grp_modules_id)
            for moduleleader_id in leader_grp_modules_id:
                ModuleLeaders.objects.get(stakeholder=stakeholder, module_id=moduleleader_id).delete()
                LeaderModuleChangeHistory.objects.create(old_module_id=module_dict["id"], stakeholder=stakeholder)

@permission_classes((permissions.IsAuthenticated,))
class UpdateStakeHolder_CV(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        """Post method."""
        user = request.user
        stakeholder = StakeHolder.objects.get(user=user)
        uploaded_file_url = None
        _file = request.data.get('cv', None)
        if _file is not None:
            fs = FileSystemStorage()
            filename = fs.save("stakeholder_cv/" + user.username.replace(" ", "_").replace(".", "") + ".pdf", _file)
            uploaded_file_url = fs.url(filename)
            print("URL = ", uploaded_file_url)
        stakeholder.cv = uploaded_file_url
        stakeholder.save()
        response_data = GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(stakeholder)
        return Response({"st": StatusCode.OK, "dt": response_data})


@permission_classes((permissions.IsAuthenticated,))
class GetAllUserGroups(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        response_data = []
        _filter = request.data.get("filter", {})
        print(request.data)
        user_grps = PermissionGroups.objects.filter(**_filter).order_by('id')
        for user_grp in user_grps:
            response_data.append(GetAllUserGroups.get_user_grp_data(user_grp))
        return Response({"st": StatusCode.OK, "dt": response_data})

    @staticmethod
    def get_user_grp_data(user_grp):
        return {
                "id": user_grp.id,
                "name": user_grp.name,
                "desc": user_grp.description,
                "permissions": user_grp.permissions,
                "parent_id": user_grp.parent_id
            }


@permission_classes((permissions.IsAuthenticated,))
class GetUserGroup(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        user_grp_id = request.data["id"]
        user_grp = PermissionGroups.objects.get(id=user_grp_id)
        response_data = GetAllUserGroups.get_user_grp_data(user_grp)
        return Response({"st": StatusCode.OK, "dt": response_data})


@permission_classes((permissions.IsAuthenticated,))
class CreateOrUpdateUserGroup(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        request_data = request.data
        user_grp_id = request_data.get("id", None)
        if user_grp_id is not None:
            user_grp = PermissionGroups.objects.get(id=user_grp_id)
        else:
            user_grp = PermissionGroups.objects.create(name=request_data["name"], description=request_data["desc"], permissions=[])
        user_grp.name = request_data["name"]
        user_grp.description = request_data["desc"]
        user_grp.permissions = request_data["permissions"]
        user_grp.parent_id = request_data.get("parent_id", None)
        user_grp.save()
        if user_grp.name == "StakeHolder":
            stakeholders = list(StakeHolder.objects.all())
        else:
            if user_grp.entity is None:
                stakeholders = StakeHolder.objects.filter(permission_grp=user_grp)
            else:
                stakeholders = StakeHolder.objects.filter(entity=user_grp.entity)

        for stakeholder in stakeholders:
            LogoutApi.logout(stakeholder.user)
        response_data = GetAllUserGroups.get_user_grp_data(user_grp)
        return Response({"st": StatusCode.OK, "dt": response_data})


@permission_classes((permissions.IsAuthenticated,))
class AddUserGroupUsers(viewsets.ViewSet):
    """Add users to usergroups API."""

    def create(self, request):
        request_data = request.data
        print("DATA = ", request_data)
        user_grp_id = request_data["id"]
        user_ids = request_data["user_ids"]
        for user_id in user_ids:
            try:
                StakeHolder.objects.get(id=user_id, permission_grp__id=user_grp_id)
            except StakeHolder.DoesNotExist:
                stakeholder = StakeHolder.objects.get(id=user_id)
                stakeholder.permission_grp.add(user_grp_id)
                stakeholder.save()
                LogoutApi.logout(stakeholder.user)
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class DeleteUserGroupUsers(viewsets.ViewSet):
    """Delete users to usergroups API."""

    def create(self, request):
        request_data = request.data
        print("DATA = ", request_data)
        user_grp_id = request_data["id"]
        user_id = request_data["user_id"]
        stakeholder = StakeHolder.objects.get(id=user_id)
        stakeholder.permission_grp.remove(user_grp_id)
        stakeholder.save()
        LogoutApi.logout(stakeholder.user)
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class DeleteStakeHolder(viewsets.ViewSet):
    """Delete users to usergroups API."""

    def create(self, request):
        request_data = request.data
        stakeholder = StakeHolder.objects.get(id=request_data["stakeholder_id"])
        LogoutApi.logout(stakeholder.user)
        DeletedUsers.objects.create(username=stakeholder.user.username)
        stakeholder.user.delete()
        stakeholder.delete()
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class ChangePassword(viewsets.ViewSet):
    """Reset password API."""

    def create(self, request):
        user = request.user
        user.set_password(request.data["new_password"])
        user.save()
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class ResetPassword(viewsets.ViewSet):
    """Reset password API."""

    def create(self, request):
        import random
        import string
        lettersAndDigits = string.ascii_letters + string.digits
        new_password =  ''.join(random.choice(lettersAndDigits) for i in range(16))
        stakeholder = StakeHolder.objects.get(id=request.data["stakeholder_id"])
        stakeholder.user.set_password(new_password)
        stakeholder.user.save()
        return Response({"st": StatusCode.OK, "dt": {"new_password": new_password}})


@permission_classes((permissions.IsAuthenticated,))
class GetResourcesRequiredData(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        req_id = request.data.get("id", None)
        print("DATA = ",request.data)
        if req_id is not None:
            res_req = ResourcesRequired.objects.get(id=req_id)
            response_data = GetResourcesRequiredData.get_resource_required_data(res_req)
        else:
            if request.data.get("filter", None) is not None:
                res_reqs = ResourcesRequired.objects.filter(**request.data["filter"]).order_by('-created_on')
            else:
                res_reqs = ResourcesRequired.objects.all().order_by('-created_on')
            response_data = []
            for res_req in res_reqs:
                response_data.append(GetResourcesRequiredData.get_resource_required_data(res_req))
        # print("DATA = ", response_data)
        return Response({"st": StatusCode.OK, "dt": response_data})

    @staticmethod
    def get_resource_required_data(res_req):
        if res_req is None:
            return {}
        response = {}
        response["id"] = res_req.id
        response["position"] = res_req.position
        response["job_description"] = res_req.job_description
        response["created_by"] = GetStakeHolderDetailedInfo.get_stakeholder_basic_info(res_req.created_by)
        response["fullfilled_by"] = res_req.fullfilled_by
        response["closed"] = res_req.closed
        response["created_on"] = res_req.created_on
        response["closing_description"] = res_req.closing_description
        response["job_description_pdf"] = res_req.job_description_pdf
        response["count"] = res_req.count
        return response

@permission_classes((permissions.IsAuthenticated,))
class CreateUpdateResourcesRequired(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        # request_data = request.data
        job_desc = request.data.get('job_desc', None)
        job_description_pdf = None
        
        if "dt" in request.data:
            request_data = json.loads(request.data["dt"])
        else:
            request_data = request.data
        req_id = request_data.get("id", None)
        closing = request_data.get("closing", False)
        stakeholder = StakeHolder.objects.get(user=request.user)
        if not closing:
            if req_id is None:
                res_req = ResourcesRequired.objects.create(position=request_data["position"])
            else:
                res_req = ResourcesRequired.objects.get(id=request_data["id"])
            if job_desc is not None:
                fs = FileSystemStorage()
                filename = fs.save("job_description/" + res_req.position.replace(" ", "_").replace(".", "").replace("-", "_") + ".pdf", job_desc)
                uploaded_file_url = fs.url(filename)
                print("URL = ", uploaded_file_url)
                job_description_pdf = uploaded_file_url
            res_req.position = request_data["position"]
            if request_data["job_description"] is None:
                request_data["job_description"] = ""
            res_req.job_description = request_data["job_description"]
            res_req.created_by = stakeholder
            # res_req.module_id = request_data["module"]["id"]
            if job_description_pdf is not None:
                res_req.job_description_pdf = job_description_pdf
            res_req.count = request_data["count"]
        else:
            res_req = ResourcesRequired.objects.get(id=request_data["id"])
            res_req.closing_description = request_data["closing_description"]
            res_req.closed_by = stakeholder
            res_req.closed = True

        res_req.save()
        response_data = GetResourcesRequiredData.get_resource_required_data(res_req)
        return Response({"st": StatusCode.OK, "dt": response_data})


@permission_classes((permissions.IsAuthenticated,))
class UpdateGenericGuide(viewsets.ViewSet):
    """Get all the list of the submodules API."""

    def create(self, request):
        """Post method."""
        uploaded_file_url = None
        _file = request.data.get('guide', None)
        request_data = json.loads(request.data["dt"])
        name = request_data["name"]
        import os
        from smcc_backend import settings
        if _file is not None:
            fs = FileSystemStorage()
            # name = "generic_guide/Generic_Guide.pdf"
            if fs.exists(name):
                os.remove(os.path.join(settings.MEDIA_ROOT, name))
            filename = fs.save(name, _file)
            uploaded_file_url = fs.url(filename)
            print("URL = ", uploaded_file_url)
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class SubmitFeedBack(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        feedback = request.data["feedback"]
        stakeholder = StakeHolder.objects.get(user=request.user)
        FeedBack.objects.create(feedback=feedback, created_by=stakeholder)
        return Response({"st": StatusCode.OK})


@permission_classes((permissions.IsAuthenticated,))
class GetFeedBackList(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        feedbacks = FeedBack.objects.all()
        response_list = []
        for feedback in feedbacks:
            response_list.append({
                "feedback": feedback.feedback,
                "username": feedback.created_by.user.username
            })
        return Response({"st": StatusCode.OK, "dt": response_list})




@permission_classes((permissions.IsAuthenticated,))
class CreateBroadcast(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        extra_data = {}
        image = request.data.get('image', None)
        video = request.data.get('video', None)
        pdf_file = request.data.get('pdf', None)
        print("DIR = ", dir(image), image, video)
        if image is not None:
            fs = FileSystemStorage()
            filename = fs.save("images/" + str(image), image)
            uploaded_file_url = fs.url(filename)
            print("URL = ", uploaded_file_url)
            extra_data["image"] = uploaded_file_url
            
        if video is not None:
            fs = FileSystemStorage()
            filename = fs.save("videos/" + str(video), video)
            uploaded_file_url = fs.url(filename)
            print("URL = ", uploaded_file_url)
            extra_data["video"] = uploaded_file_url
        if pdf_file is not None:
            fs = FileSystemStorage()
            filename = fs.save("pdf/" + str(pdf_file), pdf_file)
            uploaded_file_url = fs.url(filename)
            print("URL = ", uploaded_file_url)
            extra_data["pdf"] = uploaded_file_url
        request_data = json.loads(request.data["dt"])
        msg = request_data["msg"]
        heading = request_data["heading"]
        groups = request_data["groups"]
        groups = request_data["groups"]
        to_users = [int(d["id"]) for d in request_data["toUsers"]]
        print("To Users = ", to_users)
        print("GROUPS = ", groups, type(groups))
        stakeholder = StakeHolder.objects.get(user=request.user)
        bmsg = BroadcastMessage.objects.create(message=msg, created_by=stakeholder, heading=heading, extra_data=extra_data)
        if len(groups) > 1:
            if "test" in groups:
                groups.remove("test")
        if "test" in groups:
            recivers = StakeHolder.objects.filter(permission_grp=PermissionGroups.objects.get(name="NHMind Test").id)
            for reciver in recivers:
                BroadcastMessageRecivers.objects.create(reciver=reciver, broadcast_msg=bmsg)
                self.create_notification(reciver, bmsg)
        else:
            recivers = StakeHolder.objects.filter(designation__in=groups)
            for reciver in recivers:
                if reciver.id in to_users:
                    to_users.remove(reciver.id)
                BroadcastMessageRecivers.objects.create(reciver=reciver, broadcast_msg=bmsg)
                self.create_notification(reciver, bmsg)
                
        print("ESCOND TO users = ", to_users)
        if len(to_users) > 0:
            recivers = StakeHolder.objects.filter(id__in=to_users)
            for reciver in recivers:
                BroadcastMessageRecivers.objects.create(reciver=reciver, broadcast_msg=bmsg)
                self.create_notification(reciver, bmsg)
        return Response({"st": StatusCode.OK})
    
    @staticmethod
    def create_notification(reciver, bmsg):
        NotificationManager.create_notification(reciver=reciver, heading=bmsg.heading, category=NotificationCategory.BROADCAST_MSG, 
                    extra_data={"brd_cst_msg_id": bmsg.id})


@permission_classes((permissions.IsAuthenticated,))
class GetMyNotifications(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        msgs = BroadcastMessageRecivers.objects.select_related("broadcast_msg").filter(reciver=stakeholder).order_by('-broadcast_msg__created_on')
        response = {"broadcast_msgs": []}
        for msg in msgs:
            response["broadcast_msgs"].append({
                "id": msg.broadcast_msg.id,
                # "msg": msg.broadcast_msg.message,
                "heading": msg.broadcast_msg.heading,
                "by": msg.broadcast_msg.created_by.user.username,
                "on": msg.broadcast_msg.created_on,
                "seen": msg.seen
            })
        return Response({"st": StatusCode.OK, "dt": response})

@permission_classes((permissions.IsAuthenticated,))
class GetBroadcastMsgs(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        filter_ = request.data["filter"]
        msgs = BroadcastMessageRecivers.objects.select_related("broadcast_msg").filter(reciver=stakeholder, **filter_).order_by('-broadcast_msg__created_on')
        response = []
        for msg in msgs:
            response.append({
                "msg": msg.broadcast_msg.message,
                "heading": msg.broadcast_msg.heading,
                "by": msg.broadcast_msg.created_by.user.username,
                "on": msg.broadcast_msg.created_on,
                "image": msg.broadcast_msg.extra_data.get("image", None),
                "video": msg.broadcast_msg.extra_data.get("video", None),
                "pdf": msg.broadcast_msg.extra_data.get("pdf", None),
            })
            msg.seen = True
            msg.save()
        # if len(response) == 1:
        #     response = response[0]
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class ReferCandidate(viewsets.ViewSet):
    """Submit FeedBack API."""

    def create(self, request):
        """Post method."""
        refaral_cv = request.data.get('cv_file', None)
        request_data = json.loads(request.data["dt"])
        res_req = json.loads(request.data["res_req"])
        if refaral_cv is not None:
            fs = FileSystemStorage()
            extension = os.path.splitext(refaral_cv.name)[1]
            original_filename = str(request_data["name"]).replace(" ", "_").replace(".", "").replace("-", "_") + extension
            print(extension)
            filename = fs.save("referals/" + original_filename, refaral_cv)
            uploaded_file_url = fs.url(filename)
            stakeholder = StakeHolder.objects.get(user=request.user)
            referal = Referals.objects.create(refered_by=stakeholder, referal_data=request_data, candidate_cv=uploaded_file_url, resource_req_id=res_req["id"])
            attachments = []
            from io import StringIO
            import csv
            csvfile = StringIO()
            attachments.append({
                "file_name": original_filename,
                "file": refaral_cv,
                "type": "app"
            })
            mail = Mail()
            recipients = [request.user.email]
            cc_list = []#["leadership@nslhub.com", "nhmind@nslhub.com"]
            subject = "Referral by " + stakeholder.full_name + " - Profile of "+ request_data["name"]
            content = f"""Dear {request.user.first_name},<br><br>

                        Thank you for referring - <b>{request_data["name"]}</b> for <b>{referal.resource_req.position}</b>.<br><br>

                        As you know, referrals are one of our best sources of finding new talent, and your effort is extremely valuable to us. 
                        To track the referral status, you can contact the Leadership Module Leaders.<br><br>

                        Regards,<br><br>

                        NH Mind"""

            #New implementation
            from django.core.mail import EmailMessage
            email = EmailMessage(subject,content,"nhmind@nslhub.com",recipients, cc=cc_list)
            email.content_subtype = "html"
            email.attach_file("media/"+filename)
            email.send()

        response = {}
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class CreateEditTweet(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        # heading = request.data["heading"]
        body = request.data["body"]
        tweet_id = request.data["id"]
        tweet_obj = Tweet.objects.get(stakeholder=stakeholder, id=tweet_id)
        # tweet_obj.heading=heading
        tweet_obj.body=body
        tweet_obj.save()
        response = {}
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class GetMyTweets(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        filter_ = request.data.get("filter", {})
        today_tweet = None
        exclude_filter = {}
        today = datetime.date.today()
        print("DAY === ", today, today.isoweekday())
        friday = None
        if today.isoweekday() == 5:
            friday = today
        elif today.isoweekday() == 6:
            friday = today - datetime.timedelta(days=1)
        elif today.isoweekday() == 7:
            friday = today - datetime.timedelta(days=2)
        elif today.isoweekday() == 1:
            friday = today - datetime.timedelta(days=3)
        if friday is not None:
            tweet_count = Tweet.objects.filter(stakeholder=stakeholder, created_on__date=friday).count()
            if tweet_count > 1:
                Tweet.objects.filter(stakeholder=stakeholder, created_on__date=friday, body=None).delete()
                Tweet.objects.filter(stakeholder=stakeholder, created_on__date=friday, body="").delete()
                tweet_count = Tweet.objects.filter(stakeholder=stakeholder, created_on__date=friday).count()
                if tweet_count > 1:
                    Tweet.objects.filter(stakeholder=stakeholder, created_on__date=friday).delete()
                    tweet_count = 0
            if tweet_count == 1:
                today_tweet_obj = Tweet.objects.get(stakeholder=stakeholder, created_on__date=friday)
            else:
                today_tweet_obj = Tweet.objects.create(stakeholder=stakeholder, created_on=friday)
            today_tweet = {"id": today_tweet_obj.id, "heading": today_tweet_obj.heading, "body": today_tweet_obj.body}
            exclude_filter = {"id": today_tweet_obj.id}
        from django.db.models import Q
        # exclude_filter["body"] = None
        tweets = Tweet.objects.filter(stakeholder=stakeholder, **filter_).exclude(Q(**exclude_filter) | Q(body=None)).order_by("-created_on")
        response = []
        for tweet in tweets:
            response.append({"heading": tweet.heading, "body": tweet.body, "created_on": tweet.created_on})
        return Response({"st": StatusCode.OK, "dt": {"today_tweet": today_tweet , "old_tweet": response}})


@permission_classes((permissions.IsAuthenticated,))
class GetAllTweets(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        filter_ = request.data.get("filter", {})
        print("FILTER = ", filter_)
        today_tweet = {}
        today = datetime.date.today()

        tweets = Tweet.objects.filter(**filter_).select_related("stakeholder__user").order_by("stakeholder__employee_id")
        response = []
        for tweet in tweets:
            response.append({"heading": tweet.heading, "body": tweet.body, "created_on": tweet.created_on,
                            "user": GetStakeHolderDetailedInfo.get_stakeholder_detailed_info(tweet.stakeholder)})
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class GetAllRMSCategories(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        filter_ = request.data.get("filter", {})
        print("FILTER = ", filter_)
        rms_categories = RMSCategories.objects.filter(**filter_).order_by("-parent_id")
        response = []
        for category in rms_categories:
            data = self.get_rms_category_dict(category)
            response.append(data)
        return Response({"st": StatusCode.OK, "dt": response})
    
    @staticmethod
    def get_rms_category_dict(rms_category):
        data = {"id": rms_category.id, "name": rms_category.name}
        if rms_category.parent != None:
            data["parent"] = rms_category.parent.id
            data["parent_name"] = rms_category.parent.name
        if rms_category.stakeholder_grp != None:
            data["user_grps"] = rms_category.stakeholder_grp.id
        data["tat_days"] = int(rms_category.tat / 24)
        data["tat_hrs"] = rms_category.tat % 24
        data["priority"] = rms_category.priority
        return data


@permission_classes((permissions.IsAuthenticated,))
class SubmitRMSRequest(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        request_data = request.data
        category = RMSCategories.objects.get(id=request_data["cat_id"])
        RMSRequest.objects.create(request_type=category, requested_by=stakeholder,
                                  summary=request_data["summary"], details=request_data["details"],
                                  status=RMSRequestStatus.CREATED)
        response = {}
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class GetMyRMSRequests(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        filter_ = request.data.get("filter", {})
        request_type = request.data.get("r_type", "requested_by")
        if request_type == "assigned_to":
            filter_["assigned_to"] = stakeholder
        else:
            filter_["requested_by"] = stakeholder
        print("FILTER = ", filter_, request.data)
        requests = RMSRequest.objects.filter(**filter_).order_by("id")
        response = []
        for req in requests:
            response.append({
                "id": req.id,
                "type": req.request_type.name,
                "summary": req.summary,
                "details": req.details,
                "requested_by": GetStakeHolderDetailedInfo.get_stakeholder_basic_info(req.requested_by),
                "assigned_to": GetStakeHolderDetailedInfo.get_stakeholder_basic_info(req.assigned_to),
                "created_on": req.created_on,
                "status": str(req.status),
            })
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class CreateUpdateWorkMeal(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        stakeholder = StakeHolder.objects.get(user=request.user)
        print("DATA = ", request.data)
        meals_date = request.data["meal_on"]
        meal_times = request.data["meal_times"]
        meals_for = request.data["meal_for"]
        for meal_time in meal_times:
            for employee in meals_for:
                if employee["id"] != None:
                    try:
                        WorkMeal.objects.get(meal_for__id=employee["id"], meal_on=meals_date, meal_time=meal_time)
                    except:
                        emp_obj = StakeHolder.objects.get(id=employee["id"])
                        WorkMeal.objects.create(meal_for=emp_obj, meal_on=meals_date, meal_time=meal_time,
                                            meal_item=employee["item"], created_by=stakeholder)
        return Response({"st": StatusCode.OK})
        


@permission_classes((permissions.IsAuthenticated,))
class GetWorkMeal(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        today = request.data["date"]
        response_dt = []
        # response_dt["date"] = today
        # for meal_time in MealTime:
        #     response_dt[meal_time.value] = {}
        #     for meal_item in MealTypes:
        #         # print("TIME = ", dir(meal_time), meal_time.value)
        #         response_dt[meal_time.value][meal_item.value] = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time.value,meal_item=meal_item.value).count()

        workmealusers = WorkMeal.objects.filter(meal_on=today, meal_time=request.data["time"])
        for workmealuser in workmealusers:
            response_dt.append({
                "username": workmealuser.meal_for.user.username,
                "type": workmealuser.meal_item,
                "ordered_by": workmealuser.created_by.user.username,
            })
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.AllowAny,))
class MyWorkMealOrders(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        history_from = request.data.get("from", datetime.datetime.now().date())
        stakeholder = StakeHolder.objects.get(user=request.user)
        response_dt = []
        work_meal_dates = WorkMeal.objects.filter(created_by=stakeholder, meal_on__gte=history_from).values('meal_on').order_by('meal_on').distinct()
        print("DATES = ", work_meal_dates)
        for work_meal_date in work_meal_dates:
            workmealusers = WorkMeal.objects.filter(created_by=stakeholder, meal_on=work_meal_date["meal_on"])
            date_data = []
            for workmealuser in workmealusers:
                date_data.append({
                    "id": workmealuser.id,
                    "username": workmealuser.meal_for.user.username,
                    "type": workmealuser.meal_item,
                    "ordered_by": workmealuser.created_by.user.username,
                    "meal_time": workmealuser.meal_time,
                })
            response_dt.append({"date": work_meal_date["meal_on"], "data": date_data})
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.AllowAny,))
class DeleteWorkMealOrder(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        # history_from = request.data.get("from", datetime.datetime.now().date())
        stakeholder = StakeHolder.objects.get(user=request.user)
        dates = [request.data["date"]]
        print("")
        response_dt = []
        for date in dates:
            WorkMeal.objects.filter(created_by=stakeholder, meal_on=date).delete()
            # date_data = []
            # for workmealuser in workmealusers:
            #     date_data.append({
            #         "id": workmealuser.id,
            #         "username": workmealuser.meal_for.user.username,
            #         "type": workmealuser.meal_item,
            #         "ordered_by": workmealuser.created_by.user.username,
            #         "meal_time": workmealuser.meal_time,
            #     })
            # response_dt.append({"date": work_meal_date["meal_on"], "data": date_data})
        return Response({"st": StatusCode.OK, "dt": response_dt})




@permission_classes((permissions.IsAuthenticated,))
class GetAllReferrals(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        response_dt = []
        referrals = Referals.objects.all().order_by("-created_on")
        for referral in referrals:
            response_dt.append({
                "refered_by": referral.refered_by.user.username,
                "resource_req": GetResourcesRequiredData.get_resource_required_data(referral.resource_req),
                "referal_data": referral.referal_data,
                "candidate_cv": referral.candidate_cv
            })
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.AllowAny,))
class WorkMealSendEmail(viewsets.ViewSet):
    """Create and edit tweet API."""

    def list(self, request):
        """Post method."""
        
        today = datetime.datetime.now().date()
        subject = "Work Meal Order " + str(today)
        meal_time = MealTime.DINNER
        total_count = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time).count()
        if total_count == 0:
            return Response({"st": "OK"})
        veg_count = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time, meal_item=MealTypes.VEGETARIAN).count()
        non_veg_count = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time, meal_item=MealTypes.NON_VEGETARIAN).count()
        eggetarian_count = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time, meal_item=MealTypes.EGGETARIAN).count()
        content = "Hi,<br><br><b>Work Meal Details</b>:<br><br>" + "DATE : " + str(today) + "<br>" + " MEAL : " + MealTime(meal_time).name + "<br>" +\
                  "TOTAL COUNT : "+ str(total_count) + "<br>" +\
                  "VEG: " + str(veg_count) + "<br>" +\
                  "NON VEG: " + str(non_veg_count) + "<br>" +\
                  "EGGETARIAN: " + str(eggetarian_count) + "<br><br>" +\
                  "Regards <br> <b>NH MIND</b>" 
        
        attachments = []
        from io import StringIO
        import csv
        csvfile = StringIO()
        filewriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        filewriter.writerow(['Date', str(today)])
        filewriter.writerow(['Time', MealTime(meal_time).name])
        filewriter.writerow(['Total Count', str(total_count)])
        filewriter.writerow(['Veg Count', str(veg_count)])
        filewriter.writerow(['Non Veg Count', str(non_veg_count)])
        filewriter.writerow(['Eggitarian Count', str(eggetarian_count)])
        filewriter.writerow([])
        filewriter.writerow(['Name', 'Meal Type'])
        for meal in MealTypes:
            # print(meal, dir(meal))
            leadears = WorkMeal.objects.filter(meal_on=today, meal_time=meal_time, meal_item=meal.value).values_list("meal_for__user__username")
            for leader in leadears:
                filewriter.writerow([leader[0], meal.name])
        attachments.append({
            "file_name": "leader_count_sheet.csv",
            "file": csvfile
        })
        mail = Mail()
        recipients = ["ajay.dasaraiahgari@nslhub.com", "rajeshvarma.penmatsa@nslhub.com",
                      "joseph.vithayathil@nslhub.com", "silvester.stephen@nslhub.com", "harsh.patel@nslhub.com", "bhavani.shankar@nslhub.com" ]
        recipients = ["joseph.vithayathil@nslhub.com"]
        mail.send({"recipients": recipients, "content": content, "subject":subject, "attachments": attachments})
        return Response({"st": StatusCode.OK, "dt": {"recipients": "joseph.vithayathil@nslhub.com", "content": content, "subject":subject}})


@permission_classes((permissions.IsAuthenticated,))
class GetRMSTasks(viewsets.ViewSet):
    """Get RMS Tasks based on filter."""

    def create(self, request):
        """Post method."""
        filter_ = request.data.get("filter", {})
        rms_requests = RMSRequest.objects.filter().order_by("id")
        print("rqsts = ", rms_requests)
        response_dt = []
        for rms_request in rms_requests:
            response_dt.append(GetGroupRMSTasks.get_rms_request_dict(rms_request))
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.IsAuthenticated,))
class GetGroupRMSTasks(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        response_dt = []
        stakeholder = StakeHolder.objects.get(user=request.user)
        grps = StakeHolderRMSGroups.objects.filter(leaders=stakeholder)
        print("GRPS = ", grps)
        rms_categories = RMSCategories.objects.filter(stakeholder_grp__in=grps)
        print("cats = ", rms_categories)
        rms_requests = RMSRequest.objects.filter(request_type__in=rms_categories).order_by("id")
        print("rqsts = ", rms_requests)

        for rms_request in rms_requests:
            response_dt.append(self.get_rms_request_dict(rms_request))
        return Response({"st": StatusCode.OK, "dt": response_dt})
    
    @staticmethod
    def get_rms_request_dict(rms_request):
        response = {}
        response["id"] = rms_request.id
        response["requested_by"] = GetStakeHolderDetailedInfo.get_stakeholder_basic_info(rms_request.requested_by)
        response["request_type"] = GetAllRMSCategories.get_rms_category_dict(rms_request.request_type)
        response["summary"] = rms_request.summary
        response["details"] = rms_request.details
        response["status"] = rms_request.status
        response["created_on"] = rms_request.created_on
        response["fullfilled_on"] = rms_request.fullfilled_on
        if rms_request.assigned_to is not None:
            response["assigned_to"] = rms_request.assigned_to.id
        else:
            response["assigned_to"] = None
        return response


# @permission_classes((permissions.IsAuthenticated,))
# class GetRMSUserGroups(viewsets.ViewSet):
#     """Create and edit tweet API."""

#     def create(self, request):
#         """Post method."""
#         response_dt = []
#         grps = StakeHolderRMSGroups.objects.all()
#         for grp in grps:
#             response_dt.append(self.get_rms_user_grp_dict(grp))
#         return Response({"st": StatusCode.OK, "dt": response_dt})
    
#     @staticmethod
#     def get_rms_user_grp_dict(rms_grp):
#         response = {}
#         response["id"] = rms_grp.id
#         response["name"] = rms_grp.name
#         response["leaders"] = []
#         response["team_members"] = []
#         return response


@permission_classes((permissions.IsAuthenticated,))
class GetRMSUserGroups(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        response_dt = []
        grps = StakeHolderRMSGroups.objects.all()
        for grp in grps:
            response_dt.append(self.get_rms_user_grp_dict(grp))
        return Response({"st": StatusCode.OK, "dt": response_dt})
    
    @staticmethod
    def get_rms_user_grp_dict(rms_grp):
        response = {}
        response["id"] = rms_grp.id
        response["name"] = rms_grp.name
        response["leaders"] = rms_grp.leaders.all().values_list("id")
        response["team_members"] = rms_grp.team_members.all().values_list("id")
        return response

@permission_classes((permissions.IsAuthenticated,))
class CreateEditRMSCategory(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        request_data = request.data
        print("DATA = ", request_data)
        response_dt = {}
        if "id" not in request_data:
            rmsGrp = RMSCategories.objects.create(name=request_data["name"])
        else:
            rmsGrp = RMSCategories.objects.get(id=request_data["id"])
            rmsGrp.name = request_data["name"]
        if "parent" in request_data:
            rmsGrp.parent_id = request_data["parent"]
        if "user_grps" in request_data:
            rmsGrp.stakeholder_grp_id = request_data["user_grps"]
        rmsGrp.tat = int(request_data["tat_days"]) * 24 + int(request_data["tat_hrs"])
        rmsGrp.priority = request_data["priority"]
        rmsGrp.save()
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.IsAuthenticated,))
class AssignRMSTask(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        request_data = request.data
        print(request_data)
        response_dt = {}
        rms_request = RMSRequest.objects.get(id=request_data["id"])
        rms_request.assigned_to_id = request_data["assigned_to"]
        rms_request.status = RMSRequestStatus.ASSIGNED
        rms_request.save()
        return Response({"st": StatusCode.OK, "dt": response_dt})


@permission_classes((permissions.IsAuthenticated,))
class AssignRTGTask(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        request_data = request.data
        print(request_data)
        response_dt = {}
        rms_request = RMSRequest.objects.get(id=request_data["id"])
        rms_request.assigned_to_id = request_data["assigned_to"]
        rms_request.status = RMSRequestStatus.ASSIGNED
        rms_request.save()
        return Response({"st": StatusCode.OK, "dt": response_dt})



@permission_classes((permissions.IsAuthenticated,))
class UpdateMyTask(viewsets.ViewSet):
    """Create and edit tweet API."""

    def create(self, request):
        """Post method."""
        request_data = request.data
        print(request_data)
        response_dt = {}
        rms_request = RMSRequest.objects.get(id=request_data["id"])
        if int(request_data["status"]) > rms_request.status:
            rms_request.status = request_data["status"]
            if rms_request.status == RMSRequestStatus.FULFILLED:
                rms_request.fullfilled_on = datetime.datetime.now()
            rms_request.save()
            return Response({"st": StatusCode.OK, "dt": response_dt})
        else:
            return Response({"st": StatusCode.ERROR})


@permission_classes((permissions.IsAuthenticated,))
class GetMyRMSStatistics(viewsets.ViewSet):
    """Get personal RMS statistics password API."""

    def create(self, request):
        user = request.user
        stakeholder = StakeHolder.objects.get(user=user)
        response = {}
        response["total_count"] = RMSRequest.objects.filter(assigned_to=stakeholder).count()
        response["fullfilled_count"] = RMSRequest.objects.filter(assigned_to=stakeholder, status=RMSRequestStatus.FULFILLED).count()
        response["to_do_count"] = RMSRequest.objects.filter(assigned_to=stakeholder).exclude(status=RMSRequestStatus.FULFILLED).count()
        return Response({"st": StatusCode.OK, "dt": response})


@permission_classes((permissions.IsAuthenticated,))
class GetAllSkillNames(viewsets.ViewSet):
    """Get all the list of the Skill API."""

    def create(self, request):
        skills = Skills.objects.all().values_list('name', flat=True)
        return Response({"st": StatusCode.OK, "dt": skills})

