require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.form': 'lib/jquery.form'
    'jquery.modal': 'lib/jquery.modal.min'
    tools: 'lib/modal.tools'
  shim:
    'jquery.form': ['jquery']

require ['jquery', 'jquery.form','tools'], ($, form,tool)->
  getCookie = (name) ->
    cookieValue = null
    if document.cookie and document.cookie isnt ""
      cookies = document.cookie.split(";")
      i = 0
      while i < cookies.length
        cookie = $.trim(cookies[i])

        # Does this cookie string begin with the name we want?
        if cookie.substring(0, name.length + 1) is (name + "=")
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        i++
    cookieValue

  csrfSafeMethod = (method) ->
    # these HTTP methods do not require CSRF protection
    /^(GET|HEAD|OPTIONS|TRACE)$/.test method

  sameOrigin = (url) ->
    # test that a given url is a same-origin URL
    # url could be relative or scheme relative or absolute
    host = document.location.host # host + port
    protocol = document.location.protocol
    sr_origin = "//" + host
    origin = protocol + sr_origin

    # Allow absolute or scheme relative URLs to same origin

    # or any other URL that isn't scheme relative or absolute i.e relative.
    (url is origin or url.slice(0, origin.length + 1) is origin + "/") or (url is sr_origin or url.slice(0, sr_origin.length + 1) is sr_origin + "/") or not (/^(\/\/|http:|https:).*/.test(url))


  $.ajaxSetup beforeSend: (xhr, settings) ->
    if not csrfSafeMethod(settings.type) and sameOrigin(settings.url)

    # Send the token to same-origin, relative URLs only.
    # Send the token only if the method warrants CSRF protection
    # Using the CSRFToken value acquired earlier
      xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")
    return
  $('#dete-start').val($('#selectInput').val())
  $('#dete-end').val($('#selectInput1').val())
  $('#invest-money').blur ()->
    if $('#is_no').is(':checked')
      self = $('#invest-money')
      val = $.trim(self.val())
      checkStatus = false
      if val != ''
        if val < 200
          $('.error-style').text('投标金额不能小于200')
          checkStatus = false
        else
          if parseInt(val) > parseInt($('#invest-total').val())
             $('.error-style').text('投标金额必须小于账户可用余额!')
             checkStatus = false
          else
            r = /^[1-9]\d*00(\.00|\.0)?$/
            if !r.test(val)
              $('.error-style').text('投标金额必须是 100 的倍数!')
              checkStatus = false
            else
              $('.error-style').text('')
              checkStatus = true
      else
         $('.error-style').text('请输入投标金额')
         checkStatus = false
      return checkStatus

  $('.add-ben').click ()->
    self = $('#invest-money')
    val = $.trim(self.val())
    val = 100 if val is '' or val < 100
    if parseInt(val) + 100 <= parseInt($('#invest-total').val())
      self.val(parseInt(val) + 100)
      $('.error-style').text('')

  $('.subtract').click ()->
    self = $('#invest-money')
    val = $.trim(self.val())
    if $('.error-style').text() is ''
      if parseInt(val) - 100 >= 200
        self.val(parseInt(val) - 100)

  $('.income-range').blur ()->
    if $('#is_no').is(':checked')
      self = $('#scope-min')
      val = $.trim(self.val())
      r = /^[0-9]*[1-9][0-9]*$/
      if val != ''
        if !r.test(val) or !r.test($('#scope-max').val())
          $('.error-style').text('收益范围请输入正整数')
          return false
        else if Number(val) > Number($.trim($('#scope-max').val()))
          $('.error-style').text('请填写正确收益范围')
          return false
        else if val > 30 or $('#scope-max').val() > 30
          $('.error-style').text('请填写正确收益范围')
          return false
        else
          $('.error-style').text('')
      else
        $('.error-style').text('请填写收益范围')

  $('.tender-ul-left li select').change ()->
    if Number($('#dete-start').val()) > Number($('#dete-end').val())
      $('.error-style').text('请选择正确收益期限')
      return false
    else
       $('.error-style').text('')

  $('#submit').click ()->
    isNo = $('#is_no').is(':checked')
    if isNo
      $('#invest-money').blur()
      if $('.error-style').text() is ''
         $('.income-range').blur()
      if Number($('#dete-start').val()) > Number($('#dete-end').val()) or ($('#dete-start').val() == null or $('#dete-end').val() == null)
        $('.error-style').text('请选择正确收益期限')
        return false
    else
      $('.error-style').text('')
    if $('.error-style').text() is ''
      if $('#agree').is(':checked')
        if isNo
          tip = "您将开启自动投标"
        else
          tip = "您将关闭自动投标"
        tool.modalConfirm({
          title: '温馨提示', msg: tip, callback_ok: ()->
            $('#tenderForm').ajaxSubmit (data) ->
              $('.error-style').text(data.message)
              if data.ret_code == 0
                if isNo
                  $('#submit').text("关闭")
                  $('#is_no').prop('checked', false)
                  $('#status').text("自动投标已开启")
                else
                  $('#submit').text("开启")
                  $('#is_no').prop('checked', true)
                  $('#status').text("自动投标已关闭")
        })
      else
        alert('请同意协议')
