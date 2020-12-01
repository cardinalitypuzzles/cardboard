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
                        puzzleData
                    };
                });
            });
    }

    _tableColumns() {
        return [
            {
                Header: "Name",
                accessor: "name",
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
        ];
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
