from .service import ChatService


class FakeChatService(ChatService):
    def __init__(self, django_settings):
        self.text_channels = set()
        self.audio_channels = set()
        self.archived_channels = set()
        self.category_to_channel = dict()
        self.messages = set()

    def create_text_channel(self, guild_id, name, *args, **kwargs):
        channel_id = name + "-text"
        self.text_channels.add(channel_id)
        return channel_id

    def create_audio_channel(self, guild_id, name, *args, **kwargs):
        channel_id = name + "-audio"
        self.audio_channels.add(channel_id)
        return channel_id

    def delete_text_channel(self, guild_id, channel_id):
        self.text_channels.remove(channel_id)

    def delete_audio_channel(self, guild_id, channel_id):
        self.audio_channels.remove(channel_id)

    def archive_channel(self, guild_id, channel_id, *args, **kwargs):
        self.archived_channels.add(channel_id)

    def unarchive_text_channel(self, guild_id, channel_id, *args, **kwargs):
        if channel_id in self.archived_channels:
            self.archived_channels.remove(channel_id)

    def unarchive_voice_channel(self, guild_id, channel_id, *args, **kwargs):
        if channel_id in self.archived_channels:
            self.archived_channels.remove(channel_id)

    def categorize_channel(self, guild_id, channel_id, category_name):
        if channel_id in self.archived_channels:
            self.archived_channels.remove(channel_id)

        for category in self.category_to_channel.keys():
            if (
                category != category_name
                and channel_id in self.category_to_channel[category]
            ):
                self.category_to_channel[category].remove(channel_id)

        if category_name not in self.category_to_channel:
            self.category_to_channel[category_name] = set()

        self.category_to_channel[category_name].add(channel_id)

    def create_channel_url(self, guild_id, channel_id, is_audio=False):
        return ""

    def send_message(self, channel_id, msg, embedded_urls={}):
        self.messages.add(msg)
