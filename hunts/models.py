from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from guardian.shortcuts import get_users_with_perms


class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=None, blank=True, null=True)
    end_time = models.DateTimeField(default=None, blank=True, null=True)
    last_active_users_update_time = models.DateTimeField(
        default=None, blank=True, null=True
    )

    puzzlers = models.ManyToManyField(
        get_user_model(), related_name="hunts", blank=True
    )
    active = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, unique=True)

    class Meta:
        permissions = (
            ("hunt_admin", "Hunt admin"),
            ("hunt_access", "Hunt access"),
        )

    def get_hunt(self):
        """The hunt this object belongs to."""
        return self

    def __str__(self):
        return self.name

    def _available_slug(self):
        """Two hunts may share a name, so the slug gets a numeric suffix."""
        limit = self._meta.get_field("slug").max_length
        base = slugify(self.name)[:limit] or "hunt"
        slug, n = base, 2
        while Hunt.objects.filter(slug=slug).exists():
            suffix = f"-{n}"
            slug = base[: limit - len(suffix)] + suffix
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._available_slug()
        super().save(*args, **kwargs)
        if not hasattr(self, "settings"):
            HuntSettings.objects.create(hunt=self)

    @staticmethod
    def get_object_or_404(user=None, **kwargs):
        hunt = get_object_or_404(Hunt, **kwargs)
        if user and user.is_authenticated and user.last_accessed_hunt != hunt:
            user.last_accessed_hunt = hunt
            user.save(update_fields=["last_accessed_hunt"])
        return hunt

    # Gets a RawQuerySet of puzzles that are either solved or only feed into solved metas.
    def get_progression_puzzles(self):
        query = """
        WITH RECURSIVE progression_puzzles (id) AS (
            SELECT id
            FROM puzzles_puzzle
            WHERE (status = 'SOLVED' AND hunt_id = %s)
            UNION
            SELECT Metas.from_puzzle_id
            FROM puzzles_puzzle_metas Metas
            INNER JOIN progression_puzzles ON progression_puzzles.id = Metas.to_puzzle_id
        )
        SELECT * FROM puzzles_puzzle WHERE id IN (SELECT id FROM progression_puzzles)
        """
        return Hunt.objects.raw(query, [str(self.pk)])

    def get_users_with_perm(self, perm):
        users_perms = get_users_with_perms(self, attach_perms=True)
        result = []
        for user, perms in users_perms.items():
            if perm in perms:
                result.append(user)

        return result


class HuntSettings(models.Model):
    hunt = models.OneToOneField(
        Hunt,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    answer_queue_enabled = models.BooleanField(
        default=False,
        help_text="Toggles whether submitted answers go to an answer queue for review instead of immediately marking puzzles solved.",
    )

    #
    # Google-specific settings
    #

    # The id of your Google Drive folder
    # This should be part of the URL (https://drive.google.com/drive/folders/<folder_id>)
    # This folder is used for login permissions and for puzzle storage.
    # This is where puzzle files will be kept, so it should not be modified by humans
    google_drive_folder_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Google Drive folder",
        help_text="The ID or URL of the Google Drive folder where spreadsheets will be stored.",
    )

    # The id of your Google Sheets template file
    # This should be part of the url (https://docs.google.com/spreadsheets/d/<sheet_id>)
    google_sheets_template_file_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Google Sheets template",
        help_text="The ID or URL of your Google Sheets template file.",
    )

    # The id of a Google Drive folder where template files for this hunt can be found
    # Used as a way to get around #372
    # Cardboard will try to use one of the files in here if possible, before making a copy
    # of the master sheet.
    # TODO: Figure out a better solution to this longer-term, like getting Drive permission on sign-in
    # and using those instead of the service account, or using an add-on somehow
    google_sheets_template_folder_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Google Sheets template folder ID",
        help_text=(
            "the ID of a Google Drive folder where extra Sheet templates can be found. "
            "If this folder is not empty, Cardboard will rename and move one of these sheets "
            "when a new puzzle is created, instead of copying the template file. This maybe be "
            "useful because of #372, where scripts in Google sheets will stop working on new "
            "sheets if you create too many in one day. This way you can create sheets in advance "
            "to get around the daily limits."
        ),
    )

    # A link to the Google Drive folder that solvers can use for misc. files
    google_drive_human_url = models.URLField(
        blank=True,
        verbose_name="Google Drive Human URL",
        help_text=(
            "the URL of a Google Drive folder where human-generated files can be uploaded. "
            "This folder is linked at the top of Cardboard. If this value is not set, "
            "there will not be a link to the folder."
        ),
    )

    #
    # Discord-specific settings
    #
    create_channel_by_default = models.BooleanField(
        default=True,
        help_text="Toggles whether puzzles should have chat channels created by default",
    )

    discord_guild_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Discord guild ID",
        help_text='The id of your Discord server. This can be found on the "Widget" page in the Server Settings',
    )

    discord_puzzle_announcements_channel_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Discord announcements channel ID",
        help_text="""The id of the Discord channel to make puzzle announcements in.
        This channel can get noisy and is recommended to be its own separate channel.
        This ID can be found by enabling Developer Mode in Discord and right-clicking on the channel""",
    )

    discord_metas_category = models.CharField(
        max_length=128,
        default="metas",
        blank=True,
        help_text="The category name to create all metas in",
    )

    discord_unassigned_text_category = models.CharField(
        max_length=128,
        default="text [unassigned]",
        blank=True,
        help_text="The category name to create all unassigned Discord text channels in",
    )

    discord_unassigned_voice_category = models.CharField(
        max_length=128,
        default="voice [unassigned]",
        blank=True,
        help_text="The category name to create all unassigned Discord voice channels in",
    )

    discord_archive_category = models.CharField(
        max_length=128,
        default="archive",
        blank=True,
        help_text="The category name to archive all Discord channels for solved puzzles in",
    )

    discord_devs_role = models.CharField(
        max_length=128,
        default="dev",
        blank=True,
        help_text="The Discord role for the people maintaining the Cardboard instance, in case of problems",
    )

    active_user_lookback = models.DurationField(
        default=timedelta(minutes=10),
        verbose_name="Active user lookback (s)",
        help_text="A user is considered active on a puzzle if they've interacted with it within this duration.",
    )
