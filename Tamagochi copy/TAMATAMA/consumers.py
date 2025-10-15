import json
import random
import asyncio
from asgiref.sync import sync_to_async
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

from channels.layers import get_channel_layer

from django.db import models
from TAMATAMA.models import models_tamagochi, models_global_chat
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
online_users = set()

class tam_need_water(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
        self.current_need = current_need.tam_water

        self.current_need = calculate_need(self.current_need, current_need.tam_timeleft, 10)

        await self.send(json.dumps({"water_need" : self.current_need}))

        asyncio.create_task(self.updates(self.user))

    async def updates(self, Userid):
        while True:
            await asyncio.sleep(10)
            self.current_need -= 1
            if self.current_need < 0 :
                self.current_need = 0
            if self.current_need > 100 :
                self.current_need = 100
            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_water = self.current_need)

            await self.send(json.dumps({"water_need" : self.current_need}))

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            data = json.loads(text_data)
            if data.get("action") == "add_water":
                current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
                self.current_need = current_need.tam_water 
                self.current_need += 15
                if self.current_need > 100:
                    self.current_need = 100
                await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_water = self.current_need)
                await self.send(json.dumps({"water_need" : self.current_need}))

    async def disconnect(self, code):
        await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_timeleft = datetime.datetime.now())
        print(code)


class tam_need_food(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
        self.current_need = current_need.tam_food

        self.current_need = calculate_need(self.current_need, current_need.tam_timeleft, 16)

        await self.send(json.dumps({"food_need" : self.current_need}))

        asyncio.create_task(self.updates(self.user))

    async def updates(self, Userid):
        while True:
            await asyncio.sleep(16)
            self.current_need -= 1
            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_food = self.current_need)

            await self.send(json.dumps({"food_need" : self.current_need}))

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            data = json.loads(text_data)
            if data.get("action") == "add_food":
                current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
                self.current_need = current_need.tam_food 
                self.current_need += 15
                if self.current_need > 100:
                    self.current_need = 100
                await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_food = self.current_need)
                await self.send(json.dumps({"food_need" : self.current_need}))

    async def disconnect(self, code):
        await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_timeleft = datetime.datetime.now())
        print(code)


class tam_need_sleep(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
        self.current_need = current_need.tam_sleep

        self.current_need = calculate_need(self.current_need, current_need.tam_timeleft, 20)

        await self.send(json.dumps({"sleep_need" : self.current_need}))

        asyncio.create_task(self.updates(self.user))

    async def updates(self, Userid):
        while True:
            await asyncio.sleep(20)
            self.current_need -= 1
            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_sleep = self.current_need)

            await self.send(json.dumps({"sleep_need" : self.current_need}))

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            data = json.loads(text_data)
            if data.get("action") == "add_sleep":
                current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
                self.current_need = current_need.tam_sleep
                self.current_need += 15
                if self.current_need > 100:
                    self.current_need = 100
                await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_sleep = self.current_need)
                await self.send(json.dumps({"sleep_need" : self.current_need}))

    async def disconnect(self, code):
        await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_timeleft = datetime.datetime.now())
        print(code)


class tam_need_playtime(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
        self.current_need = current_need.tam_playtime

        self.current_need = calculate_need(self.current_need, current_need.tam_timeleft, 16)


        await self.send(json.dumps({"playtime_need" : self.current_need}))

        asyncio.create_task(self.updates(self.user))

    async def updates(self, Userid):
        while True:
            await asyncio.sleep(16)
            self.current_need -= 1
            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_playtime = self.current_need)

            await self.send(json.dumps({"playtime_need" : self.current_need}))

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            data = json.loads(text_data)
            if data.get("action") == "add_playtime":
                current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
                self.current_need = current_need.tam_playtime
                self.current_need += 15
                if self.current_need > 100:
                    self.current_need = 100
                await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_playtime = self.current_need)
                await self.send(json.dumps({"playtime_need" : self.current_need}))

    async def disconnect(self, code):
        await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = self.user, tam_timeleft = datetime.datetime.now())
        print(code)


class tam_parameter_income(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        current_need = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
        self.current_need = current_need.tam_income

        await self.send(json.dumps({"tam_income_json" : current_need.tam_income, "tam_money" : current_need.tam_money}))

        asyncio.create_task(self.updates(self.user))

    async def updates(self, Userid):
        while True:
            await asyncio.sleep(10)

            parameters = await models_tamagochi.objects.filter(tam_owner = self.user).afirst()
            parameter = parameters.tam_water + parameters.tam_food + parameters.tam_sleep + parameters.tam_playtime

            self.current_need = 50 
            if parameter < 200:
                self.current_need -= 50
            else:
                self.current_need -= (400- parameter)//4

            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_income = self.current_need)
            tam_money = parameters.tam_money + self.current_need
            await models_tamagochi.objects.filter(tam_owner=self.user).aupdate(tam_owner = Userid, tam_money = tam_money)
            await self.send(json.dumps({"tam_income_json" : parameters.tam_income, "tam_money" : tam_money}))

    async def disconnect(self, code):
        print(code)


def calculate_need(need, time, need_decay):

    timenow = datetime.datetime.timestamp(datetime.datetime.now())
    time = datetime.datetime.timestamp(time)
    timenow -= time
    print(timenow)
    if timenow < 10000:
        pass
    else:
        need = need - abs(timenow)//need_decay//200//1000
    print(need)
    if need < 0:
        need = 0
    return need


class class_chat(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if hasattr(self.user, "_wrapped") and self.user._wrapped is None:
            self.user._setup() # Forces loading the actual user
        if not self.user.is_authenticated:
            await self.close()
            return

        self.username = self.user.username
        online_users.add(self.username)

        await self.channel_layer.group_add("global_chat", self.channel_name)
        await self.accept()

        messages = await self.get_messages()
        await self.send(json.dumps({"messages" : messages}))
        await self.broadcast_online_users()


    async def disconnect(self, code):
        online_users.discard(self.username)
        await self.channel_layer.group_discard("global_chat", self.channel_name)
        await self.broadcast_online_users()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get("action") == "send_message":
            message_text = data["message"]
            message = await self.safe_message(self.user, message_text)
            await self.channel_layer.group_send("global_chat", {"type" : "chat_message", "username" : message["author"].username, "message" : message["text"]})
        if data.get("action") == "load_more":
            offset = data.get("offset", 0)
            messages =await self.get_messages(offset=offset)
            await self.send(json.dumps({"messages":messages, "offset":offset+30}))
        
    async def chat_message(self, event):
        await self.send(json.dumps(event))
        
    async def currently_online(self, event):
        await self.send(json.dumps({"online_users": event["users"]}))

    async def broadcast_online_users(self):
        await self.channel_layer.group_send("global_chat", {"type": "currently_online", "users": list(online_users)})

    async def update_users(self, event):
        await self.send(json.dumps({"online_users" : event["users"]}))

    @sync_to_async
    def safe_message(self, user, text):
        message = models_global_chat.objects.create(player = user, message_text = text, message_date = datetime.datetime.now()) 
        return {"author" : message.player, "text" : message.message_text}

    @sync_to_async
    def get_messages(self, offset=0, limit=30):
        total_count = models_global_chat.objects.count()

        start = max(total_count - offset - limit, 0)
        end = total_count - offset
        if start>0 or end>0:
            messages = models_global_chat.objects.order_by("message_date")[start:end]
        else:
            return

        return [
            {"author": msg.player, "text": msg.message_text}
            for msg in messages
        ]


        #message_test = len(list(models_global_chat.objects.order_by("-message_date").all()))
        #if message_test < 31:
        #    messages = models_global_chat.objects.order_by("-message_date")
        #else:
        #    messages = models_global_chat.objects.order_by("-message_date")[message_test-31:]



















        #message_test = len(list(models_global_chat.objects.order_by("-message_date").all()))
        #if message_test < 31:
        #    messages = models_global_chat.objects.order_by("-message_date")
        #else:
        #    messages = models_global_chat.objects.order_by("-message_date")[message_test-31:]
















