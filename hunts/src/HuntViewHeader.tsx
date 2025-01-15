import React from "react";
import { useSelector } from "react-redux";
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
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";

import type { Hunt } from "./types";

function HuntViewHeader({ hunt }: { hunt: Hunt }) {
  const numUnlocked = useSelector(selectNumUnlocked);
  const numSolved = useSelector(selectNumSolved);
  const numMetasSolved = useSelector(selectNumMetasSolved);
  const numMetasUnsolved = useSelector(selectNumMetasUnsolved);
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
              <span
                className="text-primary"
                style={{ fontSize: "1.25rem" }}
              >
                {numMetasSolved}
              </span>{" "}
              /{" "}
              <span className="text-secondary">
                {numMetasSolved + numMetasUnsolved}
              </span>
            </Col>
            <Col xs={1}>
              <span
                className="text-success"
                style={{ fontSize: "1.25rem" }}
              >
                {numSolved}
              </span>{" "}
              /{" "}
              <span className="text-secondary">
                {numUnlocked}
              </span>
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
