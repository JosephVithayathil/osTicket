# Rest apis file.
import datetime
import json
import os

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Sum
from rest_framework import permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from .status_codes import StatusCode

from .models import ticket,ticket_status,user_email,help_topic

DEFAULT_PASSWORD = "@changepassword"


@permission_classes((permissions.AllowAny,))
class GetTicketDetails(viewsets.ViewSet):
    """ post Method to get all the details of tickets created by the user via email address"""

    def create(self, request):

        email_address = request.data["email_address"]
        user_email_obj = user_email.objects.filter(address = email_address)
        user_id = []
        for id in user_email_obj:
            user_id.append(id.user_id)
        ticket_obj = ticket.objects.filter(user_id__in =user_id)
        response_data =[]
        for data in ticket_obj:
            response_data.append(GetTicketDetails.get_ticket_details(data))
        return Response({"st": StatusCode.OK, "dt": response_data})
    

    @staticmethod
    def get_ticket_details(data):
        return {
            "id": data.ticket_id,
            "ticket_pid" : data.ticket_pid,
            "number" : data.number,
            "user_id" : data.user_id,
            "user_email_id" : data.user_email_id,
            "status_id" : data.status_id,
            "dept_id" : data.dept_id,
            "sla_id" : data.sla_id,
            "topic_id" : data.topic_id,
            "staff_id" : data.staff_id,
            "team_id" : data.team_id,
            "email_id" : data.email_id,
            "lock_id" : data.lock_id,
            "flags" : data.flags,
            "sort" : data.sort,
            "ip_address" : data.ip_address,
            "source" : data.source,
            "source_extra" : data.source_extra,
            "isoverdue" : data.isoverdue,
            "isanswered" : data.isanswered,
            "duedate" : data.duedate,
            "est_duedate" : data.est_duedate,
            "reopened" : data.reopened,
            "closed " : data.closed,
            "lastupdate" : data.lastupdate,
            "created" : data.created,
            "updated" : data.updated,

        }



@permission_classes((permissions.AllowAny,))
class GetOsTicketStatus(viewsets.ViewSet):
    """Method to get ticket number and status of ticket created by user """
    

    def create(self, request):

        email_address = request.data["email_address"]
        user_email_obj = user_email.objects.filter(address = email_address)
        for id in user_email_obj:
            user_id = id.user_id
      
        # ticket_obj = ticket.objects.filter(user = user_id)
    

        response_data = []
        for data in ticket_obj:
            response_data.append(GetOsTicketStatus.get_ticket_details(data))
        return Response({"st": StatusCode.OK, "dt": response_data})


    @staticmethod
    def get_ticket_details(data):
        return {
            "number" : data.number,
            "status" : data.status.state,
        }


@permission_classes((permissions.AllowAny,))
class GetStatusOfListOfTicketId(viewsets.ViewSet):
    """Method to get ticket status of list of ticket number """
    

    def create(self, request):

        listofticketnumber = request.data["listofticketnumber"]

        response_data = []

        ticket_obj = ticket.objects.filter(number__in = listofticketnumber)

        for data in ticket_obj:
            response_data.append(GetOsTicketStatus.get_ticket_details(data))
 


    @staticmethod
    def get_os_ticket_status(data):
        return {
            "number" : data.number,
            "status" : data.status.state,
        }
        
class GetHelpTopic(viewsets.ViewSet):
    """Method to get topic and notes"""
    def create(self,request):
        topic_id = request.data["topic_id"]
        ticket_id = request.data["ticket_id"]
        help_obj  = help_topic.objects.filter(topic_id = topic_id)
        # a = ticket.objects.filter(topic_id=topic_id,ticket_id=40)
        # print("=================================================================",a.values())
        # print("---------aaaaaaaaaaa--------------",help_obj.values())
        
        response_data = []
        for data in help_obj:
            response_data.append(GetHelpTopic.get_help_topic(data))
        
        return Response({"st": StatusCode.OK, "dt": response_data})
    
    
    @staticmethod
    def get_help_topic(data):
        return {
            "topic" : data.topic,
            "notes" : data.notes,
        }
    
    
    
        






