import React from "react";
import Badge from "react-bootstrap/Badge";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import BootstrapTooltip from "react-bootstrap/Tooltip";
import Drawer from "react-modern-drawer";
import ReactTimeAgo from "react-time-ago";
import { useTranslation } from "react-i18next";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useStore } from "./store";
import type { Puzzle, PuzzleId } from "./types";
import { getPuzzleRoundColor } from "./utils";

interface SolveEvent {
  id: PuzzleId;
  name: string;
  isMeta: boolean;
  color: string;
  solvedMs: number;
}

interface ChartPoint {
  time: number;
  unlocked: number;
  solved: number;
  solveEvent?: SolveEvent;
}

interface SolvedPuzzleEntry {
  puzzle: Puzzle;
  solvedMs: number;
  color: string;
}

function getSolvedTimeMs(puzzle: Puzzle): number | null {
  if (
    puzzle.status !== "SOLVED" ||
    !puzzle.guesses ||
    puzzle.guesses.length === 0
  ) {
    return null;
  }
  let latest: number | null = null;
  for (const guess of puzzle.guesses) {
    if (!guess.created_on) {
      continue;
    }
    const ms = Date.parse(guess.created_on);
    if (!Number.isNaN(ms) && (latest === null || ms > latest)) {
      latest = ms;
    }
  }
  return latest;
}

function formatSolveTimestamp(ms: number, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(ms));
}

function formatAxisTick(ms: number, spanMs: number, locale: string): string {
  const date = new Date(ms);
  if (spanMs > 24 * 60 * 60 * 1000) {
    return new Intl.DateTimeFormat(locale, {
      weekday: "short",
      hour: "numeric",
    }).format(date);
  }
  return new Intl.DateTimeFormat(locale, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

const NICE_TIME_STEPS_MS = [
  60 * 1000, // 1 min
  5 * 60 * 1000, // 5 min
  10 * 60 * 1000, // 10 min
  15 * 60 * 1000, // 15 min
  30 * 60 * 1000, // 30 min
  60 * 60 * 1000, // 1 hr
  2 * 60 * 60 * 1000, // 2 hr
  3 * 60 * 60 * 1000, // 3 hr
  6 * 60 * 60 * 1000, // 6 hr
  12 * 60 * 60 * 1000, // 12 hr
  24 * 60 * 60 * 1000, // 1 day
  48 * 60 * 60 * 1000, // 2 days
  7 * 24 * 60 * 60 * 1000, // 1 week
];

function computeTimeTicks(startMs: number, endMs: number): number[] {
  const span = endMs - startMs;
  if (span <= 0) {
    return [startMs];
  }
  const maxTicks = 5;
  const step =
    NICE_TIME_STEPS_MS.find((s) => span / s <= maxTicks) ??
    Math.ceil(span / maxTicks);

  const firstTick = Math.ceil(startMs / step) * step;
  const ticks: number[] = [];
  for (let t = firstTick; t <= endMs; t += step) {
    ticks.push(t);
  }
  if (ticks.length < 2) {
    return [startMs, endMs];
  }
  return ticks;
}

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: ChartPoint;
  index?: number;
}

const renderSolveDot = (props: CustomDotProps) => {
  const { cx, cy, payload, index } = props;
  if (cx == null || cy == null || !payload?.solveEvent) {
    return <g key={`empty-dot-${index ?? "x"}`} />;
  }
  const { color, isMeta, id } = payload.solveEvent;
  return (
    <circle
      key={`solve-dot-${id}`}
      cx={cx}
      cy={cy}
      r={isMeta ? 5.5 : 4}
      fill={color}
      stroke="var(--bs-body-bg)"
      strokeWidth={1.25}
    />
  );
};

const renderActiveSolveDot = (props: CustomDotProps) => {
  const { cx, cy, payload, index } = props;
  if (cx == null || cy == null || !payload?.solveEvent) {
    return <g key={`empty-active-dot-${index ?? "x"}`} />;
  }
  const { color, isMeta, id } = payload.solveEvent;
  return (
    <circle
      key={`active-solve-dot-${id}`}
      cx={cx}
      cy={cy}
      r={isMeta ? 7 : 5.5}
      fill={color}
      stroke="var(--bs-body-color)"
      strokeWidth={1.5}
    />
  );
};

interface TooltipPayloadItem {
  payload?: ChartPoint;
}

interface StatsTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  locale: string;
}

const StatsChartTooltip = ({ active, payload, locale }: StatsTooltipProps) => {
  const { t } = useTranslation();
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const point = payload[0]?.payload;
  if (!point) {
    return null;
  }

  return (
    <div
      style={{
        backgroundColor: "var(--bs-body-bg)",
        color: "var(--bs-body-color)",
        border: "1px solid var(--bs-border-color)",
        borderRadius: "0.375rem",
        padding: "0.45rem 0.65rem",
        fontSize: "0.8rem",
      }}
    >
      {point.solveEvent && (
        <div className="d-flex align-items-center gap-1 fw-bold mb-1">
          <span
            style={{
              display: "inline-block",
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: point.solveEvent.color,
              flexShrink: 0,
            }}
          />
          <span>{point.solveEvent.name}</span>
          {point.solveEvent.isMeta && (
            <Badge bg="dark" text="white">
              {t("meta")}
            </Badge>
          )}
        </div>
      )}
      <div className="text-body-secondary">
        {formatSolveTimestamp(
          point.solveEvent ? point.solveEvent.solvedMs : point.time,
          locale
        )}
      </div>
      <div>
        {t("stats-solved")}: <strong>{point.solved}</strong> ·{" "}
        {t("stats-unlocked")}: <strong>{point.unlocked}</strong>
      </div>
    </div>
  );
};

export const StatsDrawer = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const { t, i18n } = useTranslation();
  const hunt = useStore((state) => state.huntSlice.hunt);
  const {
    puzzles,
    numPuzzlesUnlocked,
    numPuzzlesSolved,
    numMetasUnlocked,
    numMetasSolved,
  } = useStore((state) => state.puzzlesSlice);

  const locale = i18n.resolvedLanguage || "en";
  const timeAgoLocale = i18n.resolvedLanguage || "en-US";

  React.useEffect(() => {
    if (!open) {
      return;
    }
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  const { solvedEntries, chartData, domain } = React.useMemo(() => {
    const puzzleList = Object.values<Puzzle>(puzzles);

    const solvedList: SolvedPuzzleEntry[] = [];
    for (const puzzle of puzzleList) {
      const solvedMs = getSolvedTimeMs(puzzle);
      if (solvedMs !== null) {
        solvedList.push({
          puzzle,
          solvedMs,
          color: getPuzzleRoundColor(puzzle, puzzles),
        });
      }
    }

    const latestFirst = [...solvedList].sort((a, b) => {
      if (b.solvedMs !== a.solvedMs) {
        return b.solvedMs - a.solvedMs;
      }
      return b.puzzle.id - a.puzzle.id;
    });

    const nowMs = Date.now();
    const huntStartMs = hunt.start_time ? Date.parse(hunt.start_time) : null;
    const huntEndMs = hunt.end_time ? Date.parse(hunt.end_time) : null;

    let earliestUnlockMs: number | null = null;
    for (const puzzle of puzzleList) {
      const createdMs = Date.parse(puzzle.created_on);
      if (
        !Number.isNaN(createdMs) &&
        (earliestUnlockMs === null || createdMs < earliestUnlockMs)
      ) {
        earliestUnlockMs = createdMs;
      }
    }

    const chartStartMs =
      huntStartMs !== null && !Number.isNaN(huntStartMs)
        ? huntStartMs
        : earliestUnlockMs;

    if (
      chartStartMs === null ||
      (huntStartMs !== null && nowMs < huntStartMs && puzzleList.length === 0)
    ) {
      return {
        solvedEntries: latestFirst,
        chartData: [] as ChartPoint[],
        domain: null as [number, number] | null,
      };
    }

    const chartEndMs =
      huntEndMs !== null && !Number.isNaN(huntEndMs)
        ? Math.min(nowMs, huntEndMs)
        : nowMs;
    const effectiveEndMs = Math.max(chartEndMs, chartStartMs + 60 * 1000);

    type RawEvent =
      | { kind: "unlock"; time: number; id: PuzzleId }
      | { kind: "solve"; time: number; id: PuzzleId; solveEvent: SolveEvent };

    const events: RawEvent[] = [];

    for (const puzzle of puzzleList) {
      const createdMs = Date.parse(puzzle.created_on);
      if (!Number.isNaN(createdMs) && createdMs <= chartEndMs) {
        events.push({
          kind: "unlock",
          time: Math.max(createdMs, chartStartMs),
          id: puzzle.id,
        });
      }
    }

    for (const entry of solvedList) {
      if (entry.solvedMs <= chartEndMs) {
        events.push({
          kind: "solve",
          time: Math.max(entry.solvedMs, chartStartMs),
          id: entry.puzzle.id,
          solveEvent: {
            id: entry.puzzle.id,
            name: entry.puzzle.name,
            isMeta: entry.puzzle.is_meta,
            color: entry.color,
            solvedMs: entry.solvedMs,
          },
        });
      }
    }

    events.sort((a, b) => {
      if (a.time !== b.time) {
        return a.time - b.time;
      }
      if (a.kind !== b.kind) {
        return a.kind === "unlock" ? -1 : 1;
      }
      return a.id - b.id;
    });

    const points: ChartPoint[] = [
      { time: chartStartMs, unlocked: 0, solved: 0 },
    ];
    let unlocked = 0;
    let solved = 0;

    for (const event of events) {
      if (event.kind === "unlock") {
        unlocked += 1;
        points.push({ time: event.time, unlocked, solved });
      } else {
        solved += 1;
        points.push({
          time: event.time,
          unlocked,
          solved,
          solveEvent: event.solveEvent,
        });
      }
    }

    points.push({ time: effectiveEndMs, unlocked, solved });

    return {
      solvedEntries: latestFirst,
      chartData: points,
      domain: [chartStartMs, effectiveEndMs] as [number, number],
    };
  }, [puzzles, hunt.start_time, hunt.end_time, open]);

  const spanMs = domain ? domain[1] - domain[0] : 0;
  const xTicks = React.useMemo(
    () => (domain ? computeTimeTicks(domain[0], domain[1]) : []),
    [domain]
  );

  return (
    <Drawer
      open={open}
      onClose={onClose}
      direction="right"
      zIndex={1040}
      size="min(520px, 95vw)"
      customIdSuffix="stats"
      className="navbar-themed"
      style={{
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div style={{ flex: 1, overflowY: "auto", padding: "1rem" }}>
        {open && (
          <>
            <div className="d-flex align-items-end justify-content-between flex-wrap gap-2 mb-2 me-2">
              <div className="d-flex gap-4 fw-bold text-center ms-4">
                <div>
                  <div className="small">{t("metas")}</div>
                  <div>
                    <span
                      className="text-primary"
                      style={{ fontSize: "1.25rem" }}
                    >
                      {numMetasSolved()}
                    </span>{" "}
                    /{" "}
                    <span className="text-secondary">{numMetasUnlocked()}</span>
                  </div>
                </div>
                <div>
                  <div className="small">{t("puzzles")}</div>
                  <div>
                    <span
                      className="text-success"
                      style={{ fontSize: "1.25rem" }}
                    >
                      {numPuzzlesSolved()}
                    </span>{" "}
                    /{" "}
                    <span className="text-secondary">
                      {numPuzzlesUnlocked()}
                    </span>
                  </div>
                </div>
              </div>
              {chartData.length > 0 && domain && (
                <div className="d-flex align-items-center gap-3 small text-body-secondary">
                  <span className="d-inline-flex align-items-center gap-1">
                    <span
                      style={{
                        display: "inline-block",
                        width: "12px",
                        height: "2px",
                        backgroundColor: "#198754",
                      }}
                    />
                    {t("stats-solved")}
                  </span>
                  <span className="d-inline-flex align-items-center gap-1">
                    <span
                      style={{
                        display: "inline-block",
                        width: "12px",
                        height: "2px",
                        backgroundColor: "#6c757d",
                      }}
                    />
                    {t("stats-unlocked")}
                  </span>
                </div>
              )}
            </div>

            <div className="mb-3">
              {chartData.length > 0 && domain ? (
                <div style={{ width: "100%", height: "240px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                      data={chartData}
                      margin={{ top: 10, right: 16, bottom: 4, left: -12 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="var(--bs-border-color)"
                      />
                      <XAxis
                        dataKey="time"
                        type="number"
                        scale="time"
                        domain={domain}
                        ticks={xTicks}
                        allowDuplicatedCategory={false}
                        tickFormatter={(value: number) =>
                          formatAxisTick(value, spanMs, locale)
                        }
                        tick={{
                          fill: "var(--bs-secondary-color)",
                          fontSize: 11,
                        }}
                        stroke="var(--bs-border-color)"
                      />
                      <YAxis
                        allowDecimals={false}
                        domain={[0, "auto"]}
                        tick={{
                          fill: "var(--bs-secondary-color)",
                          fontSize: 11,
                        }}
                        stroke="var(--bs-border-color)"
                      />
                      <Tooltip
                        isAnimationActive={false}
                        content={<StatsChartTooltip locale={locale} />}
                      />
                      <Area
                        type="stepAfter"
                        dataKey="unlocked"
                        name={t("stats-unlocked")}
                        stroke="#6c757d"
                        strokeWidth={1.5}
                        fill="none"
                        dot={false}
                        activeDot={false}
                        isAnimationActive={false}
                      />
                      <Area
                        type="stepAfter"
                        dataKey="solved"
                        name={t("stats-solved")}
                        stroke="#198754"
                        strokeWidth={2}
                        fill="rgba(25, 135, 84, 0.12)"
                        dot={renderSolveDot}
                        activeDot={renderActiveSolveDot}
                        isAnimationActive={false}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center text-body-secondary py-4 small">
                  {t("no-chart-data")}
                </div>
              )}
            </div>

            <div className="border-top pt-3 mx-3">
              <h6 className="fw-bold mb-2">{t("latest-puzzles-solved")}</h6>
              {solvedEntries.length === 0 ? (
                <p className="text-body-secondary small mb-0">
                  {t("no-puzzles-solved-yet")}
                </p>
              ) : (
                <table className="table table-sm mb-0">
                  <tbody>
                    {solvedEntries
                      .slice(0, 8)
                      .map(({ puzzle, solvedMs, color }) => (
                        <tr key={puzzle.id}>
                          <td className="align-middle ps-3">
                            <span className="d-inline-flex align-items-center gap-2 flex-wrap">
                              <span
                                style={{
                                  display: "inline-block",
                                  width: "8px",
                                  height: "8px",
                                  borderRadius: "50%",
                                  backgroundColor: color,
                                  flexShrink: 0,
                                }}
                              />
                              <span>{puzzle.name}</span>
                              {puzzle.is_meta && (
                                <Badge bg="dark" text="white">
                                  {t("meta")}
                                </Badge>
                              )}
                            </span>
                          </td>
                          <td className="text-end text-nowrap text-body-secondary small align-middle pe-3">
                            <OverlayTrigger
                              placement="left"
                              overlay={
                                <BootstrapTooltip
                                  id={`stats-solved-time-${puzzle.id}`}
                                >
                                  {formatSolveTimestamp(solvedMs, locale)}
                                </BootstrapTooltip>
                              }
                            >
                              <span>
                                <ReactTimeAgo
                                  date={new Date(solvedMs)}
                                  locale={timeAgoLocale}
                                  tooltip={false}
                                />
                              </span>
                            </OverlayTrigger>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </Drawer>
  );
};
