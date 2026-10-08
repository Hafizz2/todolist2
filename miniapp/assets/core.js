// Shared helpers for the Mini App scripts (window.ZC). Loaded first.
(function () {
  'use strict';

  var tg = window.Telegram && window.Telegram.WebApp;
  var I18N = JSON.parse(document.getElementById('i18n').textContent);
  var saveQueue = Promise.resolve(); // keeps writes in order

  var ZC = {
    tg: tg,
    lang: 'am',
  };

  ZC.setLang = function (lang) {
    ZC.lang = I18N[lang] ? lang : 'am';
    document.documentElement.lang = ZC.lang;
    document.querySelectorAll('[data-i18n]').forEach(function (node) {
      node.textContent = ZC.t(node.getAttribute('data-i18n'));
    });
  };

  ZC.t = function (key, vars) {
    var s = (I18N[ZC.lang] && I18N[ZC.lang][key]) || I18N.am[key] || key;
    Object.keys(vars || {}).forEach(function (k) {
      s = s.split('{' + k + '}').join(String(vars[k]));
    });
    return s;
  };

  /** Translated name for well-known goal keys, else the stored label. */
  ZC.goalLabel = function (goal) {
    return (I18N[ZC.lang] && I18N[ZC.lang]['goal_' + goal.key]) || goal.label;
  };

  ZC.$ = function (id) {
    return document.getElementById(id);
  };

  ZC.el = function (tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  ZC.show = function (viewId) {
    document.querySelectorAll('.view').forEach(function (v) {
      v.hidden = v.id !== viewId;
    });
    window.scrollTo(0, 0);
  };

  ZC.showMessage = function (text) {
    ZC.$('message').textContent = text;
    ZC.show('view-message');
  };

  var toastTimer = null;
  ZC.toast = function (text) {
    var node = ZC.$('toast');
    node.textContent = text;
    node.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      node.hidden = true;
    }, 2500);
  };

  ZC.haptic = function (kind) {
    if (!tg || !tg.HapticFeedback) return;
    if (kind === 'success') tg.HapticFeedback.notificationOccurred('success');
    else if (kind === 'error') tg.HapticFeedback.notificationOccurred('error');
    else if (kind === 'select') tg.HapticFeedback.selectionChanged();
    else tg.HapticFeedback.impactOccurred('light');
  };

  /** Calls api/<path>. Rejects with Error(message = API error code) on failure. */
  ZC.api = function (path, body, keepalive) {
    var opts = {
      method: body ? 'POST' : 'GET',
      headers: { 'X-Telegram-Init-Data': tg.initData },
      keepalive: !!keepalive,
    };
    if (body) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    return fetch('api/' + path, opts).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.error || 'http_' + res.status);
        return data;
      });
    });
  };

  /** Like ZC.api for writes, but queued so writes reach the server in order. */
  ZC.write = function (path, body, keepalive) {
    var run = function () {
      return ZC.api(path, body, keepalive);
    };
    var result = saveQueue.then(run, run);
    saveQueue = result.catch(function () {});
    return result;
  };

  /** One BackButton handler at a time. */
  var backHandler = null;
  ZC.setBack = function (handler) {
    if (backHandler) tg.BackButton.offClick(backHandler);
    backHandler = handler;
    if (handler) {
      tg.BackButton.onClick(handler);
      tg.BackButton.show();
    } else {
      tg.BackButton.hide();
    }
  };

  window.ZC = ZC;
})();
