import { mockSchematicGeometry } from "@/lib/mockSchematicGeometry";
import type { SchematicGeometry } from "@/types/schematic";

export async function loadSchematicGeometry(): Promise<SchematicGeometry> {
  // Future Tauri bridge integration should replace this mock loader.
  return mockSchematicGeometry;
}
