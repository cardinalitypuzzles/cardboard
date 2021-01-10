import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

function HuntViewHeader({
  hunt,
  numMetasSolved,
  numSolved,
  numUnsolved,
  numUnlocked,
}) {
  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "2px",
          alignItems: "center",
        }}
      >
        <h1>{hunt.name} - All Puzzles</h1>
        <a href={"stats"}>Hunt Statistics</a>
      </div>
      <Container fluid>
        <Row className="text-center font-weight-bold small">
          <Col xs={1} className="text-nowrap">
            Metas Solved
          </Col>
          <Col xs={1}>Solved</Col>
          <Col xs={1}>Unsolved</Col>
          <Col xs={1}>Unlocked</Col>
        </Row>
        <Row className="text-center font-weight-bold">
          <Col xs={1} className="text-primary">
            {numMetasSolved}
          </Col>
          <Col xs={1} className="text-success">
            {numSolved}
          </Col>
          <Col xs={1} className="text-danger">
            {numUnsolved}
          </Col>
          <Col xs={1} className="text-secondary">
            {numUnlocked}
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default HuntViewHeader;
