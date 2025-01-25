import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";

import { useStore } from "./store";
import type { Hunt } from "./types";

function HuntViewHeader({ hunt }: { hunt: Hunt }) {
  const {
    numPuzzlesUnlocked,
    numPuzzlesSolved,
    numMetasUnlocked,
    numMetasSolved,
  } = useStore((state) => state.puzzlesSlice);

  const driveRedirect = hunt.has_drive ? (
    <OverlayTrigger
      placement="top"
      overlay={
        <Tooltip id="tooltip-right">
          Create your drawings, jamboards, etc here.
        </Tooltip>
      }
    >
      <a href="drive">Google Drive Folder 🎨🖌️📁</a>
    </OverlayTrigger>
  ) : null;

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Container fluid style={{ fontWeight: "bold" }}>
          <Row className="text-center small">
            <Col xs={1} className="text-nowrap px-0 mx-0">
              Metas
            </Col>
            <Col xs={1} className="text-nowrap px-0 mx-0">
              Puzzles
            </Col>
          </Row>
          <Row className="text-center">
            <Col xs={1}>
              <span className="text-primary" style={{ fontSize: "1.25rem" }}>
                {numMetasSolved()}
              </span>{" "}
              / <span className="text-secondary">{numMetasUnlocked()}</span>
            </Col>
            <Col xs={1}>
              <span className="text-success" style={{ fontSize: "1.25rem" }}>
                {numPuzzlesSolved()}
              </span>{" "}
              / <span className="text-secondary">{numPuzzlesUnlocked()}</span>
            </Col>
            <Col xs={1} className="text-nowrap">
              <a href="stats">Stats 📈</a>
            </Col>
            <Col xs={1} className="text-nowrap">
              {driveRedirect}
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
}

export default HuntViewHeader;
