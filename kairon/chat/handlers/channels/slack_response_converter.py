import json

from kairon.chat.handlers.channels.responseconverter import ResponseConverter

class SlackMessageConverter(ResponseConverter):

    def __init__(self, message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    # def getChannelConfig(self):
    #     config_obj = super().getChannelConfig()
    #     message_meta = config_obj.get(self.message_type)
    #     return message_meta

    def messageConverter(self, message):
        response = super().messageConverter(message)
        print(f"response in slack {response}")
        return response
        # msg_template = self.getChannelConfig()
        # print(f"messge_templae {msg_template}")
        # if self.message_type == "image":
        #     image_url = message.get("url")
        #     alt_text = message.get("caption")
        #     if None not in (image_url, alt_text):
        #         msg_template = msg_template.replace("<imageurl>", image_url) \
        #                 .replace("<alttext>",alt_text)
        #     else:
        #         msg_template = msg_template.replace("<imageurl>", image_url)
        #     print(f"message tempalate {msg_template}")
        #     return json.loads(msg_template)
        # elif self.message_type == "link":
        #     textdata = message.get("data")
        #     links = message.get("links")
        #     for key in links:
        #         linkobj = links.get(key)
        #         display = linkobj.get("displayText")
        #         url = linkobj.get("URL")
        #         link_formation = "<"+str(url)+"|"+str(display)+">"
        #         #key_mapping.update({key:link_formation})
        #         textdata = str(textdata).replace("<"+str(key)+">", link_formation)
        #     response = msg_template.replace("<data>", textdata)
        #     print(f"key formation {textdata}")
        #     return json.loads(response)
