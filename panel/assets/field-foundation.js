/* NEXUS Field Foundation — invisible warmed cache for instant panel paint. */
(function (global) {
  const KEY = "nexus-field-v3";

  function persist(data) {
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
    } catch (_e) {
      return null;
    }
    return null;
  }

  function fetchField() {
    return global.fetch("/api/field", { cache: "no-store" })
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
      else if (!d && dest) global.location.replace(dest);
    });
  }

  global.NexusField = { KEY, load, boot, persist, fetchField };
})(window);