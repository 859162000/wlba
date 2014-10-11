(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      tools: 'lib/modal.tools'
    }
  });
  require(['jquery', 'lib/backend', 'tools'], function($, backend, tool) {
    var submit_form;
    submit_form = function() {
      var identifier;
      identifier = $('input[name="identifier"]').val();
      if (!identifier) {
        tool.modalAlert({
          title: '温馨提示',
          msg: '请输入手机号'
        });
        return;
      }
      return backend.userExists(identifier.done(function() {
        $('form#identifier').submit();
        return true;
      })).fail(function() {
        return tool.modalAlert({
          title: '温馨提示',
          msg: '该用户不存在'
        });
      });
    };
    $('#submitButton').click(function(e) {
      e.preventDefault();
      return submit_form();
    });
    return $('input').keyup(function(e) {
      if (e.keyCode === 13) {
        e.preventDefault();
        return submit_form();
      }
    });
  });
}).call(this);
