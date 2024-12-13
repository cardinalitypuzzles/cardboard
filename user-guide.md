## Cardboard User Guide

### Overview

![overview](https://github.com/user-attachments/assets/abf92304-f3af-43f9-b914-ce7beff09a04)

The default page you see is a list of all puzzles in a table. The puzzle name is a link to the puzzle page on the hunt website. The puzzles are grouped by meta, and each puzzle has a Google spreadsheet associated with it.

In case you need to edit the puzzle name, URL, or meta status, you can use the pencil icon next to the puzzle name. Use the trash icon to delete a puzzle.

The default status of a new puzzle is SOLVING. To submit a guess for a puzzle, click the "Submit Answer" button for that puzzle. By default, once a guess has been submitted, the puzzle status will be changed to SOLVED and the row will be highlighted in green. Note that this does not actually submit the answer on the hunt website and you will need to submit there separately.

If the answer queue is turned on, then the status is instead PENDING and the row will be highlighted in yellow. A dedicated person monitoring the "Answer Queue" page should be responsible for submitting the answers on the hunt website and reporting back whether the answer was correct or not.

In addition, you can set a puzzle's status to STUCK or EXTRACTION using the "Status" column dropdown to indicate that the solvers are stuck on the puzzle or the puzzle just needs a final extraction to get an answer.

Users can also tag puzzles as belonging to one or more metas, mark puzzles as high priority or low priority, logic or word puzzles, backsolved, or create new tags by clicking the "+" icon in the "Tags" column.

<img src='https://user-images.githubusercontent.com/1312469/147149416-29dda7c5-bde5-4277-8866-9b9954980bcd.png' width='300'>

Clicking the "x" icon next to an existing tag will remove it from the puzzle.

There is also a static "Tools and References" page linked on the navigation bar at the top that includes links to useful puzzle tools and resources.

### Login

You login to Cardboard using a Google account. If you get an error message like

![login-error](https://user-images.githubusercontent.com/544734/71759638-0ef64900-2e7e-11ea-8362-73f789085547.png)

then you should contact an admin and ask them to add you to the Google Drive hunt folder. For more details, see the [hunt setup guide](new-hunt-setup.md#giving-a-new-user-access-to-cardboard).

### Adding and modifying puzzles

Any user can add a new puzzle by using the blue "Add New Puzzle" button in the top right.

<img src='https://user-images.githubusercontent.com/544734/71759777-3cdc8d00-2e80-11ea-9d49-48de77370976.png' width='300'>

You must specify a name but the URL is optional. If you know the puzzle is a meta puzzle, you can check the "Meta?" checkbox. In case you made a mistake or realize a puzzle is a meta later on, you can always go back and edit a puzzle by pressing the pencil icon next to the puzzle name.

In case you need to delete a puzzle (perhaps you accidentally created a duplicate), you can do so using the trash icon next to a puzzle name.

When a puzzle is created, a Google Spreadsheet is automatically created for the puzzle. These are linked from the Sheets icon.

### Searching

As a hunt progresses, the number of puzzles can get quite large (especially for a hunt like the MIT Mystery Hunt). To make things more manageable, you can use the "Search" box in the top-right to filter puzzles. The search matches puzzle name, answer, status, or tags. For example, the following shows filtering to just the puzzles that need extraction:

![extraction](https://user-images.githubusercontent.com/1312469/209478179-85516d11-9701-4cc5-b608-f5691cab1d5c.png)

### Metas and Tags

When adding a new puzzle, if you know it's a meta, you can mark it as such by checking the "Meta?" checkbox. This will automatically create a tag with the same name as the meta puzzle. You can then assign other puzzles as belonging to this meta by using the "Assign Metas" button for a puzzle or adding the meta puzzle tag using the "+" icon in the "Tags" column for a puzzle.

The main puzzles page is grouped by metas, with puzzles belonging to a meta indented underneath the meta. Each puzzle may belong to multiple metas, in which case it will appear multiple times, once under each meta it belongs to.

Meta puzzles may also be assigned to other metas (which might be meta-metas).

In addition to meta tags for puzzles, users can also tag puzzles as high or low priority, logic or word puzzles, or create new tags.

### Google Sheets integration

When a puzzle is added, a Google Sheet is automatically created for it, linked from the Sheet icon. The puzzle sheet is a clone of a template sheet, which may have some useful formulas pre-populated. Ownership of the puzzle sheets is transferred to the owner of the the template sheet - search `pendingowner:me` to see and accept the transfers.

### Tools and References

![tools](https://user-images.githubusercontent.com/1312469/209479516-9d2195d3-40b0-40d2-be35-11fccce7ef01.png)

A static list of tools and references is collected on the "Tools and References" page. You can add more by editing the [tools.html](hunts/templates/tools.html) page.
