from .service import ChatService


class FakeChatService(ChatService):
    def __init__(self, django_settings):
        self.text_channels = set()
        self.audio_channels = set()
        self.archived_channels = set()
        self.messages = set()

    def create_text_channel(self, guild_id, name, *args, **kwargs):
        self.text_channels.add(name)
        return name

    def create_audio_channel(self, guild_id, name, *args, **kwargs):
        self.audio_channels.add(name)
        return name

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

    def create_channel_url(self, guild_id, channel_id, is_audio=False):
        return ""

    def send_message(self, channel_id, msg, embedded_urls={}):
        self.messages.add(msg)
