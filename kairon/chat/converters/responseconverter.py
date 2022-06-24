from abc import ABC, abstractmethod
import json
from kairon import Utility
from loguru import logger
from ...exceptions import AppException

class ElementTransformerOps():
    def __init__(self, type, channel):
        self.type = type
        self.channel = channel

    @staticmethod
    def getChannelConfig(channel, type):
        config_obj = Utility.system_metadata.get(channel)
        if config_obj is not None:
            return config_obj.get(type)
        else:
            message_config = Utility.system_metadata.get("No_Config_error_message")
            message_config = str(message_config).format(channel, type)
            raise Exception(message_config)

    def image_transformer(self, message):
        try:
            message_template = ElementTransformerOps.getChannelConfig(self.channel, self.type)
            op_message = self.message_extractor(message, self.type)
            response = ElementTransformerOps.replace_strategy(message_template, op_message, self.channel, self.type)
            return response
        except Exception as ex:
            raise AppException(f"Exception in Image_transformer: {str(ex)}")

    def link_transformer(self, message):
        try:
            link_extract = self.message_extractor(message, self.type)
            message_template = ElementTransformerOps.getChannelConfig(self.channel, self.type)
            response = ElementTransformerOps.replace_strategy(message_template, link_extract, self.channel, self.type)
            return response
        except Exception as ex:
            raise AppException(f"Exception in Link_Transformer: {str(ex)}")

    @staticmethod
    def json_generator(json_input):
        if isinstance(json_input, dict):
                yield json_input
        elif isinstance(json_input, list):
            for item in json_input:
                yield from ResponseConverter.json_generator(item)

    def message_extractor(self, json_message, type):
        try:
            if type == "image":
                image_json = ResponseConverter.json_generator(json_message)
                body = {}
                for item in image_json:
                    if item.get("type") == "image":
                        body.update({"type": item.get("type"), "URL": item.get("src"),
                                     "caption": item.get("alt")})
                        return  body
            elif type == "link":
                link_json = ResponseConverter.json_generator(json_message)
                stringbuilder = ""
                for jsonlist in link_json:
                    childerobj = jsonlist.get("children")
                    stringbuilder = ElementTransformerOps.convertjson_to_link_format(childerobj, stringbuilder)
                body = {"data":stringbuilder}
                return body
        except Exception as ex:
            raise Exception(f"Exception in message_extraction for channel: {self.channel} "
                            f"and type: {self.type}: - {str(ex)}")

    @staticmethod
    def replace_strategy(message_template, message, channel, type):
        keymapping = Utility.system_metadata.get("channel_messagetype_and_key_mapping")
        if keymapping is not None:
            jsonkey_mapping = json.loads(keymapping)
            channel_meta = jsonkey_mapping.get(channel)
            if channel_meta is not None:
                keydata_mapping = channel_meta.get(type)
                if keydata_mapping is not None:
                    for key in keydata_mapping:
                        value_from_json = message.get(key)
                        replace_in_template = keydata_mapping.get(key)
                        message_template = message_template.replace(replace_in_template, value_from_json)
                    return json.loads(message_template)
                else:
                    message_config = Utility.system_metadata.get("channel_key_mapping_missing")
                    message_config = str(message_config).format(channel, type)
                    raise Exception(message_config)
            else:
                message_config = Utility.system_metadata.get("channel_key_mapping_missing")
                message_config = str(message_config).format(channel, type)
                raise Exception(message_config)

    @staticmethod
    def convertjson_to_link_format(arry_of_json, stringbuilder , bind_display_str = True):
        for items in arry_of_json:
            if items.get("text") is not None and str(items.get("text")).__len__() > 0:
                stringbuilder = " ".join([stringbuilder, str(items.get("text"))])
            elif items.get("type") is not None and items.get("type") == "link":
                link = items.get("href")
                if bind_display_str:
                    displaydata = items.get("children")
                    for displayobj in displaydata:
                        displaystring = displayobj.get("text")
                        link_formation = "<" + str(link) + "|" + str(displaystring) + ">"
                        break
                    stringbuilder = " ".join([stringbuilder, link_formation])
                else:
                    stringbuilder = " ".join([stringbuilder, link])
        return stringbuilder

class ResponseConverter(ABC, ElementTransformerOps):

    @abstractmethod
    def __init__(self, message_type, channel_type):
        self.channel_type = channel_type
        self.message_type = message_type
        ElementTransformerOps.__init__(self, message_type, channel_type)

    def messageConverter(self, message):
        try :
            if self.message_type == "image":
                response = self.image_transformer(message)
                return response
            elif self.message_type == "link":
                response = self.link_transformer(message)
                return response
        except Exception as e:
            logger.error(str(e))
            raise AppException(f'Unable to process message Transformation: {str(e)}')

from kairon.chat.converters.slack_response_converter import SlackMessageConverter
from kairon.chat.converters.hangout_response_converter import HangoutResponseConverter
from kairon.chat.converters.messenger_response_converter import MessengerResponseConverter
from kairon.chat.converters.whatsapp_response_converter import WhatsappResponseConverter
from kairon.chat.converters.telegram_response_converter import TelegramResponseConverter

class ConverterFactory():
    @staticmethod
    def getConcreteInstance(message_type, channel_type):
        if channel_type== "slack":
            return SlackMessageConverter(message_type, channel_type)
        elif channel_type== "hangout":
            return HangoutResponseConverter(message_type, channel_type)
        elif channel_type== "messenger":
            return MessengerResponseConverter(message_type, channel_type)
        elif channel_type== "telegram":
            return TelegramResponseConverter(message_type, channel_type)
        elif channel_type== "whatsapp":
            return WhatsappResponseConverter(message_type, channel_type)