
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from . import models
from django.contrib.auth.models import User
import datetime

class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        self.accept() 

        try:
            user_channel = models.UserChannel.objects.get(user = self.scope.get("user"))
            user_channel.channel_name = self.channel_name
            user_channel.save()

        except:
            user_channel = models.UserChannel()
            user_channel.user = self.scope.get("user")
            user_channel.channel_name = self.channel_name
            user_channel.save()

        


        self.person_id = self.scope.get("url_route").get("kwargs").get("id")

        # async_to_sync(self.channel_layer.group_add)("test" , self.channel_name) 
        
        # data = {
        #     "type" : "reciver.function",
        # }
        # async_to_sync(self.channel_layer.group_send)("group_channels" , data) 

    def receive(self, text_data):
        text_data = json.loads(text_data)
        # print(text_data.get("type"))
        # print(text_data.get("message"))
        other_user = User.objects.get(id = self.person_id)


        if text_data.get("type") == "new_message":
            now = datetime.datetime.now()
            date = now.date()
            time = now.time()


            new_message = models.Message()
            new_message.from_who = self.scope.get("user")
            new_message.to_whom = other_user
            new_message.message = text_data.get("message")
            new_message.date = date
            new_message.time = time
            new_message.has_been_seen = False
            new_message.save()

            try:
                user_channel_name = models.UserChannel.objects.get(user= other_user)
            
                data = {
                    "type" : "reciver_function",
                    "type_of_data" : "new_message",
                    "data" : text_data.get("message")
                }
        
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)
            except:
                pass

        elif text_data.get("type") == "i_have_seen_the_message":  
            try:
                user_channel_name = models.UserChannel.objects.get(user= other_user)
                data = {"type" : "reciver_function",
                        "type_of_data" : "the_masssages_have_been_seen_from_the_other"}
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)

                messages_have_not_been_seen = models.Message.objects.filter(from_who = other_user, to_whom = self.scope.get("user"))
                messages_have_not_been_seen.update(has_been_seen = True)

            except:
                pass
    
    def reciver_function(self, recived_data):
        data = json.dumps(recived_data)
        self.send(data)