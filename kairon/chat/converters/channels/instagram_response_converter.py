from kairon.chat.converters.channels.responseconverter import ResponseConverter


class InstagramResponseConverter(ResponseConverter):
    def __init__(self,message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    def link_transformer(self, message):
        textdata = message.get("data")
        links = message.get("links")
        for key in links:
            linkobj = links.get(key)
            url = linkobj.get("URL")
            link_formation = str(url)
            textdata = str(textdata).replace("<" + str(key) + ">", link_formation)
        formatted_message = {"data": textdata}
        message_template = self.getChannelConfig()
        response = self.replace_strategy(message_template, formatted_message)
        return response

    def messageConverter(self, message):
        if self.message_type == "image":
            response = super().messageConverter(message)
            return response
        elif self.message_type == "link":
            response = self.link_transformer(message)
            return response
        # else:
        #     msg_template = super().getChannelConfig()
        #     print(f"messge_templae {msg_template}")
        #     textdata = message.get("data")
        #     links = message.get("links")
        #     for key in links:
        #         linkobj = links.get(key)
        #         display = linkobj.get("displayText")
        #         url = linkobj.get("URL")
        #         link_formation = str(url)
        #         # key_mapping.update({key:link_formation})
        #         textdata = str(textdata).replace("<" + str(key) + ">", link_formation)
        #     response = msg_template.replace("<data>", textdata)
        #     print(f"key formation {textdata}")
        #     return json.loads(response)