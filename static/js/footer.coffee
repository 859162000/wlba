require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.validate': 'lib/jquery.validate.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
  shim:
    'jquery.modal': ['jquery']
    'jquery.validate': ['jquery']
    'jquery.placeholder': ['jquery']

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', 'jquery.placeholder'], ($, modal, backend, validate, placeholder)->

  $('.login-modal').click (e)->
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/"
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)

    e.preventDefault()
    $(this).modal()

    $.validator.addMethod "emailOrPhone", (value, element)->
      return backend.checkEmail(value) or backend.checkMobile(value)

    $('#login-form').validate
      rules:
        identifier:
          required: true
          emailOrPhone: true
        password:
          required: true
          minlength: 6
        captcha_1:
          required: true
          minlength: 4

      messages:
        identifier:
          required: '不能为空'
          emailOrPhone: '请输入邮箱或者手机号'
        password:
          required: '不能为空'
          minlength: $.format("密码需要最少{0}位")
        captcha_1:
          required: '不能为空'
          minlength: $.format("验证码要输入4位")

      #errorContainer:
        #"#errMessage1, #errMessage2, #errMessage3"

      $('.captcha-refresh').click ->
        $form = $(this).parents('form')
        url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/"

        $.getJSON url, {}, (json)->
          $form.find('input[name="captcha_0"]').val(json.key)
          $form.find('img.captcha').attr('src', json.image_url)

      submitHandler: (form) ->
        $.ajax(
          url: $('#login-form').attr('action')
          type: "POST"
          beforeSend: (XMLHttpRequest) ->
            XMLHttpRequest.setRequestHeader("X-Requested-With","XMLHttpRequest")
          data: $("#login-form").serialize()
          dataType: "json"
        )
        .done (data,textStatus) ->
          $('#user-info-ajax').html(
            '<a href="/accounts/home">'
            + data.nick_name +
            ' 的个人中心</a> <a class="logout" href="/accounts/logout">退出</a>'
          )
          $('#id_identifier').val ''
          $('#id_password').val ''
          $.modal.close()
        .fail (xhr)->
          #if xhr.status == '4xx'
          alert('登录失败，请重新登录')


  $('.register-modal').click (e)->
    e.preventDefault()
    $(this).modal()







