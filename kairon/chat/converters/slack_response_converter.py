from kairon.chat.converters.responseconverter import ResponseConverter

class SlackMessageConverter(ResponseConverter):

    def __init__(self, message_type, channel_type):
        super().__init__(message_type, channel_type)
        self.message_type = message_type
        self.channel_type = channel_type

    def messageConverter(self, message):
        response = super().messageConverter(message)
        return response