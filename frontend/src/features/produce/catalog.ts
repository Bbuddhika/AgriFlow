import { apiRead } from "@/lib/api";

export type ProduceType = { id: string; code: string; name: string; unit: string };

export async function loadCatalog(): Promise<ProduceType[]> {
  return apiRead<ProduceType[]>("/api/v1/catalog/produce");
}
