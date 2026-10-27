import { readFile } from "fs/promises";
import { homedir } from "os";
import { join } from "path";

export async function GET() {
  try {
    const path = join(homedir(), ".gantry", "active_pos.json");
    const raw = await readFile(path, "utf-8");
    return Response.json(JSON.parse(raw));
  } catch {
    return Response.json({ containers: [] });
  }
}
