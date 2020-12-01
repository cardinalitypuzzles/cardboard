import React from "react";
import PropTypes from "prop-types";
import { PuzzleTable} from "./puzzle-table.js";

export class HuntViewMain extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            puzzleData: [],
        };
        this.columns = this._tableColumns();
    }

    componentDidMount() {
        const huntApiUrl = `/api/v1/hunt/${this.props.huntId}`;
        const puzzlesApiUrl = `/api/v1/hunt/${this.props.huntId}/puzzles`;
        fetch(huntApiUrl)
            .then(response => {
                if (response.status > 400) {
                    //TODO: Some error handling should go here
                    console.error("Hunt API failure", response);
                }
                return response.json();
            })
            .then(huntData => {
                this.setState(() => {
                    return {
                        huntData
                    };
                });
            });

        fetch(puzzlesApiUrl)
            .then(response => {
                if (response.status > 400) {
                    // TODO: error handling
                    console.error("Puzzles API failure", response);
                }
                return response.json();
            })
            .then(puzzleData => {
                this.setState(() => {
                    return {
                        puzzleData: this._processPuzzleData(puzzleData),
                    };
                });
            });
    }

    _tableColumns() {
        return [
            {
                Header: "id",
                accessor: "id",
            },
            {
                Header: "Name",
                accessor: "name",
                Cell: ({ row, value }) =>
                    row.canExpand ? (
                        <span
                            {...row.getToggleRowExpandedProps({
                                style: {
                                    paddingLeft: `${row.depth * 2}rem`,
                                },
                            })}
                        >
                            {row.isExpanded ? '▼' : '▶'} {value}
                            </span>
                    ) : (
                        <span
                            style={{paddingLeft: `${row.depth * 2}rem`}}>
                            {value}
                            </span>
                    ),
            },
            {
                Header: "Answer",
                accessor: "answer",
            },
            {
                Header: "Status",
                accessor: "status",
            },
            {
                Header: "Sheet",
                accessor: "sheet",
            },
            {
                Header: "Tags",
                id: "tags",
            },
            {
                Header: "Metas",
                accessor: "metas",
            },
            {
                Header: "Feeders",
                accessor: "feeders",
            },
        ];
    }

    _puzzleComparator(a, b) {
        // Solved puzzles should appear below unsolved ones
        if (a.status == "SOLVED" && b.status != "SOLVED") {
            return 1;
        } else if (b.status == "SOLVED" && a.status != "SOLVED") {
            return -1;
        }
        // Feeders before metas
        if (a.feeders.length == 0 && b.feeders.length > 0) {
            return -1;
        } else if (a.feeders.length > 0 && b.feeders.length == 0) {
            return 1;
        }
        // Newer puzzles before old ones
        // TODO: once creation times are added to puzzles, use those instead
        return b.id - a.id;
    }

    _processPuzzleData(puzzleData) {
        const rowMap = {};
        puzzleData.forEach(row => {
           rowMap[row.id] = row;
        });
        puzzleData.forEach(row => {
            if (row.feeders.length > 0) {
                row.subRows = [];
                row.feeders.forEach(subRowId => {
                    row.subRows.push(rowMap[subRowId]);
                });
            }
        });
        puzzleData.forEach(row => {
            if (row.subRows) {
                row.subRows.sort(this._puzzleComparator);
            }
        });
        const rows = Object.values(rowMap).filter(row => row.metas.length == 0);
        rows.sort(this._puzzleComparator);
        return rows;
    }

    render() {
        if (this.state.huntData) {
            return (
            <div>
                <h1>{this.state.huntData.name} - All Puzzles</h1>
                <PuzzleTable columns={this.columns} data={this.state.puzzleData} />
            </div>
            );
        } else {
            return <h1>Loading...</h1>;
        }
    }
}

HuntViewMain.propTypes = {
    huntId: PropTypes.string.isRequired,
};
