// Zikr Circle Mini App: My Day checklist + zikr counter. Vanilla JS, no build step.
(function () {
  'use strict';

  var tg = window.Telegram && window.Telegram.WebApp;
  var I18N = JSON.parse(document.getElementById('i18n').textContent);
  var lang = 'am';

  var COUNTER_BATCH = 10; // taps per save
  var COUNTER_IDLE_MS = 2000; // save after this long without taps
  var QUANTITY_DEBOUNCE_MS = 600;

  var goals = []; // [{key, label, type, target, groups, amount}]
  var counterGoal = null;
  var pendingTaps = 0;
  var counterTimer = null;
  var saveQueue = Promise.resolve(); // keeps writes in order

  // --- helpers ---------------------------------------------------------

  function t(key, vars) {
    var s = (I18N[lang] && I18N[lang][key]) || I18N.am[key] || key;
    Object.keys(vars || {}).forEach(function (k) {
      s = s.split('{' + k + '}').join(String(vars[k]));
    });
    return s;
  }

  function $(id) {
    return document.getElementById(id);
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function goalLabel(goal) {
    return (I18N[lang] && I18N[lang]['goal_' + goal.key]) || goal.label;
  }

  function isDone(goal) {
    return goal.amount >= goal.target;
  }

  function applyI18n() {
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(function (node) {
      node.textContent = t(node.getAttribute('data-i18n'));
    });
  }

  function show(viewId) {
    document.querySelectorAll('.view').forEach(function (v) {
      v.hidden = v.id !== viewId;
    });
  }

  function showMessage(text) {
    $('message').textContent = text;
    show('view-message');
  }

  var toastTimer = null;
  function toast(text) {
    var node = $('toast');
    node.textContent = text;
    node.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      node.hidden = true;
    }, 2500);
  }

  function haptic(kind) {
    if (!tg || !tg.HapticFeedback) return;
    if (kind === 'success') tg.HapticFeedback.notificationOccurred('success');
    else if (kind === 'select') tg.HapticFeedback.selectionChanged();
    else tg.HapticFeedback.impactOccurred('light');
  }

  // --- API -------------------------------------------------------------

  function api(path, body, keepalive) {
    var opts = {
      method: body ? 'POST' : 'GET',
      headers: { 'X-Telegram-Init-Data': tg.initData },
      keepalive: !!keepalive,
    };
    if (body) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    return fetch(path, opts).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.error || 'http_' + res.status);
        return data;
      });
    });
  }

  /** Queue a write so it runs after earlier ones; resolves with the server's amount. */
  function saveEntry(goal, change, keepalive) {
    var body = Object.assign({ goal_key: goal.key }, change);
    var run = function () {
      return api('api/entry.php', body, keepalive);
    };
    var result = saveQueue.then(run, run);
    saveQueue = result.catch(function () {});
    return result.then(function (data) {
      return data.amount;
    });
  }

  // --- My Day ----------------------------------------------------------

  function renderSummary() {
    var done = goals.filter(isDone).length;
    $('day-progress').textContent =
      goals.length && done === goals.length
        ? t('all_done')
        : t('done_count', { done: done, total: goals.length });
    $('day-bar').style.width = goals.length ? (100 * done) / goals.length + '%' : '0';
  }

  function renderDay() {
    var list = $('goal-list');
    list.textContent = '';
    $('day-empty').hidden = goals.length > 0;
    goals.forEach(function (goal) {
      list.appendChild(renderGoal(goal));
    });
    renderSummary();
  }

  function renderGoal(goal) {
    var li = el('li', 'goal goal-' + goal.type + (isDone(goal) ? ' is-done' : ''));
    var check = el('span', 'check', isDone(goal) ? '✓' : '');
    var label = el('span', 'goal-label', goalLabel(goal));
    li.appendChild(check);
    li.appendChild(label);

    if (goal.type === 'checkbox') {
      li.setAttribute('role', 'checkbox');
      li.setAttribute('aria-checked', String(isDone(goal)));
      li.tabIndex = 0;
      li.addEventListener('click', function () {
        toggleCheckbox(goal);
      });
    } else if (goal.type === 'counter') {
      li.appendChild(el('span', 'goal-amount', goal.amount + ' / ' + goal.target));
      li.appendChild(el('span', 'chevron', '›'));
      li.setAttribute('role', 'button');
      li.setAttribute('aria-label', goalLabel(goal) + ' — ' + t('open_counter'));
      li.tabIndex = 0;
      li.addEventListener('click', function () {
        openCounter(goal);
      });
    } else {
      li.appendChild(renderStepper(goal));
    }
    return li;
  }

  function refreshGoal(goal) {
    var index = goals.indexOf(goal);
    var old = $('goal-list').children[index];
    if (old) old.replaceWith(renderGoal(goal));
    renderSummary();
  }

  function toggleCheckbox(goal) {
    var previous = goal.amount;
    goal.amount = isDone(goal) ? 0 : 1;
    haptic(goal.amount ? 'success' : 'select');
    refreshGoal(goal);
    saveEntry(goal, { amount: goal.amount }).catch(function () {
      goal.amount = previous;
      refreshGoal(goal);
      toast(t('save_failed'));
    });
  }

  function renderStepper(goal) {
    var wrap = el('span', 'stepper');
    var minus = el('button', 'step', '−');
    var value = el('span', 'step-value', goal.amount + ' / ' + goal.target);
    var plus = el('button', 'step', '+');
    minus.type = plus.type = 'button';
    minus.setAttribute('aria-label', '−1');
    plus.setAttribute('aria-label', '+1');
    var timer = null;
    var saved = goal.amount;

    function change(step) {
      var next = Math.max(0, goal.amount + step);
      if (next === goal.amount) return;
      var wasDone = isDone(goal);
      goal.amount = next;
      haptic(!wasDone && isDone(goal) ? 'success' : 'select');
      value.textContent = goal.amount + ' / ' + goal.target;
      wrap.parentNode.classList.toggle('is-done', isDone(goal));
      wrap.parentNode.querySelector('.check').textContent = isDone(goal) ? '✓' : '';
      renderSummary();
      clearTimeout(timer);
      timer = setTimeout(function () {
        saveEntry(goal, { amount: goal.amount })
          .then(function (amount) {
            saved = amount;
          })
          .catch(function () {
            goal.amount = saved;
            refreshGoal(goal);
            toast(t('save_failed'));
          });
      }, QUANTITY_DEBOUNCE_MS);
    }

    minus.addEventListener('click', function (e) {
      e.stopPropagation();
      change(-1);
    });
    plus.addEventListener('click', function (e) {
      e.stopPropagation();
      change(1);
    });
    wrap.appendChild(minus);
    wrap.appendChild(value);
    wrap.appendChild(plus);
    return wrap;
  }

  // --- Zikr counter ----------------------------------------------------

  function renderCounter() {
    $('counter-count').textContent = counterGoal.amount;
    $('counter-done').hidden = !isDone(counterGoal);
    $('counter-tap').classList.toggle('is-done', isDone(counterGoal));
  }

  function openCounter(goal) {
    counterGoal = goal;
    $('counter-label').textContent = goalLabel(goal);
    $('counter-target').textContent = t('target', { target: goal.target });
    renderCounter();
    show('view-counter');
    tg.BackButton.show();
  }

  function closeCounter() {
    flushTaps(false);
    counterGoal = null;
    tg.BackButton.hide();
    renderDay();
    show('view-day');
  }

  function flushTaps(keepalive) {
    clearTimeout(counterTimer);
    if (!counterGoal || pendingTaps === 0) return;
    var goal = counterGoal;
    var delta = pendingTaps;
    pendingTaps = 0;
    saveEntry(goal, { delta: delta }, keepalive).catch(function () {
      pendingTaps += delta; // retried with the next batch
      toast(t('save_failed'));
    });
  }

  function onTap() {
    var wasDone = isDone(counterGoal);
    counterGoal.amount += 1;
    pendingTaps += 1;
    haptic(!wasDone && isDone(counterGoal) ? 'success' : 'tap');
    renderCounter();
    clearTimeout(counterTimer);
    if (pendingTaps >= COUNTER_BATCH) {
      flushTaps(false);
    } else {
      counterTimer = setTimeout(function () {
        flushTaps(false);
      }, COUNTER_IDLE_MS);
    }
  }

  function onReset() {
    var goal = counterGoal;
    tg.showConfirm(t('reset_confirm'), function (ok) {
      if (!ok || counterGoal !== goal) return;
      clearTimeout(counterTimer);
      pendingTaps = 0;
      goal.amount = 0;
      renderCounter();
      saveEntry(goal, { amount: 0 }).catch(function () {
        toast(t('save_failed'));
      });
    });
  }

  // --- startup ---------------------------------------------------------

  function start() {
    if (!tg || !tg.initData) {
      showMessage(t('open_in_telegram'));
      return;
    }
    tg.ready();
    tg.expand();

    $('counter-tap').addEventListener('click', onTap);
    $('counter-reset').addEventListener('click', onReset);
    tg.BackButton.onClick(closeCounter);
    // Save pending taps whenever the app is hidden or closed.
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') flushTaps(true);
    });
    window.addEventListener('pagehide', function () {
      flushTaps(true);
    });

    api('api/day.php')
      .then(function (data) {
        lang = I18N[data.user.lang] ? data.user.lang : 'am';
        goals = data.goals;
        applyI18n();
        if (data.group_id) {
          // Group settings (owner only) arrive in Phase 3.
          $('notice').textContent = t('group_settings_soon');
          $('notice').hidden = false;
        }
        renderDay();
        show('view-day');
      })
      .catch(function (err) {
        applyI18n();
        showMessage(t(err.message === 'unauthorized' ? 'open_in_telegram' : 'load_failed'));
      });
  }

  start();
})();
