from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope)
        if self.scope["user"].is_anonymous:
            self.close()
        else:
            # Setting the group name as the pk of the user primary key as it is unique to each user. The group name is used to communicate with the user.
            kwargs = self.scope["url_route"]["kwargs"]
            if "hunt_pk" in kwargs:
                self.group_name = kwargs["hunt_pk"]
                async_to_sync(self.channel_layer.group_add)(
                    self.group_name, self.channel_name
                )
                self.accept()
            else:
                self.close()

    def disconnect(self, close_code):
        self.close()

    def notify(self, event):
        self.send(text_data=json.dumps(event["text"]))
