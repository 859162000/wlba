// Generated by CoffeeScript 1.7.1
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    return $('#setPasswordButton').click(function(e) {
      var password1, password2;
      password1 = $('input[name="password1"').val();
      password2 = $('input[name="password2"').val();
      if (password1 !== password2) {
        return console.log('Password not match');
      } else {
        return $.post('/accounts/password_reset_password', {
          password1: password1,
          password2: password2
        }).done(function() {
          return window.location = 'http://www.baidu.com';
        }).fail(function() {
          return console.log('更改密码失败 请重试');
        });
      }
    });
  });

}).call(this);

//# sourceMappingURL=set_password.map
