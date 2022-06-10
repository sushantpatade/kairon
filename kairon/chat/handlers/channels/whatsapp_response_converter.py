from kairon.chat.handlers.channels.responseconverter import ResponseConverter
import json

class WhatsappResponseConverter(ResponseConverter):

    def __init__(self, message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    def messageConverter(self, message):
        if self.message_type == "image":
            response = super().messageConverter(message)
            return response
        else:
            msg_template = super().getChannelConfig()
            print(f"messge_templae {msg_template}")
            textdata = message.get("data")
            links = message.get("links")
            for key in links:
                linkobj = links.get(key)
                display = linkobj.get("displayText")
                url = linkobj.get("URL")
                link_formation = str(url)
                # key_mapping.update({key:link_formation})
                textdata = str(textdata).replace("<" + str(key) + ">", link_formation)
            response = msg_template.replace("<data>", textdata)
            print(f"key formation {textdata}")
            return json.loads(response)

        print(f"response in slack {response}")
        return response
