from abc import ABC, abstractmethod
import json
from kairon import Utility
from loguru import logger
from ...exceptions import AppException

class ElementTransformer():
    def __init__(self, type, channel):
        self.type = type
        self.channel = channel

    def getChannelConfig(self):
        config_obj = Utility.system_metadata.get(self.channel)
        message_meta = config_obj.get(self.type)
        return message_meta

    def image_transformer(self, message):
        message_template = self.getChannelConfig()
        if message_template is not None:
            op_message = self.message_extractor(message, self.type)
            response = self.replace_strategy(message_template, op_message)
            return response
        else:
            message_config = Utility.system_metadata.get("No_Config_error_message")
            message_config = str(message_config).format(self.channel, self.type)
            raise Exception(message_config)

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

    @staticmethod
    def json_generator( json_input, lookup_key, value):
        if isinstance(json_input, dict):
                yield json_input
        elif isinstance(json_input, list):
            for item in json_input:
                yield from ResponseConverter.json_generator(item, lookup_key, value)

    def message_extractor(self, json_message, type):
        if type == "image":
            image_json = ResponseConverter.json_generator(json_message, "type", type)
            body = {}
            for item in image_json:
                if item.get("type") == "image":
                    body.update({"type": item.get("type"), "URL": item.get("src"),
                                 "caption": item.get("alt")})
                    return  body
        elif type == "link":
            link_json = ResponseConverter.json_generator(json_message, "children", type)
            stringbuilder = ""
            for jsonlist in link_json:
                childerobj = jsonlist.get("children")
                for items in childerobj:
                    if items.get("text") is not None and str(items.get("text")).__len__() > 0:
                        stringbuilder = " ".join([stringbuilder, str(items.get("text"))])
                    elif items.get("type") is not None and items.get("type") == "link":
                        link = items.get("href")
                        displaydata = items.get("children")
                        for displayobj in displaydata:
                            displaystring = displayobj.get("text")
                            link_formation = "<" + str(link) + "|" + str(displaystring) + ">"
                        stringbuilder = " ".join([stringbuilder, link_formation])
            body = {"data":stringbuilder}
            return body


    def replace_strategy(self, message_template, message):
        replacekeys = {"slack": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                 "link": {"data": "<data>"}},
                       "messenger": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                 "link": {"data": "<data>"} } ,
                       "hangout": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                     "link": {"data": "<data>"}},
                       "telegram": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                   "link": {"data": "<data>"}},
                       "whatsapp": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                     "link": {"data": "<data>"}},
                       "instagram": {"image": {"URL": "<imageurl>", "caption": "<alttext>"},
                                    "link": {"data": "<data>"}}
                                     }
        # TODO : if replacekey config is missing
        channel_meta = replacekeys.get(self.channel).get(self.type)
        for key in channel_meta:
            value_from_json = message.get(key)
            replace_in_template = channel_meta.get(key)
            message_template = message_template.replace(replace_in_template, value_from_json)
        return json.loads(message_template)

class ResponseConverter(ABC, ElementTransformer):

    @abstractmethod
    def __init__(self, message_type, channel_type):
        self.channel_type = channel_type
        self.message_type = message_type
        ElementTransformer.__init__(self, message_type, channel_type)

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