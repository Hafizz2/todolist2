// CyberBuddy dashboard - reads the same plan as the Telegram bot.
var KEY = "cyberbuddy-progress";
var plan, challenges, state, viewDay, puzzle;

function blankState() {
  return { current_day: 1, completed: {}, streak: 0, best_streak: 0, last_done_date: null, solved: [], tasks: {} };
}

function loadLocal() {
  try {
    return Object.assign(blankState(), JSON.parse(localStorage.getItem(KEY)) || {});
  } catch (e) {
    return blankState();
  }
}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {
    // storage blocked (private mode) - progress just won't persist
  }
}

// Merge the bot's progress (committed by GitHub Actions) into the browser's.
function mergeBot(bot) {
  Object.assign(state.completed, bot.completed || {});
  state.current_day = Math.max(state.current_day, bot.current_day || 1);
  state.solved = Array.from(new Set(state.solved.concat(bot.solved || [])));
  if ((bot.last_done_date || "") > (state.last_done_date || "")) {
    state.last_done_date = bot.last_done_date;
    state.streak = bot.streak;
  }
  state.best_streak = Math.max(state.best_streak, bot.best_streak || 0);
}

function isoToday() {
  var d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function isoYesterday() {
  var d = new Date();
  d.setDate(d.getDate() - 1);
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function el(tag, attrs, children) {
  var node = document.createElement(tag);
  Object.keys(attrs || {}).forEach(function (k) {
    if (k === "text") node.textContent = attrs[k];
    else if (k === "class") node.className = attrs[k];
    else node.setAttribute(k, attrs[k]);
  });
  (children || []).forEach(function (c) {
    node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  });
  return node;
}

// Turn `code` spans into <code> elements without using innerHTML.
function rich(text) {
  var span = el("span");
  text.split(/(`[^`]+`)/).forEach(function (part) {
    if (part.startsWith("`") && part.endsWith("`") && part.length > 1) span.appendChild(el("code", { text: part.slice(1, -1) }));
    else if (part) span.appendChild(document.createTextNode(part));
  });
  return span;
}

function renderStats() {
  var total = plan.days.length;
  var done = Object.keys(state.completed).length;
  document.getElementById("stat-done").textContent = done;
  document.getElementById("stat-streak").textContent = state.streak;
  document.getElementById("stat-solved").textContent = state.solved.length;
  document.getElementById("progress-bar").style.width = (100 * done) / total + "%";
  document.getElementById("progress-label").textContent =
    done + " of " + total + " days complete · currently on day " + state.current_day;
}

function renderLesson() {
  var d = plan.days[viewDay - 1];
  var box = document.getElementById("lesson");
  box.replaceChildren();

  var label = viewDay === state.current_day ? "Today · " : "Preview · ";
  box.appendChild(el("span", { class: "phase-tag", text: label + "Day " + d.day + "/" + plan.days.length }));
  box.appendChild(el("p", { class: "sub", text: d.phase_name }));
  box.appendChild(el("h2", { class: "lesson-title", text: (state.completed[d.day] ? "✅ " : "") + d.title }));

  var tasks = el("ul", { class: "tasks" });
  d.tasks.forEach(function (t, i) {
    var id = d.day + ":" + i;
    var cb = el("input", { type: "checkbox", "aria-label": "Task " + (i + 1) });
    cb.checked = !!state.tasks[id];
    var li = el("li", { class: cb.checked ? "checked" : "" }, [cb, rich(t)]);
    cb.addEventListener("change", function () {
      state.tasks[id] = cb.checked;
      li.classList.toggle("checked", cb.checked);
      save();
    });
    tasks.appendChild(li);
  });
  box.appendChild(el("h3", { text: "📋 Tasks" }));
  box.appendChild(tasks);

  if (d.links.length) {
    box.appendChild(el("h3", { text: "🔗 Links" }));
    var links = el("ul", { class: "links" });
    d.links.forEach(function (l) {
      links.appendChild(el("li", {}, [el("a", { href: l.url, target: "_blank", rel: "noopener", text: l.name })]));
    });
    box.appendChild(links);
  }
  if (d.tools.length) {
    var tools = el("p", {}, [el("strong", { text: "🧰 Tools: " })]);
    d.tools.forEach(function (t, i) {
      if (i) tools.appendChild(document.createTextNode(", "));
      tools.appendChild(rich(t));
    });
    box.appendChild(tools);
  }
  if (d.challenge) {
    box.appendChild(el("div", { class: "challenge" }, [el("strong", { text: "🎯 Challenge: " }), rich(d.challenge)]));
  }

  var row = el("div", { class: "row" });
  if (viewDay === state.current_day) {
    row.appendChild(button("✅ Mark day done", "", markDone));
    row.appendChild(button("Skip", "ghost", function () { move(1); }));
    row.appendChild(button("Back", "ghost", function () { move(-1); }));
  } else {
    row.appendChild(button("Make this my current day", "", function () {
      state.current_day = viewDay;
      save();
      renderAll();
    }));
    row.appendChild(button("Back to today", "ghost", function () {
      viewDay = state.current_day;
      renderLesson();
    }));
  }
  box.appendChild(row);
}

function button(text, cls, onClick) {
  var b = el("button", { type: "button", class: cls, text: text });
  b.addEventListener("click", onClick);
  return b;
}

function markDone() {
  var today = isoToday();
  state.completed[state.current_day] = today;
  if (state.last_done_date !== today) {
    state.streak = state.last_done_date === isoYesterday() ? state.streak + 1 : 1;
    state.last_done_date = today;
  }
  state.best_streak = Math.max(state.best_streak, state.streak);
  if (state.current_day < plan.days.length) state.current_day += 1;
  save();
  renderAll();
}

function move(step) {
  state.current_day = Math.min(plan.days.length, Math.max(1, state.current_day + step));
  save();
  renderAll();
}

function renderPhases() {
  var box = document.getElementById("phases");
  box.replaceChildren();
  Object.keys(plan.phases).forEach(function (key) {
    var days = plan.days.filter(function (d) { return d.phase === key; });
    var done = days.filter(function (d) { return state.completed[d.day]; }).length;
    var list = el("ul", { class: "day-list" });
    days.forEach(function (d) {
      var mark = state.completed[d.day] ? "✅ " : d.review ? "📝 " : "▫️ ";
      var li = el("li", { class: d.day === state.current_day ? "current" : "", text: mark + "Day " + d.day + " · " + d.title });
      li.addEventListener("click", function () {
        viewDay = d.day;
        renderLesson();
        document.getElementById("lesson").scrollIntoView({ behavior: "smooth" });
      });
      list.appendChild(li);
    });
    var open = days.some(function (d) { return d.day === state.current_day; });
    var details = el("details", {}, [
      el("summary", {}, [plan.phases[key] + " ", el("small", { text: "(" + done + "/" + days.length + ")" })]),
      list,
    ]);
    details.open = open;
    box.appendChild(details);
  });
}

function newPuzzle() {
  var unsolved = challenges.filter(function (c) { return state.solved.indexOf(c.id) === -1; });
  var pool = unsolved.length ? unsolved : challenges;
  puzzle = pool[Math.floor(Math.random() * pool.length)];
  var box = document.getElementById("puzzle");
  box.replaceChildren(
    el("p", { class: "sub", text: "#" + puzzle.id + " · " + puzzle.category + " " + "⭐".repeat(puzzle.difficulty) }),
    el("p", {}, [rich(puzzle.prompt)])
  );
  if (puzzle.tool) box.appendChild(el("p", { class: "sub" }, ["🧰 Try: ", rich(puzzle.tool)]));
  document.getElementById("puzzle-result").textContent = "";
  document.getElementById("puzzle-answer").value = "";
}

async function sha256(text) {
  var buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
}

async function checkPuzzle(e) {
  e.preventDefault();
  var answer = document.getElementById("puzzle-answer").value.trim().toLowerCase().split(/\s+/).join(" ");
  var result = document.getElementById("puzzle-result");
  if (!answer) return;
  var ok = puzzle.answers.indexOf(await sha256(answer)) !== -1;
  if (ok) {
    if (state.solved.indexOf(puzzle.id) === -1) state.solved.push(puzzle.id);
    save();
    renderStats();
    result.textContent = "🎉 Correct! Hit 'New puzzle' for another.";
  } else {
    result.textContent = "❌ Not quite - try again or take a hint.";
  }
}

function renderAll() {
  viewDay = state.current_day;
  renderStats();
  renderLesson();
  renderPhases();
}

async function init() {
  state = loadLocal();
  var responses = await Promise.all([
    fetch("../cyberbot/curriculum.json").then(function (r) { return r.json(); }),
    fetch("../cyberbot/challenges.json").then(function (r) { return r.json(); }),
    fetch("../cyberbot/state.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }),
  ]);
  plan = responses[0];
  challenges = responses[1].challenges;
  mergeBot(responses[2]);
  save();

  var source = document.getElementById("source");
  source.href = plan.source;

  document.getElementById("puzzle-form").addEventListener("submit", checkPuzzle);
  document.getElementById("puzzle-next").addEventListener("click", newPuzzle);
  document.getElementById("puzzle-hint").addEventListener("click", function () {
    document.getElementById("puzzle-result").textContent = "💡 " + puzzle.hint;
  });
  document.getElementById("reset").addEventListener("click", function () {
    if (!confirm("Reset progress saved in this browser? (Your bot's progress is not affected.)")) return;
    state = blankState();
    save();
    renderAll();
  });

  renderAll();
  newPuzzle();
}

init().catch(function (err) {
  document.getElementById("lesson").textContent =
    "Couldn't load the plan (" + err.message + "). Open this page through a web server or GitHub Pages, not as a file.";
});
