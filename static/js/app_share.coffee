require.config
  paths:
    jquery: 'lib/jquery.min'
    jquerymobile: 'lib/jquery.mobile.custom.min'

require ['jquery', 'lib/backend', 'jquerymobile'], ($, backend, mobile)->

  Request = new Object()
  Request = backend.getRequest();
  req_identifier = Request['identifier']
  if req_identifier
    $(".re_identifier").text(req_identifier)
    $("#reg_identifier").val(reg_identifier)

  checkMobile = (identifier) ->
    re = undefined
    re = /^1\d{10}$/
    re.test identifier

  $("#button-get-validate-code-modal").click (e) ->
    element = this
    if $(element).hasClass 'disable'
      return
    $(".error-message").text("")
    friend_identifier = $("#friend_identifier").val()
    identifier = $("#my_identifier").val().trim()
    if !identifier
      $(".error-message").text("请输入手机号")
    if checkMobile(identifier)
      if identifier == $("#friend_identifier").val()
        $(".error-message").text("自己不能邀请自己")
      else
        backend.userExists identifier
        .done ->
          $(".popup-message").text("您输入的手机号已注册过网利宝！")
          $("#popupDialog").popup('open')
          $("#popupDialog").on "popupafterclose", ()->
            window.location.href = "/activity/wap/share?phone=" + identifier + "&reg=n#stepDownload"
            return true
        .fail ->
          $(".popup-message").text("验证码已发送至您手机，请注意查收。")
          $("#popupDialog").popup('open')
          $("#popupDialog").on "popupafterclose", ()->
            window.location.href = "/activity/wap/share_reg/?friend_identifier=" + friend_identifier + "&identifier=" + identifier
            return true
    else
      $(".error-message").text("手机号输入错误")

  $('.downloadApp').click (event)->
    console.log navigator.userAgent
    iphone = /iphone/i.test navigator.userAgent.toLowerCase()
    android = /android/i.test navigator.userAgent.toLowerCase()
    if iphone
      window.location.href = "https://itunes.apple.com/cn/app/wang-li-bao/id881326898?mt=8"
      return true
    else if android
      window.location.href = "http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao#opened"
      return true
    else
      $(".popup-message").text("抱歉当前移动平台只支持 iOS 和安卓客户端。您可以去网利宝网站（www.wanglibao.com）进行投资。")
      $("#popupDialogDown").popup('open')
      $("#popupDialogDown").on "popupafterclose", ()->
        window.location.href = "/"
        return true


