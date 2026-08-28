import { notificationStore } from "../stores/notificationStore";

function currentHashedScripts(): string {
  return Array.from(document.querySelectorAll("script[src]"))
    .map((el) => new URL((el as HTMLScriptElement).src, window.location.href).pathname)
    .filter((path) => path.includes("/assets/"))
    .sort()
    .join("|");
}

function scriptsFromIndexHtml(html: string): string {
  return [...html.matchAll(/src="([^"]*\/assets\/[^"]+)"/g)]
    .map((match) => match[1])
    .sort()
    .join("|");
}

export function startAppVersionPolling(intervalMs = 5 * 60 * 1000): void {
  const installed = currentHashedScripts();
  if (!installed) return;

  let prompted = false;

  const check = async () => {
    if (prompted) return;
    try {
      const response = await fetch(`/index.html?_=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) return;
      const html = await response.text();
      const published = scriptsFromIndexHtml(html);
      if (published && published !== installed) {
        prompted = true;
        notificationStore.add(
          "A new version of the onicai app is available.",
          "info",
          0,
          {
            label: "Refresh page",
            onClick: () => window.location.reload(),
          },
        );
      }
    } catch (error) {
      console.debug("Version check failed:", error);
    }
  };

  setTimeout(check, 15000);
  setInterval(check, intervalMs);
}
