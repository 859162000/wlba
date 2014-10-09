(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.zclip': 'lib/jquery.zclip.min'
    }
  });
  require(['jquery', 'jquery.zclip'], function($, zclip) {
    return $(document).ready(function() {
      return $("#inviteCopyButton").zclip()({
        path: '/static/images/ZeroClipboard.swf',
        copy: $('.invite-textarea').text(),
        afterCopy: function() {
          return alert('复制成功！\n你可以粘贴到QQ或论坛中发送给好友');
        }
      });
    });
  });
}).call(this);
