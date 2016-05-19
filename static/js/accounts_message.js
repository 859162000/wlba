// Generated by CoffeeScript 1.10.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      knockout: 'lib/knockout',
      underscore: 'lib/underscore-min'
    }
  });

  require(['jquery', 'knockout', 'underscore', 'lib/backend', 'model/messageTable', 'model/pager', 'model/tab'], function($, ko, _, backend, message, pager, tab) {
    return $('.msg-id').click(function(e) {
      var msg_icon, msg_id, msg_id_id, read_status;
      e.preventDefault();
      msg_id = e.currentTarget.id || $(this).attr('data-id');
      msg_icon = $("#icon_" + msg_id).attr('class');
      read_status = $('#' + msg_id).attr('data-read-status');
      msg_id_id = $('#' + msg_id).attr('data-msg-id');
      if (msg_icon === 'icon-msg-arrow-down') {
        $("#cnt_" + msg_id).show();
        $("#title_" + msg_id).removeClass('blue');
        $("#icon_" + msg_id).removeClass('icon-msg-arrow-down');
        $("#icon_" + msg_id).addClass('icon-msg-arrow-up');
        if (read_status === 'False' || read_status === '0') {
          return backend.readMessage(msg_id_id).done(function(data) {
            return $('#' + msg_id).attr('data-read-status', 'True');
          });
        }
      } else {
        $("#cnt_" + msg_id).hide();
        $("#icon_" + msg_id).removeClass('icon-msg-arrow-up');
        return $("#icon_" + msg_id).addClass('icon-msg-arrow-down');
      }
    });
  });

}).call(this);
