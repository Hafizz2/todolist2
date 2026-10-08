// Group Settings (owner only): goals, schedule, privacy. Uses window.ZC (core.js).
// The server enforces ownership; this screen is only shown when the API allows it.
(function () {
  'use strict';

  var ZC = window.ZC;
  var tg = ZC.tg;
  var t = ZC.t;
  var $ = ZC.$;
  var el = ZC.el;

  var CUSTOM = '__custom';
  var PRIVACY_MODES = ['completion', 'group_total_only', 'full_counts'];
  var GOAL_TYPES = ['counter', 'checkbox', 'quantity'];

  var state = null; // {group, goals, presets, timezones}
  var initialized = false;

  ZC.openSettings = function (groupId) {
    return ZC.api('group.php?id=' + encodeURIComponent(groupId)).then(function (data) {
      state = data;
      init();
      render();
      ZC.show('view-settings');
      ZC.setBack(close);
    });
  };

  function close() {
    tg.MainButton.hide();
    ZC.showDay();
  }

  function errorText(err) {
    var key = 'err_' + err.message;
    var text = t(key);
    return text === key ? t('save_failed') : text;
  }

  function fail(err) {
    ZC.haptic('error');
    ZC.toast(errorText(err));
  }

  function init() {
    if (initialized) return;
    initialized = true;
    $('add-preset').addEventListener('change', onPresetChange);
    $('add-type').addEventListener('change', syncAddTarget);
    $('add-goal').addEventListener('click', addGoal);
    ['set-morning', 'set-night', 'set-timezone'].forEach(function (id) {
      $(id).addEventListener('input', markDirty);
      $(id).addEventListener('change', markDirty);
    });
    tg.MainButton.onClick(saveSettings);
  }

  function render() {
    $('settings-title').textContent = state.group.title;
    $('add-label').placeholder = t('goal_name');
    renderGoals();
    renderAddForm();
    renderSchedule();
    renderPrivacy();
    tg.MainButton.hide();
  }

  // --- goals -----------------------------------------------------------

  function renderGoals() {
    var list = $('settings-goals');
    list.textContent = '';
    state.goals.forEach(function (goal) {
      list.appendChild(renderGoalRow(goal));
    });
  }

  function isPreset(goal) {
    return goal.key.indexOf('custom_') !== 0;
  }

  function renderGoalRow(goal) {
    var li = el('li', 'goal setting-goal' + (goal.active ? '' : ' is-off'));
    var main = el('div', 'setting-main');

    // Well-known goals are shown translated by key, so only custom names are editable.
    if (isPreset(goal)) {
      main.appendChild(el('span', 'goal-label', ZC.goalLabel(goal)));
    } else {
      var label = el('input', 'inline-input');
      label.type = 'text';
      label.value = goal.label;
      label.maxLength = 100;
      label.setAttribute('aria-label', t('goal_name'));
      label.addEventListener('change', function () {
        updateGoal(goal, { label: label.value });
      });
      main.appendChild(label);
    }
    main.appendChild(el('span', 'hint small', goal.active ? t('type_' + goal.type) : t('goal_off')));
    li.appendChild(main);

    if (goal.type !== 'checkbox') {
      var target = el('input', 'target-input');
      target.type = 'number';
      target.min = '1';
      target.max = '100000';
      target.inputMode = 'numeric';
      target.value = goal.target;
      target.setAttribute('aria-label', t('daily_target'));
      target.addEventListener('change', function () {
        updateGoal(goal, { target: parseInt(target.value, 10) });
      });
      li.appendChild(target);
    }

    var toggle = el('label', 'switch');
    var box = el('input');
    box.type = 'checkbox';
    box.checked = goal.active;
    box.setAttribute('aria-label', ZC.goalLabel(goal));
    box.addEventListener('change', function () {
      ZC.haptic('select');
      updateGoal(goal, { active: box.checked });
    });
    toggle.appendChild(box);
    toggle.appendChild(el('span', 'slider'));
    li.appendChild(toggle);
    return li;
  }

  function updateGoal(goal, patch) {
    var next = Object.assign({}, goal, patch);
    if (!Number.isInteger(next.target)) {
      fail(new Error('invalid_target'));
      renderGoals();
      return;
    }
    ZC.write('goals.php', {
      group_id: state.group.id,
      action: 'update',
      goal_id: goal.id,
      label: next.label,
      target: next.target,
      active: next.active,
    })
      .then(function (data) {
        state.goals = data.goals;
        renderGoals();
        renderAddForm();
      })
      .catch(function (err) {
        fail(err);
        renderGoals(); // back to the saved values
      });
  }

  // --- add goal --------------------------------------------------------

  function option(value, text) {
    var node = el('option', '', text);
    node.value = value;
    return node;
  }

  function renderAddForm() {
    var taken = state.goals.map(function (g) {
      return g.key;
    });
    var select = $('add-preset');
    select.textContent = '';
    state.presets.forEach(function (p) {
      if (taken.indexOf(p.key) === -1) select.appendChild(option(p.key, ZC.goalLabel(p)));
    });
    select.appendChild(option(CUSTOM, t('custom_goal')));

    var types = $('add-type');
    types.textContent = '';
    GOAL_TYPES.forEach(function (type) {
      types.appendChild(option(type, t('type_' + type)));
    });
    $('add-label').value = '';
    onPresetChange();
  }

  function selectedPreset() {
    var key = $('add-preset').value;
    return state.presets.filter(function (p) {
      return p.key === key;
    })[0];
  }

  function onPresetChange() {
    var preset = selectedPreset();
    $('add-custom').hidden = !!preset;
    $('add-target').value = preset ? preset.target : 1;
    syncAddTarget();
  }

  function syncAddTarget() {
    var preset = selectedPreset();
    var type = preset ? preset.type : $('add-type').value;
    $('add-target-row').hidden = type === 'checkbox';
  }

  function addGoal() {
    var preset = selectedPreset();
    var body = {
      group_id: state.group.id,
      action: 'add',
      target: parseInt($('add-target').value, 10) || 1,
    };
    if (preset) {
      body.preset = preset.key;
    } else {
      body.label = $('add-label').value;
      body.type = $('add-type').value;
    }
    ZC.write('goals.php', body)
      .then(function (data) {
        ZC.haptic('success');
        state.goals = data.goals;
        renderGoals();
        renderAddForm();
      })
      .catch(fail);
  }

  // --- schedule & privacy ----------------------------------------------

  function renderSchedule() {
    $('set-morning').value = state.group.morning_time;
    $('set-night').value = state.group.night_time;
    var select = $('set-timezone');
    select.textContent = '';
    state.timezones.forEach(function (tz) {
      select.appendChild(option(tz, tz.replace(/_/g, ' ')));
    });
    select.value = state.group.timezone;
  }

  function renderPrivacy() {
    var box = $('set-privacy');
    box.textContent = '';
    PRIVACY_MODES.forEach(function (mode) {
      var row = el('label', 'radio-row');
      var input = el('input');
      input.type = 'radio';
      input.name = 'privacy';
      input.value = mode;
      input.checked = state.group.privacy_mode === mode;
      input.addEventListener('change', markDirty);
      var text = el('span', 'radio-text');
      text.appendChild(el('span', 'radio-title', t('privacy_' + mode)));
      text.appendChild(el('span', 'hint small', t('privacy_' + mode + '_desc')));
      row.appendChild(input);
      row.appendChild(text);
      box.appendChild(row);
    });
  }

  function markDirty() {
    tg.MainButton.setText(t('save'));
    tg.MainButton.show();
  }

  function saveSettings() {
    var privacy = document.querySelector('input[name="privacy"]:checked');
    tg.MainButton.showProgress();
    ZC.write('group.php', {
      id: state.group.id,
      morning_time: $('set-morning').value,
      night_time: $('set-night').value,
      timezone: $('set-timezone').value,
      privacy_mode: privacy ? privacy.value : '',
    })
      .then(function (data) {
        state.group = data.group;
        ZC.haptic('success');
        ZC.toast(t('saved'));
        tg.MainButton.hide();
      })
      .catch(fail)
      .then(function () {
        tg.MainButton.hideProgress();
      });
  }
})();
