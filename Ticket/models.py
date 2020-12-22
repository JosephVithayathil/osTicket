from django.db import models
from enum import Enum
from django.db.models import Model 


class SourceTypeEnum(Enum):
    Web = 0
    Email = 1
    Phone = 2
    API = 3
    Other = 4

class user_email(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    flags = models.IntegerField()
    address = models.TextField(max_length = 255)

    class Meta:
        managed = False
        db_table = "ost_user_email"


class user(models.Model):
    id = models.IntegerField(primary_key=True)
    org_id = models.IntegerField()
    default_email = models.ForeignKey(user_email,on_delete=models.CASCADE,null= True)
    status = models.IntegerField()
    name = models.CharField(max_length = 128,default = '')
    created = models.DateTimeField() 
    updated = models.DateTimeField() 

    class Meta:
        managed = False
        db_table = "ost_user"

class ticket_status(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length = 60,default = '')
    state = models.CharField(max_length = 16,default = '')
    mode = models.IntegerField()
    flags = models.IntegerField()
    sort = models.IntegerField()
    properties  = models.TextField(max_length = 65535) 
    created = models.DateTimeField() 
    updated = models.DateTimeField() 

    def __str__(self):
        return self.name
        
    class Meta:
        managed = False
        db_table = "ost_ticket_status"



class ticket(models.Model):
    ticket_id = models.IntegerField(primary_key=True)
    ticket_pid = models.IntegerField()
    number = models.CharField(max_length=200,default ='')
    user = models.ForeignKey(user,on_delete=models.CASCADE,null= True)
    user_email_id = models.IntegerField()
    status = models.ForeignKey(ticket_status,on_delete=models.CASCADE,null= True)
    dept_id = models.IntegerField()
    sla_id = models.IntegerField()
    topic_id = models.IntegerField()
    staff_id = models.IntegerField()
    team_id = models.IntegerField()
    email_id = models.IntegerField()
    lock_id = models.IntegerField()
    flags = models.IntegerField()
    sort = models.IntegerField()
    ip_address = models.CharField(max_length = 40,default ='')
    source = models.IntegerField(choices=[(val.value, val.name) for val in SourceTypeEnum], null=True)
    source_extra = models.CharField(max_length = 40,default ='')
    isoverdue = models.SmallIntegerField(null=True)
    isanswered = models.SmallIntegerField(null=True)
    duedate = models.DateTimeField() 
    est_duedate = models.DateTimeField() 
    reopened = models.DateTimeField() 
    closed = models.DateTimeField() 
    lastupdate = models.DateTimeField() 
    created = models.DateTimeField() 
    updated = models.DateTimeField() 


    class Meta:
        managed = False
        db_table = "ost_ticket"


class user_account(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length = 128,default = '')
    status = models.IntegerField()
    timezone = models.CharField(max_length = 64,default = '')
    lang = models.CharField(max_length = 64,default = '')
    username = models.CharField(max_length = 64,default = '')
    passwd = models.CharField(max_length = 128,default = '')
    backend = models.CharField(max_length = 32,default = '')
    extra = models.TextField(max_length = 65535)
    registered = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "ost_user_account"







