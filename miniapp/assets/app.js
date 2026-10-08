// My Day checklist + zikr counter, and app startup. Uses window.ZC (core.js).
(function () {
  'use strict';

  var ZC = window.ZC;
  var tg = ZC.tg;
  var t = ZC.t;
  var $ = ZC.$;
  var el = ZC.el;

  var COUNTER_BATCH = 10; // taps per save
  var COUNTER_IDLE_MS = 2000; // save after this long without taps
  var QUANTITY_DEBOUNCE_MS = 600;

  var goals = []; // [{key, label, type, target, groups, amount}]
  var counterGoal = null;
  var pendingTaps = 0;
  var counterTimer = null;

  function isDone(goal) {
    return goal.amount >= goal.target;
  }

  function saveEntry(goal, change, keepalive) {
    var body = Object.assign({ goal_key: goal.key }, change);
    return ZC.write('entry.php', body, keepalive).then(function (data) {
      return data.amount;
    });
  }

  // --- My Day ----------------------------------------------------------

  function loadDay() {
    return ZC.api('day.php').then(function (data) {
      goals = data.goals;
      return data;
    });
  }

  function showDay(notice) {
    $('notice').textContent = notice || '';
    $('notice').hidden = !notice;
    ZC.setBack(null);
    renderDay();
    ZC.show('view-day');
  }

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
    li.appendChild(el('span', 'check', isDone(goal) ? '✓' : ''));
    li.appendChild(el('span', 'goal-label', ZC.goalLabel(goal)));

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
      li.setAttribute('aria-label', ZC.goalLabel(goal) + ' — ' + t('open_counter'));
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
    var old = $('goal-list').children[goals.indexOf(goal)];
    if (old) old.replaceWith(renderGoal(goal));
    renderSummary();
  }

  function toggleCheckbox(goal) {
    var previous = goal.amount;
    goal.amount = isDone(goal) ? 0 : 1;
    ZC.haptic(goal.amount ? 'success' : 'select');
    refreshGoal(goal);
    saveEntry(goal, { amount: goal.amount }).catch(function () {
      goal.amount = previous;
      refreshGoal(goal);
      ZC.toast(t('save_failed'));
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
      ZC.haptic(!wasDone && isDone(goal) ? 'success' : 'select');
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
            ZC.toast(t('save_failed'));
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
    $('counter-label').textContent = ZC.goalLabel(goal);
    $('counter-target').textContent = t('target', { target: goal.target });
    renderCounter();
    ZC.show('view-counter');
    ZC.setBack(closeCounter);
  }

  function closeCounter() {
    flushTaps(false);
    counterGoal = null;
    showDay();
  }

  function flushTaps(keepalive) {
    clearTimeout(counterTimer);
    if (!counterGoal || pendingTaps === 0) return;
    var goal = counterGoal;
    var delta = pendingTaps;
    pendingTaps = 0;
    saveEntry(goal, { delta: delta }, keepalive).catch(function () {
      pendingTaps += delta; // retried with the next batch
      ZC.toast(t('save_failed'));
    });
  }

  function onTap() {
    var wasDone = isDone(counterGoal);
    counterGoal.amount += 1;
    pendingTaps += 1;
    ZC.haptic(!wasDone && isDone(counterGoal) ? 'success' : 'tap');
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
        ZC.toast(t('save_failed'));
      });
    });
  }

  // --- startup ---------------------------------------------------------

  /** Leaving group settings: reload My Day, since goals may have changed. */
  ZC.showDay = function () {
    loadDay()
      .then(function () {
        showDay();
      })
      .catch(function () {
        ZC.showMessage(t('load_failed'));
      });
  };

  function start() {
    if (!tg || !tg.initData) {
      ZC.showMessage(t('open_in_telegram'));
      return;
    }
    tg.ready();
    tg.expand();

    $('counter-tap').addEventListener('click', onTap);
    $('counter-reset').addEventListener('click', onReset);
    // Save pending taps whenever the app is hidden or closed.
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') flushTaps(true);
    });
    window.addEventListener('pagehide', function () {
      flushTaps(true);
    });

    loadDay()
      .then(function (data) {
        ZC.setLang(data.user.lang);
        if (!data.group_id) {
          showDay();
          return;
        }
        // Opened from a group's /setup link: owners get its settings, everyone else My Day.
        ZC.openSettings(data.group_id).catch(function (err) {
          showDay(err.message === 'not_owner' ? t('not_owner') : '');
        });
      })
      .catch(function (err) {
        ZC.setLang('am');
        ZC.showMessage(t(err.message === 'unauthorized' ? 'open_in_telegram' : 'load_failed'));
      });
  }

  start();
})();
