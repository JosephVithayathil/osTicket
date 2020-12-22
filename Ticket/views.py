from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import status 



# class Login(APIView):

#     def post(self,request):
#          username = request.POST.get('username')
#          password = request.POST.get('password')

#          user = authenticate(request, username=username, password=password)
#          if user is not None:
#              return JsonResponse({"login":"Sucessfully"})
#          else:
            
#              return JsonResponse({"Wrong1":"credential"})

# class UserDetails(APIView):
#     print("**************************************")
#     def get(self,request):
#         print("---------------------------")
#         print("--------------------------------")
#         return JsonResponse({"Wrong1":"credential"})








  

        
       
