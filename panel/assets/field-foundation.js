/* NEXUS Field Foundation — full panel cache for instant paint (/api/status). */
(function (global) {
  const KEY = "nexus-field-v4";
  const LEGACY_KEYS = ["nexus-field-v3", "nexus-field-v2"];

  function persist(data) {
    if (!data) return;
    try {
      global.sessionStorage.setItem(KEY, JSON.stringify(data));
    } catch (_e) {
      /* private mode */
    }
    global.NEXUS_FIELD = data;
    try {
      global.dispatchEvent(new CustomEvent("nexus-field-ready", { detail: data }));
    } catch (_e2) {
      /* old browsers */
    }
  }

  function load() {
    if (global.NEXUS_FIELD) return global.NEXUS_FIELD;
    try {
      const raw = global.sessionStorage.getItem(KEY);
      if (raw) return JSON.parse(raw);
      for (const legacy of LEGACY_KEYS) {
        const old = global.sessionStorage.getItem(legacy);
        if (old) {
          const doc = JSON.parse(old);
          persist(doc);
          return doc;
        }
      }
    } catch (_e) {
      return null;
    }
    return null;
  }

  function fetchField() {
    return global.fetch("/api/status", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }

  function boot(dest) {
    const cached = load();
    if (cached) {
      global.NEXUS_FIELD = cached;
      if (dest) global.location.replace(dest);
      fetchField().then((d) => { if (d) persist(d); });
      return;
    }
    fetchField().then((d) => {
      if (d) persist(d);
      if (dest) global.location.replace(dest);
    });
  }

  global.NexusField = { KEY, load, boot, persist, fetchField };
})(window);