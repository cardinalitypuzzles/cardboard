from django.db import migrations

# A tag belongs to one hunt, and so does a puzzle, but the join table only has
# a foreign key to each -- nothing ties the two hunts together. Expressing that
# as a CHECK isn't possible (no subqueries), so it's a trigger.
FORWARD = """
CREATE OR REPLACE FUNCTION puzzle_tag_same_hunt() RETURNS trigger AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM puzzles_puzzle p, puzzles_puzzletag t
        WHERE p.id = NEW.puzzle_id
          AND t.id = NEW.puzzletag_id
          AND p.hunt_id <> t.hunt_id
    ) THEN
        RAISE EXCEPTION
            'puzzle % and tag % belong to different hunts',
            NEW.puzzle_id, NEW.puzzletag_id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER puzzle_tag_same_hunt
    BEFORE INSERT OR UPDATE ON puzzles_puzzle_tags
    FOR EACH ROW EXECUTE FUNCTION puzzle_tag_same_hunt();
"""

REVERSE = """
DROP TRIGGER IF EXISTS puzzle_tag_same_hunt ON puzzles_puzzle_tags;
DROP FUNCTION IF EXISTS puzzle_tag_same_hunt();
"""


def add_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(FORWARD, params=None)


def drop_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE, params=None)


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0037_remove_puzzletag_unique_tag_names_per_hunt_and_more"),
    ]

    operations = [migrations.RunPython(add_trigger, drop_trigger)]
