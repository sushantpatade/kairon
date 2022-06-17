from kairon.chat.converters.responseconverter import ResponseConverter
from kairon import Utility

class WhatsappResponseConverter(ResponseConverter):

    def __init__(self, message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    def message_extractor(self, json_message, type):
        if type == "image":
            return super().message_extractor(json_message, type)
        if type == "link":
            link_json = ResponseConverter.json_generator(json_message, "children", type)
            stringbuilder = ""
            for jsonlist in link_json:
                childerobj = jsonlist.get("children")
                for items in childerobj:
                    if items.get("text") is not None and str(items.get("text")).__len__() > 0:
                        stringbuilder = " ".join([stringbuilder, str(items.get("text"))])
                    elif items.get("type") is not None and items.get("type") == "link":
                        link = items.get("href")
                        stringbuilder = " ".join([stringbuilder, link])
            body = {"data": stringbuilder}
            return body

    def link_transformer(self, message):
        link_extract = self.message_extractor(message, self.type)
        message_template = self.getChannelConfig()
        if message_template is not None:
            response = self.replace_strategy(message_template, link_extract)
            return response
        else:
            message_config = Utility.system_metadata.get("No_Config_error_message")
            message_config = str(message_config).format(self.channel, self.type)
            raise Exception(message_config)

    def messageConverter(self, message):
        if self.message_type == "image":
            response = super().messageConverter(message)
            return response
        elif self.message_type == "link":
            response = self.link_transformer(message)
            return response