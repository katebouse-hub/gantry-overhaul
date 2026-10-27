"use client";

import { useState, useEffect, useCallback } from "react";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThreadListSidebar } from "@/components/assistant-ui/threadlist-sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbLink,
} from "@/components/ui/breadcrumb";
import {
  getCellZone,
  getCellSection,
  ZONE_BG,
  CONTAINER_STYLE,
  type Container,
  type GantryState,
} from "@/lib/gantry-data";
import { RefreshCw } from "lucide-react";

const GRID_ROWS = 27;
const GRID_COLS = 20;
const CELL_W = 22;
const CELL_H = 22;

function buildRowCells(
  x: number,
  containers: Container[],
  selected: string | null,
  onSelect: (c: Container) => void
): React.ReactNode[] {
  const rowContainers = containers
    .filter((c) => c.pos_1.x === x)
    .map((c) => ({
      ...c,
      yMin: Math.min(c.pos_1.y, c.pos_2.y),
      yMax: Math.max(c.pos_1.y, c.pos_2.y),
    }))
    .sort((a, b) => a.yMin - b.yMin);

  const cells: React.ReactNode[] = [];
  let y = 1;
  let ci = 0;

  while (y <= GRID_COLS) {
    const c = rowContainers[ci];
    if (c && c.yMin === y) {
      const span = c.yMax - c.yMin + 1;
      const style = CONTAINER_STYLE[c.color] ?? { bg: "#6b7280", text: "#fff" };
      const isSelected = selected === c.id;
      cells.push(
        <td
          key={y}
          colSpan={span}
          onClick={() => onSelect(c)}
          title={`${c.id} (${c.color})`}
          style={{
            width: CELL_W * span,
            height: CELL_H,
            backgroundColor: style.bg,
            color: style.text,
            border: isSelected
              ? "2px solid #facc15"
              : "1px solid rgba(0,0,0,0.15)",
            cursor: "pointer",
            fontSize: 9,
            fontWeight: 600,
            textAlign: "center",
            verticalAlign: "middle",
            padding: 0,
            userSelect: "none",
            boxSizing: "border-box",
            outline: isSelected ? "2px solid #facc15" : "none",
          }}
        >
          {c.id}
        </td>
      );
      y += span;
      ci++;
    } else {
      const zone = getCellZone(x, y);
      cells.push(
        <td
          key={y}
          style={{
            width: CELL_W,
            height: CELL_H,
            backgroundColor: zone ? ZONE_BG[zone] : "#f3f4f6",
            border: "1px solid rgba(0,0,0,0.08)",
            padding: 0,
            boxSizing: "border-box",
          }}
        />
      );
      y++;
    }
  }

  return cells;
}

function GantryGrid({
  containers,
  selected,
  onSelect,
}: {
  containers: Container[];
  selected: string | null;
  onSelect: (c: Container) => void;
}) {
  return (
    <div className="overflow-auto rounded-lg border bg-white shadow-sm dark:bg-gray-900">
      <table
        style={{
          borderCollapse: "collapse",
          tableLayout: "fixed",
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                width: 28,
                fontSize: 9,
                color: "#9ca3af",
                fontWeight: 400,
                textAlign: "center",
                padding: "2px 0",
              }}
            >
              x\y
            </th>
            {Array.from({ length: GRID_COLS }, (_, i) => i + 1).map((y) => (
              <th
                key={y}
                style={{
                  width: CELL_W,
                  fontSize: 9,
                  color: "#9ca3af",
                  fontWeight: 400,
                  textAlign: "center",
                  padding: "2px 0",
                }}
              >
                {y}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: GRID_ROWS }, (_, i) => i + 1).map((x) => (
            <tr key={x}>
              <td
                style={{
                  width: 28,
                  fontSize: 9,
                  color: "#9ca3af",
                  textAlign: "right",
                  paddingRight: 4,
                  userSelect: "none",
                }}
              >
                {x}
              </td>
              {buildRowCells(x, containers, selected, onSelect)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ContainerDetails({ container }: { container: Container | null }) {
  if (!container) {
    return (
      <div className="mt-4 rounded-lg border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
        Click a container on the grid to see details.
      </div>
    );
  }

  const style = CONTAINER_STYLE[container.color] ?? { bg: "#6b7280", text: "#fff" };
  const section = getCellSection(container.pos_1.x, container.pos_1.y);
  const zone = getCellZone(container.pos_1.x, container.pos_1.y);
  const yMin = Math.min(container.pos_1.y, container.pos_2.y);
  const yMax = Math.max(container.pos_1.y, container.pos_2.y);

  return (
    <div className="mt-4 rounded-lg border bg-card px-4 py-3 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <span
          className="rounded px-2 py-0.5 text-xs font-bold"
          style={{ backgroundColor: style.bg, color: style.text }}
        >
          {container.id}
        </span>
        <span className="text-sm font-semibold capitalize">{container.color}</span>
        {zone && (
          <span className="ml-auto text-xs text-muted-foreground">
            Zone: <span className="font-medium capitalize">{zone}</span>
            {section && ` (${section})`}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-sm">
        <div>
          <span className="text-muted-foreground">Row (x): </span>
          <span className="font-mono font-medium">{container.pos_1.x}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Columns (y): </span>
          <span className="font-mono font-medium">
            {yMin} → {yMax}
          </span>
        </div>
        <div>
          <span className="text-muted-foreground">Height (z): </span>
          <span className="font-mono font-medium">{container.pos_1.z}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Span: </span>
          <span className="font-mono font-medium">{yMax - yMin + 1} units</span>
        </div>
        <div>
          <span className="text-muted-foreground">pos_1: </span>
          <span className="font-mono font-medium">
            ({container.pos_1.x}, {container.pos_1.y}, {container.pos_1.z})
          </span>
        </div>
        <div>
          <span className="text-muted-foreground">pos_2: </span>
          <span className="font-mono font-medium">
            ({container.pos_2.x}, {container.pos_2.y}, {container.pos_2.z})
          </span>
        </div>
      </div>
    </div>
  );
}

export default function GantryPage() {
  const [state, setState] = useState<GantryState | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Container | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchState = useCallback(async (showSpinner = false) => {
    if (showSpinner) setRefreshing(true);
    try {
      const res = await fetch("/api/gantry/state");
      const data: GantryState = await res.json();
      setState(data);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchState();
  }, [fetchState]);

  const containers = state?.containers ?? [];

  return (
    <SidebarProvider>
      <div className="flex h-dvh w-full pr-0.5">
        <ThreadListSidebar />
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/">Gantry Chat</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>Gantry Interactive</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <button
              onClick={() => fetchState(true)}
              disabled={refreshing}
              className="ml-auto flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent disabled:opacity-50"
            >
              <RefreshCw
                className={`size-3 ${refreshing ? "animate-spin" : ""}`}
              />
              Refresh
            </button>
          </header>

          <div className="flex flex-1 flex-col overflow-auto p-4">
            {loading ? (
              <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
                Loading gantry state…
              </div>
            ) : (
              <>
                <div className="mb-2 flex items-center gap-3">
                  <h1 className="text-sm font-semibold">
                    Gantry Grid{" "}
                    <span className="font-normal text-muted-foreground">
                      ({GRID_ROWS}×{GRID_COLS}) — {containers.length} containers
                    </span>
                  </h1>
                  <div className="ml-auto flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <span className="inline-block size-3 rounded-sm border" style={{ background: "#fee2e2" }} />
                      Red zone
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="inline-block size-3 rounded-sm border" style={{ background: "#dbeafe" }} />
                      Blue zone
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="inline-block size-3 rounded-sm border" style={{ background: "#ffedd5" }} />
                      Orange zone
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="inline-block size-3 rounded-sm border" style={{ background: "#fef9c3" }} />
                      Yellow zone
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="inline-block size-3 rounded-sm border" style={{ background: "#e5e7eb" }} />
                      Black zone
                    </span>
                  </div>
                </div>

                <GantryGrid
                  containers={containers}
                  selected={selected?.id ?? null}
                  onSelect={setSelected}
                />

                <ContainerDetails container={selected} />
              </>
            )}
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
