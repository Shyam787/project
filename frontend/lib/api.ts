export type BackendReady = {
  success: boolean;
  payload?: {
    status: string;
    environment: string;
    pipeline_order: string[];
  };
};

const baseUrl =
  process.env.INTERNAL_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

export async function getBackendReady(): Promise<BackendReady | null> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/ready`, {
      next: { revalidate: 15 }
    });
    if (!response.ok) return null;
    return (await response.json()) as BackendReady;
  } catch {
    return null;
  }
}
