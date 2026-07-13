const pptxgen = require("pptxgenjs");

const DARK = "12141C";
const CARD = "20232F";
const CARD2 = "262A38";
const AMBER = "E8A33D";
const AMBER_D = "C8862A";
const TEAL = "4FB6A6";
const TEXT = "F2EFE9";
const MUTED = "9BA0B5";
const MUTED_D = "6B7085";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5

function bgSlide() {
  const s = pres.addSlide();
  s.background = { color: DARK };
  return s;
}

function pageNum(s, n) {
  s.addText(String(n).padStart(2, "0"), {
    x: 12.5, y: 7.05, w: 0.6, h: 0.3,
    fontFace: "Consolas", fontSize: 10, color: MUTED_D, align: "right",
  });
}

// ---------- Slide 1: Title (uses cover.png full-bleed) ----------
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addImage({ path: "cover.png", x: 0, y: 0, w: 13.333, h: 7.5 });
}

// ---------- Slide 2: The problem ----------
{
  const s = bgSlide();
  s.addText("Model routing today is a guess", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true,
    fontSize: 34, color: TEXT,
  });
  s.addText("Most multi-model systems route with hand-written rules", {
    x: 0.7, y: 1.35, w: 11.5, h: 0.5, fontFace: "Calibri", fontSize: 16, color: MUTED,
  });

  const items = [
    { label: "if difficulty > 0.7:", desc: "brittle thresholds nobody revisits", icon: "\u2717" },
    { label: "always use the big model", desc: "safe, but burns budget on easy queries", icon: "\u2717" },
    { label: "never adapts", desc: "no feedback loop — the rule doesn't learn from outcomes", icon: "\u2717" },
  ];
  let y = 2.4;
  items.forEach((it) => {
    s.addShape("roundRect", { x: 0.7, y, w: 11.9, h: 1.15, rectRadius: 0.1, fill: { color: CARD }, line: { type: "none" } });
    s.addShape("ellipse", { x: 1.05, y: y + 0.32, w: 0.5, h: 0.5, fill: { color: "2C3040" }, line: { color: AMBER_D, width: 1.5 } });
    s.addText(it.icon, { x: 1.05, y: y + 0.32, w: 0.5, h: 0.5, align: "center", valign: "middle", fontFace: "Arial", bold: true, fontSize: 18, color: AMBER });
    s.addText(it.label, { x: 1.8, y: y + 0.16, w: 9.5, h: 0.4, fontFace: "Consolas", fontSize: 17, bold: true, color: TEXT, margin: 0 });
    s.addText(it.desc, { x: 1.8, y: y + 0.58, w: 9.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0 });
    y += 1.4;
  });
  pageNum(s, 2);
}

// ---------- Slide 3: Core idea ----------
{
  const s = bgSlide();
  s.addText("Every model is an arm in a bandit", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });
  s.addText("BanditRoute treats model choice as a multi-armed bandit problem, and learns which arm to pull from reward feedback — not from a rule anyone wrote.", {
    x: 0.7, y: 1.35, w: 11.0, h: 0.7, fontFace: "Calibri", fontSize: 15, color: MUTED,
  });

  const arms = [
    { name: "Phi-3 (local)", note: "free, fast, lower accuracy" },
    { name: "Qwen (local)", note: "free, strong on code" },
    { name: "Fireworks Small", note: "cheap, solid all-rounder" },
    { name: "Fireworks Large", note: "best accuracy, most expensive" },
  ];
  const startX = 0.9, w = 2.75, gap = 0.25, y = 2.6, h = 3.5;
  arms.forEach((a, i) => {
    const x = startX + i * (w + gap);
    const highlight = i === 2;
    s.addShape("roundRect", {
      x, y, w, h, rectRadius: 0.12,
      fill: { color: highlight ? AMBER : CARD },
      line: { color: highlight ? AMBER_D : "383C4D", width: 1.5 },
    });
    s.addShape("roundRect", {
      x: x + 0.35, y: y + 0.5, w: w - 0.7, h: 0.9, rectRadius: 0.08,
      fill: { color: highlight ? "1A1D29" : "2C3040" }, line: { type: "none" },
    });
    s.addText(String.fromCharCode(945 + i), {
      x: x + 0.35, y: y + 0.5, w: w - 0.7, h: 0.9, align: "center", valign: "middle",
      fontFace: "Arial", bold: true, fontSize: 30, color: highlight ? AMBER : MUTED_D,
    });
    s.addText(a.name, {
      x: x + 0.15, y: y + 1.65, w: w - 0.3, h: 0.5, align: "center",
      fontFace: "Arial", bold: true, fontSize: 15, color: highlight ? "1A1D29" : TEXT,
    });
    s.addText(a.note, {
      x: x + 0.15, y: y + 2.15, w: w - 0.3, h: 0.9, align: "center",
      fontFace: "Calibri", fontSize: 12, color: highlight ? "3A2F14" : MUTED,
    });
  });
  pageNum(s, 3);
}

// ---------- Slide 4: How it works ----------
{
  const s = bgSlide();
  s.addText("Thompson Sampling, in four steps", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });

  const steps = [
    ["01", "Sample a belief", "Each arm has a Beta distribution over its success rate. Draw one sample per arm."],
    ["02", "Pick the best sample", "Route the query to whichever arm's sample came out highest this time."],
    ["03", "Observe the outcome", "Was the answer correct? What did it cost in tokens and latency?"],
    ["04", "Update the belief", "Feed the reward back into that arm's distribution. Repeat."],
  ];
  let y = 1.7;
  steps.forEach((st) => {
    s.addText(st[0], { x: 0.7, y, w: 1.0, h: 1.1, fontFace: "Arial", bold: true, fontSize: 34, color: AMBER });
    s.addText(st[1], { x: 1.8, y: y + 0.02, w: 4.3, h: 0.5, fontFace: "Arial", bold: true, fontSize: 17, color: TEXT });
    s.addText(st[2], { x: 1.8, y: y + 0.5, w: 4.3, h: 0.65, fontFace: "Calibri", fontSize: 12.5, color: MUTED });
    y += 1.3;
  });

  s.addShape("roundRect", { x: 7.0, y: 1.7, w: 5.6, h: 4.6, rectRadius: 0.12, fill: { color: CARD }, line: { type: "none" } });
  s.addText("REWARD FUNCTION", { x: 7.4, y: 2.0, w: 4.8, h: 0.35, fontFace: "Consolas", fontSize: 13, color: MUTED_D });
  s.addText("reward =", { x: 7.4, y: 2.5, w: 4.8, h: 0.4, fontFace: "Consolas", fontSize: 20, color: TEXT, bold: true });
  s.addText("accuracy", { x: 7.4, y: 2.95, w: 4.8, h: 0.4, fontFace: "Consolas", fontSize: 20, color: TEAL, bold: true });
  s.addText("\u2212 \u03BB \u00D7 token_cost", { x: 7.4, y: 3.4, w: 4.8, h: 0.4, fontFace: "Consolas", fontSize: 20, color: AMBER, bold: true });
  s.addText("\u2212 \u03BC \u00D7 latency", { x: 7.4, y: 3.85, w: 4.8, h: 0.4, fontFace: "Consolas", fontSize: 20, color: AMBER, bold: true });
  s.addText("Squashed to [0,1] and fed directly into the Beta-distribution update — so the router optimizes for getting it right, cheaply and fast, not accuracy alone.", {
    x: 7.4, y: 4.5, w: 4.8, h: 1.6, fontFace: "Calibri", fontSize: 12.5, color: MUTED,
  });
  pageNum(s, 4);
}

// ---------- Slide 5: Contextual routing ----------
{
  const s = bgSlide();
  s.addText("Context is the difference-maker", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });
  s.addText("The bandit doesn't learn one best model — it learns a separate belief per task type, so routing adapts to what's actually being asked.", {
    x: 0.7, y: 1.35, w: 11.2, h: 0.6, fontFace: "Calibri", fontSize: 15, color: MUTED,
  });

  const rows = [
    ["Code", "Routes toward the model with the strongest code accuracy per dollar"],
    ["Math", "Routes toward the highest-accuracy model — correctness matters most here"],
    ["QA", "Routes toward cheap models once they prove easy questions don't need more"],
    ["Creative", "Spreads across mid-tier models — no single arm dominates"],
  ];
  let y = 2.5;
  rows.forEach((r) => {
    s.addShape("roundRect", { x: 0.7, y, w: 11.9, h: 0.95, rectRadius: 0.08, fill: { color: CARD }, line: { type: "none" } });
    s.addShape("roundRect", { x: 0.7, y, w: 2.2, h: 0.95, rectRadius: 0.08, fill: { color: CARD2 }, line: { type: "none" } });
    s.addText(r[0], { x: 0.7, y, w: 2.2, h: 0.95, align: "center", valign: "middle", fontFace: "Arial", bold: true, fontSize: 16, color: AMBER });
    s.addText(r[1], { x: 3.1, y, w: 9.3, h: 0.95, valign: "middle", fontFace: "Calibri", fontSize: 14, color: TEXT, margin: 0 });
    y += 1.12;
  });
  pageNum(s, 5);
}

// ---------- Slide 6: Results ----------
{
  const s = bgSlide();
  s.addText("It learns — and it saves money", {
    x: 0.7, y: 0.5, w: 11.5, h: 0.8, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });
  s.addText("2,000 simulated queries against 4 model profiles", {
    x: 0.7, y: 1.2, w: 11.0, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED,
  });

  const stats = [
    ["92.8%", "cost saved vs. always\nusing the largest model"],
    ["77.5%", "overall accuracy"],
    ["~350", "queries to converge on\nstable routing per task"],
  ];
  let x = 0.7;
  stats.forEach((st) => {
    s.addShape("roundRect", { x, y: 1.8, w: 3.75, h: 1.6, rectRadius: 0.1, fill: { color: CARD }, line: { type: "none" } });
    s.addText(st[0], { x: x + 0.25, y: 1.92, w: 3.3, h: 0.7, fontFace: "Arial", bold: true, fontSize: 34, color: AMBER });
    s.addText(st[1], { x: x + 0.25, y: 2.6, w: 3.3, h: 0.7, fontFace: "Calibri", fontSize: 12, color: MUTED });
    x += 4.0;
  });

  s.addImage({ path: "dashboard.png", x: 0.7, y: 3.65, w: 11.9, h: 3.55 });
  pageNum(s, 6);
}

// ---------- Slide 7: Real-world validation (honest) ----------
{
  const s = bgSlide();
  s.addText("Validated against real models, honestly", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 32, color: TEXT,
  });

  s.addShape("roundRect", { x: 0.7, y: 1.6, w: 5.7, h: 4.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: TEAL, width: 1.5 } });
  s.addText("WHAT'S REAL", { x: 1.05, y: 1.9, w: 5.0, h: 0.35, fontFace: "Consolas", fontSize: 13, color: TEAL });
  s.addText([
    { text: "Same bandit, real API calls\n", options: { bold: true, fontSize: 16, color: TEXT, breakLine: true } },
    { text: "Runs against 4 free-tier models on OpenRouter (Llama 3.3 70B, Qwen3 Coder, GPT-OSS 20B, Llama 3.2 3B) — graded against a hand-labeled answer key, not simulated.", options: { fontSize: 13, color: MUTED } },
  ], { x: 1.05, y: 2.35, w: 5.0, h: 3.7, fontFace: "Calibri", lineSpacingMultiple: 1.3 });

  s.addShape("roundRect", { x: 6.85, y: 1.6, w: 5.75, h: 4.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: AMBER, width: 1.5 } });
  s.addText("WHAT'S ROUGH", { x: 7.2, y: 1.9, w: 5.0, h: 0.35, fontFace: "Consolas", fontSize: 13, color: AMBER });
  s.addText([
    { text: "Free-tier reality\n", options: { bold: true, fontSize: 16, color: TEXT, breakLine: true } },
    { text: "Free model slugs rotate without notice, and popular models hit shared-pool rate limits independent of your own usage. The code makes real, correct calls — a full clean run just takes patience on the free tier.", options: { fontSize: 13, color: MUTED } },
  ], { x: 7.2, y: 2.35, w: 5.0, h: 3.7, fontFace: "Calibri", lineSpacingMultiple: 1.3 });

  pageNum(s, 7);
}

// ---------- Slide 8: Tech stack ----------
{
  const s = bgSlide();
  s.addText("Tech stack", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });

  const stack = [
    ["Python", "core implementation"],
    ["Thompson Sampling", "contextual multi-armed bandit"],
    ["NumPy", "reward computation, rolling stats"],
    ["Matplotlib", "dashboard visualizations"],
    ["OpenRouter API", "live free-tier model routing"],
    ["Requests", "HTTP client for real API calls"],
  ];
  let col = 0, row = 0;
  const cx = [0.7, 4.6, 8.5], cw = 3.7;
  stack.forEach((it, i) => {
    col = i % 3; row = Math.floor(i / 3);
    const x = cx[col], y = 2.0 + row * 1.9;
    s.addShape("roundRect", { x, y, w: cw, h: 1.55, rectRadius: 0.1, fill: { color: CARD }, line: { type: "none" } });
    s.addShape("ellipse", { x: x + 0.3, y: y + 0.28, w: 0.4, h: 0.4, fill: { color: "2C3040" }, line: { color: TEAL, width: 1.5 } });
    s.addText((i + 1).toString(), { x: x + 0.3, y: y + 0.28, w: 0.4, h: 0.4, align: "center", valign: "middle", fontFace: "Consolas", bold: true, fontSize: 14, color: TEAL });
    s.addText(it[0], { x: x + 0.3, y: y + 0.78, w: cw - 0.6, h: 0.4, fontFace: "Arial", bold: true, fontSize: 15, color: TEXT });
    s.addText(it[1], { x: x + 0.3, y: y + 1.15, w: cw - 0.6, h: 0.35, fontFace: "Calibri", fontSize: 11, color: MUTED });
  });
  pageNum(s, 8);
}

// ---------- Slide 9: What's next ----------
{
  const s = bgSlide();
  s.addText("If I had more time", {
    x: 0.7, y: 0.55, w: 11.5, h: 0.9, fontFace: "Arial", bold: true, fontSize: 34, color: TEXT,
  });

  const next = [
    ["Harden the live integration", "retry logic per arm, fallback when a free model is congested"],
    ["Real embeddings + LinUCB", "swap task-type context for query embeddings — a genuine contextual bandit"],
    ["FastAPI service", "wrap the router as a live endpoint, not a batch script"],
  ];
  let y = 2.0;
  next.forEach((n, i) => {
    s.addShape("roundRect", { x: 0.7, y, w: 11.9, h: 1.35, rectRadius: 0.1, fill: { color: CARD }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 1.0, y: y + 0.3, w: 0.7, h: 0.75, fontFace: "Arial", bold: true, fontSize: 32, color: AMBER });
    s.addText(n[0], { x: 2.0, y: y + 0.2, w: 9.9, h: 0.45, fontFace: "Arial", bold: true, fontSize: 17, color: TEXT });
    s.addText(n[1], { x: 2.0, y: y + 0.68, w: 9.9, h: 0.5, fontFace: "Calibri", fontSize: 13, color: MUTED });
    y += 1.6;
  });
  pageNum(s, 9);
}

// ---------- Slide 10: Closing ----------
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addText("BanditRoute", {
    x: 0.9, y: 2.9, w: 11.5, h: 1.1, fontFace: "Arial", bold: true, fontSize: 54, color: TEXT,
  });
  s.addText("A reinforcement-learning router that learns which model to call.", {
    x: 0.95, y: 3.95, w: 10.5, h: 0.5, fontFace: "Calibri", fontSize: 18, color: MUTED,
  });
  s.addText("Thanks for watching — happy to dig into the code, the reward math, or the live demo.", {
    x: 0.95, y: 4.6, w: 10.5, h: 0.5, fontFace: "Calibri", fontSize: 14, italic: true, color: TEAL,
  });
}

pres.writeFile({ fileName: "banditroute_deck.pptx" }).then(() => {
  console.log("done");
});
