/* KILROY virtual rootfs — browser-side Linux-compatible tree */
(function (global) {
  "use strict";

  function F(content, mode, owner) {
    return { t: "f", m: mode || "-rw-r--r--", o: owner || "kilroy", s: content || "", x: false };
  }
  function X(content, mode) {
    return { t: "f", m: mode || "-rwxr-xr-x", o: "root", s: content || "", x: true };
  }
  function D(children) {
    return { t: "d", m: "drwxr-xr-x", o: "kilroy", c: children || {} };
  }
  function L(target) {
    return { t: "l", m: "lrwxrwxrwx", o: "kilroy", l: target };
  }

  var STATUS = [
    "name=KILROY",
    "codename=Sanctuary",
    "version=1.1.0",
    "abi=kilroy-field-1.0",
    "compat=Linux-POSIX",
    "field_one=canonical",
    "authority=127.0.0.1",
    "depth=0",
    "slots=TIME,RAM,THERMO,CONTEXT,CPU,FLOW,CACHE,DIRECT",
    "grok16_pair=5.2.0",
    "ammoos_pair=2.0.0-beta3",
  ].join("\n");

  var SECURITY = [
    "nexus_guard=armed",
    "loopback_sanctuary=127.0.0.1",
    "strike_authorized=false",
    "field_not_one_scan=active",
    "rekill_registry=loaded",
  ].join("\n");

  var BOOT_PROC = [
    "loader=grok",
    "handoff=ok",
    "initramfs=build/initramfs.cpio.gz",
    "bzImage=build/bzImage",
    "LOCALVERSION=-kilroy",
  ].join("\n");

  var OS_RELEASE = [
    "NAME=KILROY",
    "PRETTY_NAME=KILROY Field OS 1.1.0 Sanctuary",
    "ID=kilroy",
    "ID_LIKE=linux",
    "VERSION_ID=1.1.0",
    "VERSION_CODENAME=Sanctuary",
    "HOME_URL=https://zacharygeurts.github.io/KILROY/",
    "SUPPORT_URL=https://github.com/ZacharyGeurts/KILROY",
    "BUG_REPORT_URL=https://github.com/ZacharyGeurts/KILROY/issues",
  ].join("\n");

  var BASHRC = [
    "# KILROY field shell — loopback sanctuary",
    "export PS1='kilroy@127.0.0.1:\\w\\$ '",
    "export PATH=/bin:/usr/bin:/opt/kilroy/scripts",
    "alias ll='ls -la'",
    "alias la='ls -A'",
    "echo 'Field 1 @ 127.0.0.1 — type help or ls'",
  ].join("\n");

  var BUILD_SH = [
    "#!/bin/sh",
    "# KILROY kernel build (run on host Linux)",
    "./scripts/kilroy-stage-compat.sh",
    "./scripts/build-kilroy.sh",
    "echo 'bzImage -> build/bzImage'",
  ].join("\n");

  var GROK_BOOT = [
    "#!/bin/sh",
    "qemu-system-x86_64 -kernel build/bzImage -initrd build/initramfs.cpio.gz \\",
    "  -append 'console=ttyS0' -nographic",
  ].join("\n");

  var tree = D({
    bin: D({
      busybox: L("/bin/kilroy-status"),
      sh: X("#!/bin/sh\n# KILROY shell\n", "-rwxr-xr-x"),
      "kilroy-status": X("#!/bin/sh\ncat /proc/kilroy_field/status\n"),
      "kilroy-ioctl-test": X("#!/bin/sh\necho ioctl ABI kilroy-field-1.0 layout=9\n"),
      ls: L("/bin/busybox"),
      cat: L("/bin/busybox"),
      echo: L("/bin/busybox"),
      pwd: L("/bin/busybox"),
      cd: L("/bin/busybox"),
      uname: L("/bin/busybox"),
    }),
    boot: D({
      grok: D({
        bzImage: F("[kernel image — run ./scripts/build-kilroy.sh]", "-rw-r--r--", "root"),
        "initramfs.cpio.gz": F("[initramfs — run ./scripts/grok-mkimage.sh]", "-rw-r--r--", "root"),
        "BOOTX64.EFI": F("[Limine EFI]", "-rw-r--r--", "root"),
      }),
    }),
    etc: D({
      hostname: F("kilroy-field\n"),
      "os-release": F(OS_RELEASE + "\n"),
      "grok.conf": F("default=kilroy\nsanctuary=127.0.0.1\ntheme=field\n"),
      passwd: F("root:x:0:0:root:/root:/bin/sh\nkilroy:x:1000:1000:Field Operator:/home/kilroy:/bin/sh\n"),
    }),
    home: D({
      kilroy: D({
        ".bashrc": F(BASHRC + "\n"),
        ".profile": F("source ~/.bashrc\n"),
        "field-node": D({
          README: F("Your field node — spin up with: spin quick\n"),
          "spin.log": F("ready — awaiting grok-boot-qemu.sh\n"),
        }),
      }),
    }),
    opt: D({
      kilroy: D({
        README: F("KILROY Field OS — Linux-compatible, not Linux.\nhttps://zacharygeurts.github.io/KILROY/\n"),
        scripts: D({
          "build-kilroy.sh": X(BUILD_SH + "\n"),
          "grok-mkimage.sh": X("#!/bin/sh\n./scripts/grok-compose.sh && ./scripts/grok-mkimage.sh\n"),
          "grok-boot-qemu.sh": X(GROK_BOOT + "\n"),
          "kilroy-become-substrate.sh": X("#!/bin/sh\necho substrate overlay → KILROY identity\n"),
        }),
        build: D({
          bzImage: L("/boot/grok/bzImage"),
          "initramfs.cpio.gz": L("/boot/grok/initramfs.cpio.gz"),
        }),
      }),
    }),
    proc: D({
      kilroy_field: D({
        status: F(STATUS + "\n"),
        security: F(SECURITY + "\n"),
        boot: F(BOOT_PROC + "\n"),
      }),
      version: F("Linux version 7.1.1-kilroy (g16@field) #1 SMP Field OS\n"),
      cpuinfo: F("processor\t: 0\nmodel name\t: KILROY Field Die\nflags\t\t: field_physics amouranthrtx\n"),
      meminfo: F("MemTotal:       16777216 kB\nMemFree:        8388608 kB\nSwapCached:            0 kB\n"),
      uptime: F(" 12345.67 98765.43\n"),
    }),
    root: D({
      ".kilroy": F("sanctuary=127.0.0.1\nfield_one=canonical\n"),
    }),
    tmp: D({}),
    usr: D({
      bin: D({
        g16: X("#!/bin/sh\necho Grok16 g16 @ 16.2.0 — belt_2_0\n"),
        pythong: X("#!/bin/sh\necho GPY-16 driver — field python\n"),
        python3: L("/usr/bin/pythong"),
      }),
    }),
    var: D({
      log: D({
        "kilroy-boot.log": F("[grok-boot] Field OS 1.1.0 Sanctuary online\n[field-one] scan complete\n"),
        "field-hostile.log": F("FIELD_NOT_ONE entries consolidated to Field 1\n"),
      }),
    }),
  });

  function normalize(p) {
    var parts = p.replace(/\\/g, "/").split("/").filter(Boolean);
    var out = [];
    parts.forEach(function (seg) {
      if (seg === ".") return;
      if (seg === "..") {
        out.pop();
        return;
      }
      out.push(seg);
    });
    return "/" + out.join("/");
  }

  function resolve(root, cwd, raw) {
    var base = raw.charAt(0) === "/" ? "" : cwd === "/" ? "" : cwd.slice(1);
    var full = normalize("/" + (base ? base + "/" : "") + raw);
    var segs = full === "/" ? [] : full.slice(1).split("/");
    var node = root;
    var path = [];
    for (var i = 0; i < segs.length; i++) {
      var name = segs[i];
      if (!node || node.t !== "d") return { err: "not a directory: /" + path.join("/") };
      path.push(name);
      var next = node.c[name];
      if (!next) return { err: "no such file or directory: " + full };
      if (next.t === "l" && i < segs.length - 1) {
        var resolved = resolve(root, "/", next.l);
        if (resolved.err) return resolved;
        node = resolved.node;
        path = resolved.path === "/" ? [] : resolved.path.slice(1).split("/");
        i--;
        continue;
      }
      node = next;
    }
    if (node.t === "l") {
      var link = resolve(root, "/", node.l);
      if (link.err) return link;
      return { node: link.node, path: link.path };
    }
    return { node: node, path: full };
  }

  function resolveParent(root, cwd, raw) {
    var target = raw || ".";
    if (target === "..") return resolve(root, cwd, "..");
    var full = target.charAt(0) === "/" ? normalize(target) : normalize(cwd + "/" + target);
    var parent = full.replace(/\/[^/]+$/, "") || "/";
    var base = full.split("/").pop() || "";
    var r = resolve(root, "/", parent);
    if (r.err) return r;
    if (r.node.t !== "d") return { err: "not a directory: " + parent };
    return { dir: r.node, name: base, path: full, parent: parent };
  }

  function listEntries(dirNode, showAll) {
    var names = Object.keys(dirNode.c).sort();
    if (showAll) {
      names.unshift(".", "..");
    }
    return names.map(function (n) {
      if (n === "." || n === "..") return { name: n, node: n === "." ? dirNode : null, link: n };
      return { name: n, node: dirNode.c[n] };
    });
  }

  function formatMode(node) {
    return node.m || (node.t === "d" ? "drwxr-xr-x" : "-rw-r--r--");
  }

  function sizeOf(node) {
    if (node.t === "d") return 4096;
    if (node.t === "l") return (node.l || "").length;
    return (node.s || "").length;
  }

  global.KILROY_VFS = {
    root: tree,
    normalize: normalize,
    resolve: resolve,
    resolveParent: resolveParent,
    listEntries: listEntries,
    formatMode: formatMode,
    sizeOf: sizeOf,
    read: function (node) {
      if (!node) return "";
      if (node.t === "f") return node.s || "";
      if (node.t === "l") return node.l + "\n";
      return "";
    },
    isDir: function (node) {
      return node && node.t === "d";
    },
    isFile: function (node) {
      return node && (node.t === "f" || node.t === "l");
    },
  };
})(typeof window !== "undefined" ? window : globalThis);