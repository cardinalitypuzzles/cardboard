## Small Board

This guide gives an overview of how to use Small Board and its features.

For instructions on how to set up an existing deployment for a new hunt, see this [new hunt setup guide](new-hunt-setup.md).

For development instructions, see the [dev guide](dev-guide.md).


### Overview

![overview](https://user-images.githubusercontent.com/544734/71759676-6a283b80-2e7e-11ea-82d0-f2f4fc737c71.png)

The default page you see is a list of all puzzles in a table. The puzzle name is a link to the puzzle page on the hunt website. The puzzles are grouped by meta, and each puzzle has a Google spreadsheet ("Sheet" column) associated with it.

In case you need to edit the puzzle name, URL, or meta status, you can use the pencil icon next to the puzzle name. Use the trash icon to delete a puzzle.

To submit a guess for a puzzle, click the "Submit Answer" button for that puzzle. Once a guess has been submitted, the puzzle status will be changed to PENDING and the row will be highlighted in yellow. Note that this does not actually submit the answer on the hunt website. A dedicated person monitoring the "Answer Queue" page should be responsible for submitting the answers on the hunt website and reporting back whether the answer was correct or not.

The default status of a new puzzle is SOLVING. When an answer is submitted, the status automatically changes to PENDING, and when a puzzle is solved (an answer is confirmed to be correct), the status changes to SOLVED. In addition, you can set a puzzle's status to STUCK or EXTRACTION by using the pencil icon in the "Status" column to indicate that the solvers are stuck on the puzzle or the puzzle just needs a final extraction to get an answer.

Users can also tag puzzles as belonging to one or more metas, mark puzzles as high priority or low priority, logic or word puzzles, backsolved, or create new tags by clicking the "+" icon in the "Tags" column.

<img src='https://user-images.githubusercontent.com/544734/71759748-cfc8f780-2e7f-11ea-948d-1d0f32593089.png' width='300'>

Clicking the "x" icon next to an existing tag will remove it from the puzzle.

There is also a static "Tools and References" page linked on the navigation bar at the top that includes links to useful puzzle tools and resources.


### Login

You login to Small Board using a Google account. If you get an error message like

![login-error](https://user-images.githubusercontent.com/544734/71759638-0ef64900-2e7e-11ea-8362-73f789085547.png)

then you should contact an admin and ask them to add you to the Google Drive hunt folder. For more details, see the [hunt setup guide](new-hunt-setup.md#giving-a-new-user-access-to-small-board).


### Adding and modifying puzzles

Any user can add a new puzzle by using the blue "Add New Puzzle" button in the top right.

<img src='https://user-images.githubusercontent.com/544734/71759777-3cdc8d00-2e80-11ea-9d49-48de77370976.png' width='300'>

You must specify a name but the URL is optional. If you know the puzzle is a meta puzzle, you can check the "Meta?" checkbox. In case you made a mistake or realize a puzzle is a meta later on, you can always go back and edit a puzzle by pressing the pencil icon next to the puzzle name.

In case you need to delete a puzzle (perhaps you accidentally created a duplicate), you can do so using the trash icon next to a puzzle name.

When a puzzle is created, a Google Spreadsheet are automatically created for the puzzle. These are accessible from the links in the "Sheet" column.


### Searching

As a hunt progresses, the number of puzzles can get quite large (especially for a hunt like the MIT Mystery Hunt). To make things more manageable, you can use the "Search" box in the top-right to filter puzzles. The search matches puzzle name, answer, status, or tags. For example, the following shows filtering to just the puzzles that need extraction:

![extraction](https://user-images.githubusercontent.com/544734/71759824-38fd3a80-2e81-11ea-8670-d0a1039f6502.png)


### Metas and Tags

When adding a new puzzle, if you know it's a meta, you can mark it as such by checking the "Meta?" checkbox. This will automatically create a tag with the same name as the meta puzzle. You can then assign other puzzles as belonging to this meta by using the "Assign Metas" button for a puzzle or adding the meta puzzle tag using the "+" icon in the "Tags" column for a puzzle.

The main puzzles page is grouped by metas, with puzzles belonging to a meta indented underneath the meta. Each puzzle may belong to multiple metas, in which case it will appear multiple times, once under each meta it belongs to.

Meta puzzles may also be assigned to other metas (which might be meta-metas).

In addition to meta tags for puzzles, users can also tag puzzles as high or low priority, logic or word puzzles, or create new tags.


### Google Sheets integration

When a puzzle is added, a Google Sheet is automatically created for it, accessible from the link under the "Sheet" column. The puzzle sheet is a clone of a template sheet, which may have some useful formulas pre-populated.


### Tools and References

![tools](https://user-images.githubusercontent.com/544734/71760134-8def7f80-2e86-11ea-82cf-b6b8e906ebf7.png)

A static list of tools and references is collected on the "Tools and References" page. You can add more by editing the [tools.html](hunts/templates/tools.html) page.
