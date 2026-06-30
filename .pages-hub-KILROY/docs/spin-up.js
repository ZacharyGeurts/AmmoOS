(function () {
  const VERSION = "v1.1.0";
  const VER = "1.1.0";
  const REPO = "https://github.com/ZacharyGeurts/KILROY.git";
  const RELEASES = "https://github.com/ZacharyGeurts/KILROY/releases/download/" + VERSION;

  const platformMap = {
    x86_64: "linux-gnu-x86_64",
    aarch64: "linux-gnu-aarch64",
    i386: "linux-gnu-i386",
    riscv64: "linux-gnu-riscv64",
    arm: "linux-gnu-arm",
    darwin_arm64: "darwin-aarch64",
    darwin_x64: "darwin-x86_64",
    win64: "win32-x86_64",
    android_arm64: "android-aarch64",
  };

  const profiles = {
    quick: {
      steps: [
        "git clone " + REPO,
        "cd KILROY && git checkout " + VERSION,
        "./scripts/kilroy-become-substrate.sh",
        "./scripts/build-kilroy.sh",
        "./scripts/grok-mkimage.sh",
        "./scripts/grok-boot-qemu.sh",
      ],
    },
    full: {
      steps: [
        "git clone https://github.com/ZacharyGeurts/AmmoOS.git",
        "cd AmmoOS && ./scripts/wire-stack.sh",
        "cd ../KILROY && git checkout " + VERSION,
        "./scripts/build-kilroy.sh",
        "cd .. && ./scripts/start-field-stack.sh",
        "open http://127.0.0.1:9477/grok-lab",
      ],
    },
    release: {
      steps: [],
    },
  };

  const cmdEl = document.getElementById("spin-cmd");
  const profileSel = document.getElementById("spin-profile");
  const platSel = document.getElementById("spin-platform");

  function asset(plat) {
    const id = platformMap[plat] || platformMap.x86_64;
    return "kilroy-" + VER + "-" + id + ".tar.gz";
  }

  function render() {
    const profile = profileSel ? profileSel.value : "quick";
    const plat = platSel ? platSel.value : "x86_64";
    let steps;
    if (profile === "release") {
      const a = asset(plat);
      steps = [
        "curl -LO " + RELEASES + "/" + a,
        "tar -xzf " + a,
        "# see BOOTSTRAP.md inside pack for your OS",
      ];
    } else {
      steps = (profiles[profile] || profiles.quick).steps.slice();
    }
    if (cmdEl) cmdEl.textContent = steps.join("\n");
  }

  if (profileSel) profileSel.addEventListener("change", render);
  if (platSel) platSel.addEventListener("change", render);
  render();

  const copyBtn = document.getElementById("copy-cmd");
  if (copyBtn && cmdEl) {
    copyBtn.addEventListener("click", function () {
      navigator.clipboard.writeText(cmdEl.textContent || "").then(function () {
        copyBtn.textContent = "Copied!";
        setTimeout(function () { copyBtn.textContent = "Copy commands"; }, 1800);
      });
    });
  }
})();