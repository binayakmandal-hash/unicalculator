// ----- Theme toggle: saves the choice in the browser -----
const themeBtn = document.getElementById("theme-btn");
const root = document.documentElement;

function showIcon() {
  themeBtn.textContent = root.dataset.theme === "dark" ? "☀" : "☾";
}
showIcon();

themeBtn.addEventListener("click", () => {
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", root.dataset.theme);
  showIcon();
});

// ----- Tool tabs: click a card, show its panel, hide the others -----
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".panel");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.toggle("active", t === tab));
    panels.forEach((p) => p.classList.toggle("active", p.id === tab.dataset.tab));
  });
});

// ----- BMI: switch between US and Metric fields -----
const unitButtons = document.querySelectorAll(".seg button");
const unitBoxes = document.querySelectorAll(".units");
const unitInput = document.getElementById("unit");   // hidden field Python reads

unitButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    unitInput.value = btn.dataset.unit;
    unitButtons.forEach((b) => b.classList.toggle("active", b === btn));
    unitBoxes.forEach((box) => box.classList.toggle("active", box.dataset.unit === btn.dataset.unit));
  });
});

// ----- Grades: add / remove subject rows -----
const subjList = document.getElementById("subj-list");
document.querySelector(".add-row").addEventListener("click", () => {
  const row = subjList.querySelector(".subj-row").cloneNode(true);
  row.querySelectorAll("input").forEach((i) => (i.value = i.name === "outof" ? "100" : ""));
  subjList.appendChild(row);
  row.querySelector("input").focus();
});
subjList.addEventListener("click", (e) => {
  if (!e.target.classList.contains("del-row")) return;
  const rows = subjList.querySelectorAll(".subj-row");
  const row = e.target.closest(".subj-row");
  if (rows.length > 1) row.remove();
  else row.querySelectorAll("input").forEach((i) => (i.value = i.name === "outof" ? "100" : ""));
});

// After a form submit, this should stop the browser from re-sending
// the form when you press refresh (matters for deposit and withdraw)
if (window.history.replaceState) {
  window.history.replaceState(null, "", window.location.href);
}