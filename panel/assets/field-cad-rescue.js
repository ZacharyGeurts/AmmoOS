/**
 * Secure-attention hook — opens Monster native popup when AmmoOS has focus.
 * @g16 5.1.0 · Grok16/field-stack-fabric · ammo-c2 rescue chord
 */
(function (global) {
  "use strict";

  function isRunningOs() {
    const path = global.location?.pathname || "";
    return path === "/field" || path === "/field/" || path === "/";
  }

  function hasOsFocus() {
    if (isRunningOs()) return true;
    if (document.hasFocus && document.hasFocus()) return true;
    try {
      if (global.parent !== global && global.parent.document?.hasFocus?.()) return true;
    } catch (_) {}
    return false;
  }

  function isCadChord(ev) {
    if (!ev.ctrlKey || !ev.altKey) return false;
    if (ev.key === "Delete" || ev.key === "Del") return true;
    if (ev.ctrlKey && ev.shiftKey && ev.key === "Escape") return true;
    return false;
  }

  function openMonster() {
    if (global.FieldMonsterCadPopup?.open) {
      global.FieldMonsterCadPopup.open();
      return;
    }
    global.FieldMonsterHangDialog?.poll?.();
  }

  function onKeydown(ev) {
    if (!hasOsFocus()) return;
    if (ev.ctrlKey && ev.shiftKey && ev.key === "Escape") {
      ev.preventDefault();
      ev.stopPropagation();
      openMonster();
      return;
    }
    if (ev.ctrlKey && ev.altKey && (ev.key === "Delete" || ev.key === "Del")) {
      ev.preventDefault();
      ev.stopPropagation();
      openMonster();
    }
  }

  function init() {
    document.addEventListener("keydown", onKeydown, true);
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        global.FieldMonsterCadPopup?.close?.();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.FieldCadRescue = { hasOsFocus, isRunningOs, init };
})(typeof window !== "undefined" ? window : globalThis);