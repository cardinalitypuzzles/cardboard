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
import {
  SafeCol,
  SafeContainer,
  SafeOverlayTrigger,
  SafeRow,
  SafeTooltip,
} from "./types";

function HuntViewHeader({ hunt }: { hunt: Hunt }) {
  const numUnlocked = useSelector(selectNumUnlocked);
  const numSolved = useSelector(selectNumSolved);
  const numMetasSolved = useSelector(selectNumMetasSolved);
  const numMetasUnsolved = useSelector(selectNumMetasUnsolved);
  const driveRedirect = hunt.has_drive ? (
    <SafeOverlayTrigger
      placement="top"
      overlay={
        <SafeTooltip id="tooltip-right">
          Create your drawings, jamboards, etc here.
        </SafeTooltip>
      }
    >
      <a href="drive">Google Drive Folder 🎨🖌️📁</a>
    </SafeOverlayTrigger>
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
        <SafeContainer fluid>
          <SafeRow className="text-center font-weight-bold small">
            <SafeCol xs={1} className="text-nowrap px-0 mx-0">
              Metas
            </SafeCol>
            <SafeCol xs={1} className="text-nowrap px-0 mx-0">
              Puzzles
            </SafeCol>
          </SafeRow>
          <SafeRow className="text-center">
            <SafeCol xs={1}>
              <span
                className="text-primary font-weight-bold"
                style={{ fontSize: "1.25rem" }}
              >
                {numMetasSolved}
              </span>{" "}
              /{" "}
              <span className="text-secondary font-weight-bold">
                {numMetasSolved + numMetasUnsolved}
              </span>
            </SafeCol>
            <SafeCol xs={1}>
              <span
                className="text-success font-weight-bold"
                style={{ fontSize: "1.25rem" }}
              >
                {numSolved}
              </span>{" "}
              /{" "}
              <span className="text-secondary font-weight-bold">
                {numUnlocked}
              </span>
            </SafeCol>
            <SafeCol xs={1} className="text-nowrap">
              <a href="stats">Stats 📈</a>
            </SafeCol>
            <SafeCol xs={1} className="text-nowrap">
              {driveRedirect}
            </SafeCol>
          </SafeRow>
        </SafeContainer>
      </div>
    </div>
  );
}

export default HuntViewHeader;
