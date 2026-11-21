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

function getStarPoints(
  cx: number,
  cy: number,
  outerRadius: number,
  innerRadius: number
): string {
  const points: string[] = [];
  for (let i = 0; i < 10; i++) {
    const angle = -Math.PI / 2 + (i * Math.PI) / 5;
    const radius = i % 2 === 0 ? outerRadius : innerRadius;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;
    points.push(`${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return points.join(" ");
}

const renderSolveDot = (props: CustomDotProps) => {
  const { cx, cy, payload, index } = props;
  if (cx == null || cy == null || !payload?.solveEvent) {
    return <g key={`empty-dot-${index ?? "x"}`} />;
  }
  const { color, isMeta, id } = payload.solveEvent;
  if (isMeta) {
    return (
      <polygon
        key={`solve-dot-${id}`}
        points={getStarPoints(cx, cy, 7.5, 3.4)}
        fill={color}
        stroke="var(--bs-body-bg)"
        strokeWidth={1.25}
        strokeLinejoin="round"
      />
    );
  }
  return (
    <circle
      key={`solve-dot-${id}`}
      cx={cx}
      cy={cy}
      r={4}
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
  if (isMeta) {
    return (
      <polygon
        key={`active-solve-dot-${id}`}
        points={getStarPoints(cx, cy, 9, 4)}
        fill={color}
        stroke="var(--bs-body-color)"
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
    );
  }
  return (
    <circle
      key={`active-solve-dot-${id}`}
      cx={cx}
      cy={cy}
      r={5.5}
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

const DEFAULT_STATS_DRAWER_WIDTH = 520;
const MIN_STATS_DRAWER_WIDTH = 260;
const STATS_DRAWER_WIDTH_STORAGE_KEY = "cardboard-stats-drawer-width";

const DEFAULT_STATS_CHART_HEIGHT = 240;
const MIN_STATS_CHART_HEIGHT = 120;
const STATS_CHART_HEIGHT_STORAGE_KEY = "cardboard-stats-chart-height";

function clampDrawerWidth(width: number): number {
  const maxWidth = Math.max(
    MIN_STATS_DRAWER_WIDTH,
    Math.floor(window.innerWidth * 0.95)
  );
  return Math.min(Math.max(width, MIN_STATS_DRAWER_WIDTH), maxWidth);
}

function getInitialDrawerWidth(): number {
  try {
    const stored = localStorage.getItem(STATS_DRAWER_WIDTH_STORAGE_KEY);
    if (stored) {
      const parsed = parseInt(stored, 10);
      if (!Number.isNaN(parsed)) {
        return clampDrawerWidth(parsed);
      }
    }
  } catch {
    // Ignore localStorage access errors.
  }
  return clampDrawerWidth(DEFAULT_STATS_DRAWER_WIDTH);
}

function clampChartHeight(height: number): number {
  const maxHeight = Math.max(
    MIN_STATS_CHART_HEIGHT,
    Math.floor(window.innerHeight * 0.75)
  );
  return Math.min(Math.max(height, MIN_STATS_CHART_HEIGHT), maxHeight);
}

function getInitialChartHeight(): number {
  try {
    const stored = localStorage.getItem(STATS_CHART_HEIGHT_STORAGE_KEY);
    if (stored) {
      const parsed = parseInt(stored, 10);
      if (!Number.isNaN(parsed)) {
        return clampChartHeight(parsed);
      }
    }
  } catch {
    // Ignore localStorage access errors.
  }
  return clampChartHeight(DEFAULT_STATS_CHART_HEIGHT);
}

export const StatsDrawer = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const { t, i18n } = useTranslation();
  const hunt = useStore((state) => state.huntSlice.hunt);
  const { puzzles } = useStore((state) => state.puzzlesSlice);

  const [drawerWidth, setDrawerWidth] = React.useState<number>(
    getInitialDrawerWidth
  );
  const [isDragging, setIsDragging] = React.useState(false);
  const dragStartRef = React.useRef<{ x: number; width: number } | null>(null);
  const latestWidthRef = React.useRef<number>(drawerWidth);
  latestWidthRef.current = drawerWidth;

  const [chartHeight, setChartHeight] = React.useState<number>(
    getInitialChartHeight
  );
  const [isDraggingHeight, setIsDraggingHeight] = React.useState(false);
  const heightDragStartRef = React.useRef<{ y: number; height: number } | null>(
    null
  );
  const latestHeightRef = React.useRef<number>(chartHeight);
  latestHeightRef.current = chartHeight;

  const locale = i18n.resolvedLanguage || "en";
  const timeAgoLocale = i18n.resolvedLanguage || "en-US";

  React.useEffect(() => {
    if (!isDragging) {
      return;
    }

    const prevUserSelect = document.body.style.userSelect;
    const prevCursor = document.body.style.cursor;
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";

    const onMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current) {
        return;
      }
      const deltaX = dragStartRef.current.x - e.clientX;
      setDrawerWidth(clampDrawerWidth(dragStartRef.current.width + deltaX));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      dragStartRef.current = null;
      try {
        localStorage.setItem(
          STATS_DRAWER_WIDTH_STORAGE_KEY,
          String(latestWidthRef.current)
        );
      } catch {
        // Ignore localStorage access errors.
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      document.body.style.userSelect = prevUserSelect;
      document.body.style.cursor = prevCursor;
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [isDragging]);

  const handleDragStart = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    dragStartRef.current = { x: e.clientX, width: drawerWidth };
    setIsDragging(true);
  };

  React.useEffect(() => {
    if (!isDraggingHeight) {
      return;
    }

    const prevUserSelect = document.body.style.userSelect;
    const prevCursor = document.body.style.cursor;
    document.body.style.userSelect = "none";
    document.body.style.cursor = "row-resize";

    const onMouseMove = (e: MouseEvent) => {
      if (!heightDragStartRef.current) {
        return;
      }
      const deltaY = e.clientY - heightDragStartRef.current.y;
      setChartHeight(
        clampChartHeight(heightDragStartRef.current.height + deltaY)
      );
    };

    const onMouseUp = () => {
      setIsDraggingHeight(false);
      heightDragStartRef.current = null;
      try {
        localStorage.setItem(
          STATS_CHART_HEIGHT_STORAGE_KEY,
          String(latestHeightRef.current)
        );
      } catch {
        // Ignore localStorage access errors.
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      document.body.style.userSelect = prevUserSelect;
      document.body.style.cursor = prevCursor;
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [isDraggingHeight]);

  const handleHeightDragStart = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    heightDragStartRef.current = { y: e.clientY, height: chartHeight };
    setIsDraggingHeight(true);
  };

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
      size={drawerWidth}
      customIdSuffix="stats"
      className="navbar-themed"
      style={{
        display: "flex",
        flexDirection: "column",
        transition: isDragging ? "none" : undefined,
      }}
    >
      <div
        role="separator"
        aria-orientation="vertical"
        onMouseDown={handleDragStart}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          bottom: 0,
          width: "8px",
          cursor: "col-resize",
          zIndex: 10,
        }}
      />
      <div style={{ flex: 1, overflowY: "auto", padding: "1rem" }}>
        {open && (
          <>
            {chartData.length > 0 && domain && (
              <div className="d-flex align-items-center justify-content-end gap-3 small text-body-secondary mb-2 me-2">
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

            <div>
              {chartData.length > 0 && domain ? (
                <div style={{ width: "100%", height: `${chartHeight}px` }}>
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

            {chartData.length > 0 && domain ? (
              <div
                role="separator"
                aria-orientation="horizontal"
                onMouseDown={handleHeightDragStart}
                className="mx-3 my-2"
                style={{
                  height: "10px",
                  cursor: "row-resize",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <div
                  style={{
                    width: "100%",
                    borderTop: "1px solid var(--bs-border-color)",
                  }}
                />
              </div>
            ) : (
              <div className="border-top mx-3 my-3" />
            )}

            <div className="pt-1 mx-3">
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
