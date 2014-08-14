require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'


require ['jquery', 'lib/backend', 'tools'], ($, backend, tool)->

  $("#invite_top_bar").click () ->
    backend.userProfile {

    }
    .done ->
      window.location.href = '/accounts/invite/'
    .fail (xhr)->
      if xhr.status == 403
        $('.login-modal').trigger('click')
        return

