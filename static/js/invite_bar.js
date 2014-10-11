(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      tools: 'lib/modal.tools'
    }
  });
  require(['jquery', 'lib/backend', 'tools'], function($, backend, tool) {
    return $("#invite_top_bar").click(function() {
      return backend.userProfile({}.done(function() {
        return window.location.href = '/accounts/invite/';
      })).fail(function(xhr) {
        if (xhr.status === 403) {
          $('.login-modal').trigger('click');
        }
      });
    });
  });
}).call(this);
