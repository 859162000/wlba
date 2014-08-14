require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.zclip': 'lib/jquery.zclip.min'


require ['jquery','jquery.zclip'], ($, zclip)->
  $(document).ready ->
    $("#inviteCopyButton").zclip()
      path:'/static/images/ZeroClipboard.swf'
      copy: $('.invite-textarea').text()
      afterCopy: ->
        alert('复制成功！\n你可以粘贴到QQ或论坛中发送给好友');
