from abc import ABC, abstractmethod
import json
from kairon import Utility

class ResponseConverter(ABC):

    @abstractmethod
    def __init__(self, message_type, channel_type):
        self.channel_type = channel_type
        self.message_type = message_type

    def messageConverter(self, message):
        msg_template = self.getChannelConfig()
        if self.message_type == "image":
            image_url = message.get("URL")
            alt_text = message.get("caption")
            if None not in (image_url, alt_text):
                msg_template = msg_template.replace("<imageurl>", image_url) \
                    .replace("<alttext>", alt_text)
            else:
                msg_template = msg_template.replace("<imageurl>", image_url)
            return json.loads(msg_template)
        elif self.message_type == "link":
            textdata = message.get("data")
            links = message.get("links")
            for key in links:
                linkobj = links.get(key)
                display = linkobj.get("displayText")
                url = linkobj.get("URL")
                # TODO: displaytext can be empty
                link_formation = "<" + str(url) + "|" + str(display) + ">"
                # key_mapping.update({key:link_formation})
                textdata = str(textdata).replace("<" + str(key) + ">", link_formation)
            response = msg_template.replace("<data>", textdata)
            return json.loads(response)

    def getChannelConfig(self):
        config_obj = Utility.system_metadata.get(self.channel_type)
        message_meta = config_obj.get(self.message_type)
        return message_meta