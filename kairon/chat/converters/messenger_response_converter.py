from kairon.chat.converters.responseconverter import ResponseConverter, ElementTransformerOps
from kairon import Utility


class MessengerResponseConverter(ResponseConverter):

    def __init__(self,message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    def message_extractor(self, json_message, type):
        if type == "image":
            return super().message_extractor(json_message, type)
        if type == "link":
            link_json = ResponseConverter.json_generator(json_message)
            stringbuilder = ""
            for jsonlist in link_json:
                childerobj = jsonlist.get("children")
                stringbuilder = ElementTransformerOps.convertjson_to_link_format(childerobj, stringbuilder, bind_display_str=False)
            body = {"data":stringbuilder}
            return body


    def link_transformer(self, message):
        link_extract = self.message_extractor(message, self.type)
        message_template = ElementTransformerOps.getChannelConfig(self.channel_type, self.message_type)
        if message_template is not None:
            response = ElementTransformerOps.replace_strategy(message_template, link_extract, self.channel_type, self.message_type)
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