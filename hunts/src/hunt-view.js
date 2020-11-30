import React from "react";
import PropTypes from "prop-types";

export class HuntViewMain extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        const huntApiUrl = `/api/v1/hunt/${this.props.huntId}`;
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
    }

    render() {
        if (this.state.huntData) {
            return <h1>{this.state.huntData.name}</h1>;
        } else {
            return <h1>Hello world!</h1>;
        }
    }
}

HuntViewMain.propTypes = {
    huntId: PropTypes.string.isRequired,
};
