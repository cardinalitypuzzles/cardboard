## Small Board User Guide

This guide gives an overview of how to use Small Board for a hunt (which should be set up by an admin) and its features.


### Overview

![overview](https://user-images.githubusercontent.com/544734/71759676-6a283b80-2e7e-11ea-82d0-f2f4fc737c71.png)

The default page you see is a list of all puzzles in a table. The puzzle name is a link to the puzzle page on the hunt website. The puzzles are grouped by meta, and each puzzle has a Google spreadsheet ("Sheet" column) and Slack channel ("Slack" column) associated with it.

In case you need to edit the puzzle name, URL, or meta status, you can use the pencil icon next to the puzzle name. Use the trash icon to delete a puzzle.

To submit a guess for a puzzle, click the "Submit Answer" button for that puzzle. Once a guess has been submitted, the puzzle status will be changed to PENDING and the row will be highlighted in yellow. Note that this does not actually submit the answer on the hunt website. A dedicated person monitoring the "Answer Queue" page should be responsible for submitting the answers on the hunt website and reporting back whether the answer was correct or not.

The default status of a new puzzle is SOLVING. When an answer is submitted, the status automatically changes to PENDING, and when a puzzle is solved (an answer is confirmed to be correct), the status changes to SOLVED. In addition, you can set a puzzle's status to STUCK or EXTRACTION by using the pencil icon in the "Status" column to indicate that the solvers are stuck on the puzzle or the puzzle just needs a final extraction to get an answer.

Users can also tag puzzles as belonging to one or more metas, mark puzzles as high priority or low priority, logic or word puzzles, backsolved, or create new tags.

<img src='https://user-images.githubusercontent.com/544734/71759748-cfc8f780-2e7f-11ea-948d-1d0f32593089.png' width='200'>


### Login

You login to Small Board using a Google account. If you get an error message like

![login-error](https://user-images.githubusercontent.com/544734/71759638-0ef64900-2e7e-11ea-8362-73f789085547.png)

then you should contact an admin and ask them to add you to the Google Drive hunt folder (and invite you to the Slack workspace).


### Adding and modifying puzzles

Any user can add a new puzzle by using the blue "Add New Puzzle" button in the top right.

![add-puzzle](https://user-images.githubusercontent.com/544734/71759777-3cdc8d00-2e80-11ea-9d49-48de77370976.png)

You must specify a name but the URL is optional. If you know the puzzle is a meta puzzle, you can check the "Meta?" checkbox. In case you made a mistake or realize a puzzle is a meta later on, you can always go back and edit a puzzle by pressing the pencil icon next to the puzzle name.

In case you need to delete a puzzle (perhaps you accidentally created a duplicate), you can do so using the trash icon next to a puzzle name.


### Searching

As a hunt progresses, the number of puzzles can get quite large (especially for a hunt like the MIT Mystery Hunt). To make things more manageable, you can use the "Search" box in the top-right to filter puzzles. The search matches puzzle name, answer, status, or tags. For example, the following shows filtering to just the puzzles that need extraction:

![extraction](https://user-images.githubusercontent.com/544734/71759824-38fd3a80-2e81-11ea-8670-d0a1039f6502.png)



- answer submission and verification

- metas and tags

- Slack integration

- tools and references