// Shared Workspace home-link definition (ONE definition — do not hardcode the
// workspace URL in app files). The workspace landing page lives on port 8088
// of the SAME host that serves the app, so the URL is derived at runtime from
// window.location.hostname. Mirrored copies (ingest/ and ddma/) are
// byte-identical; to change the port or path, edit here and mirror.
// Usage in app HTML:
//   <a data-workspace-home target="deepdive-workspace" ...>... label ...</a>
//   <a data-workspace-home data-workspace-page="cockpit.html" ...>cockpit</a>
// plus one include per page: <script src="workspace-link.js"></script>
(function () {
  function workspaceBaseUrl() {
    return 'http://' + window.location.hostname + ':8088/';
  }
  function applyWorkspaceLinks() {
    document.querySelectorAll('a[data-workspace-home]').forEach(function (a) {
      a.href = workspaceBaseUrl() + (a.getAttribute('data-workspace-page') || '');
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
