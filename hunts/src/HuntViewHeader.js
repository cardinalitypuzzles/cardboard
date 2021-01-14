import React from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  selectNumUnlocked,
  selectNumSolved,
  selectNumUnsolved,
  selectNumMetasSolved,
  selectNumMetasUnsolved,
} from "./puzzlesSlice";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

function HuntViewHeader({ hunt }) {
  const dispatch = useDispatch();

  const numUnlocked = useSelector(selectNumUnlocked);
  const numSolved = useSelector(selectNumSolved);
  const numUnsolved = useSelector(selectNumUnsolved);
  const numMetasSolved = useSelector(selectNumMetasSolved);
  const numMetasUnsolved = useSelector(selectNumMetasUnsolved);

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-start",
          padding: "2px",
          alignItems: "center",
        }}
      >
        <h1>{hunt.name} - All Puzzles</h1>
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Container fluid>
          <Row className="text-center font-weight-bold small">
            <Col xs={1} className="text-nowrap px-0 mx-0">
              Metas Solved
            </Col>
            <Col xs={1}>Solved</Col>
            <Col xs={1}>Unlocked</Col>
            <Col xs={1}>Unsolved</Col>
            <Col xs={1} className="text-nowrap px-0 mx-0">
              Metas Unsolved
            </Col>
          </Row>
          <Row className="text-center font-weight-bold">
            <Col xs={1} className="text-primary">
              {numMetasSolved}
            </Col>
            <Col xs={1} className="text-success">
              {numSolved}
            </Col>
            <Col xs={1} className="text-secondary">
              {numUnlocked}
            </Col>
            <Col xs={1} className="text-danger">
              {numUnsolved}
            </Col>
            <Col xs={1} className="text-warning">
              {numMetasUnsolved}
            </Col>
            <Col xs={1} className="text-nowrap">
              <a href={"stats"}>Stats 📈</a>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
}

export default HuntViewHeader;
