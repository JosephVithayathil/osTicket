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
        
class department(models.Model):
    pid = models.IntegerField() 
    tpl_id = models.IntegerField()
    sla_id = models.IntegerField()
    schedule_id = models.IntegerField()
    email_id = models.IntegerField()
    autoresp_email_id = models.IntegerField()
    manager_id =  models.IntegerField()
    flags = models.IntegerField()
    name = models.IntegerField()
    signature = models.TextField(max_length = 65535)
    ispublic =  models.SmallIntegerField()
    group_membership = models.SmallIntegerField() 
    ticket_auto_response = models.SmallIntegerField()
    message_auto_response = models.SmallIntegerField()
    path = models.CharField(max_length= 128)
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = "ost_department"
        
class staff(models.Model):
    staff_id = models.IntegerField()
    dept_id = models.ForeignKey(department,on_delete=models.CASCADE,null= True)
    role_id = models.IntegerField()
    username = models.CharField(max_length= 32)
    firstname = models.CharField(max_length= 32)
    lastname = models.CharField(max_length= 32)
    passwd = models.CharField(max_length= 128)
    backend = models.CharField(max_length= 32)
    email = models.CharField(max_length= 255)
    phone = models.CharField(max_length= 24)
    phone_ext = models.CharField(max_length= 6)
    mobile = models.CharField(max_length= 24)
    signature = models.TextField(max_length = 65535)
    lang = models.CharField(max_length= 16)
    timezone = models.CharField(max_length= 64)
    locale = models.CharField(max_length= 16)
    notes = models.TextField(max_length = 65535)
    isactive = models.SmallIntegerField(max_length=1)
    isadmin = models.SmallIntegerField(max_length=1)
    isvisible = models.SmallIntegerField(max_length=1)
    onvacation = models.SmallIntegerField(max_length=1)
    assigned_only = models.SmallIntegerField()
    change_passwd = models.SmallIntegerField()
    max_page_size = models.IntegerField()
    auto_refresh_rate = models.IntegerField()
    # default_signature_type =
    # default_paper_size =
    extra = models.TextField(max_length = 65535)
    permissions = models.TextField(max_length = 65535)
    created = models.DateTimeField(auto_now_add=True)
    lastlogin = models.DateTimeField(auto_now_add=True)
    passwdreset = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = "ost_staff"
        
class ticket_priority(models.Model):
    priority_id = models.SmallIntegerField()
    priority = models.CharField(max_length= 60)
    priority_desc = models.CharField(max_length= 30)
    priority_color = models.CharField(max_length = 7)
    priority_urgency = models.SmallIntegerField()
    ispublic = models.SmallIntegerField()
    
    class Meta:
        managed = False
        db_table = "ost_ticket_priority" 
           
        
class help_topic(models.Model):
    topic = models.IntegerField(primary_key=True)
    topic_pid = models.IntegerField()
    ispublic = models.SmallIntegerField()
    noautoresp = models.SmallIntegerField()
    flags = models.IntegerField() 
    status_id = models.IntegerField() 
    priority_id = models.ForeignKey(ticket_priority,on_delete=models.CASCADE,null= True)
    dept_id = models.ForeignKey(department,on_delete=models.CASCADE,null= True)
    staff_id = models.IntegerField() 
    team_id = models.IntegerField() 
    sla_id = models.IntegerField() 
    page_id = models.IntegerField() 
    sequence_id = models.IntegerField()  
    sort = models.IntegerField() 
    topic = models.CharField(max_length= 32)
    number_format = models.CharField(max_length= 32)
    notes = models.TextField(max_length = 65535)
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        managed = False
        db_table = "ost_help_topic"
        


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
    # topic = models.ForeignKey(help_topic,on_delete=models.CASCADE,null= True)
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
        








