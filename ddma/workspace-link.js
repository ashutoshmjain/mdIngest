// Shared Workspace home-link definition (ONE definition — do not hardcode the
// workspace URL in app files). The workspace landing page lives on port 8088
// of the SAME host that serves the app, so the URL is derived at runtime from
// window.location.hostname. Mirrored copies (ingest/ and ddma/) are
// byte-identical; to change the port or path, edit here and mirror.
// Usage in app HTML:
//   <a data-workspace-home ...>... label ...</a>
//   <a data-workspace-home data-workspace-page="cockpit.html" ...>cockpit</a>
// plus one include per page: <script src="workspace-link.js"></script>
(function () {
  function workspaceBaseUrl() {
    return 'http://' + window.location.hostname + ':8088/';
  }
  function cutroomBaseUrl() {
    return 'http://' + window.location.hostname + ':8000/';
  }
  function beatsBaseUrl() {
    return 'http://' + window.location.hostname + ':8001/';
  }
  function applyWorkspaceLinks() {
    document.querySelectorAll('a[data-workspace-home]').forEach(function (a) {
      a.href = workspaceBaseUrl() + (a.getAttribute('data-workspace-page') || '');
    });
    document.querySelectorAll('a[data-cutroom-home]').forEach(function (a) {
      a.href = cutroomBaseUrl() + (a.getAttribute('data-cutroom-page') || 'curator.html');
    });
    document.querySelectorAll('a[data-beats-home]').forEach(function (a) {
      a.href = beatsBaseUrl() + (a.getAttribute('data-beats-page') || 'beats.html');
    });
  }
  // Shared helper for app code (e.g. the Curator Workspace button handler).
  window.deepdiveWorkspaceUrl = workspaceBaseUrl;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyWorkspaceLinks);
  } else {
    applyWorkspaceLinks();
  }
})();
