require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.modal': 'lib/jquery.modal.min'
    'jquery.validate': 'lib/jquery.validate.min'
    'jquery.complexify': 'lib/jquery.complexify.min'
    'jquery.placeholder': 'lib/jquery.placeholder'
    'underscore': 'lib/underscore-min'
    tools: 'lib/modal.tools'
  shim:
    'jquery.modal': ['jquery']
    'jquery.validate': ['jquery']
    'jquery.complexify': ['jquery']
    'jquery.placeholder': ['jquery']

require ['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', "tools", 'jquery.complexify', 'jquery.placeholder', 'underscore'], ($, modal, backend, validate,tool,  complexify, placeholder, _)->


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


  $.validator.addMethod "emailOrPhone", (value, element)->
      return backend.checkEmail(value) or backend.checkMobile(value)

  $('#login-modal-form').validate
    rules:
      identifier:
        required: true
        emailOrPhone: true
      password:
        required: true
        minlength: 6
        maxlength: 20
      captcha_1:
        required: true
        minlength: 1

    messages:
      identifier:
        required: '不能为空'
        emailOrPhone: '请输入手机号'
      password:
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")
        maxlength: '密码不能超过20位'
      captcha_1:
        required: '不能为空'
        minlength: $.format("验证码至少输入1位")

    errorPlacement: (error, element) ->
        error.appendTo $(element).parents('.form-row').children('.form-row-error')

    submitHandler: (form) ->
      if $('#login_submit').hasClass('disabled')
        return
      $('#login_submit').addClass('disabled')
      $.ajax
        url: $('#login-modal-form').attr('action')
        type: "POST"
        data: $("#login-modal-form").serialize()
      .done (data,textStatus) ->
        next_url = ''
        arr = /\?next=(\/.+)$/ig.exec(window.location)
        if(arr && arr[1])
          next_url = arr[1]
          window.location.href = next_url
        else
          location.reload()

        $('#login_submit').removeClass('disabled')
      .fail (xhr)->
        result = JSON.parse xhr.responseText
        message = result.message
        error_message = _.chain(message).pairs().map((e)->e[1]).flatten().value()
        $('.captcha-refresh', '#login-modal-form').trigger('click')
        alert error_message
        $('#login_submit').removeClass('disabled')

  $('#register-modal-form').validate
    rules:
      identifier:
        required: true
        isMobile: true
      validate_code:
        required: true

      password:
        required: true
        minlength: 6
        maxlength: 20
      password2:
        equalTo: "#reg_password"
      agreement:
        required: true

    messages:
      identifier:
        required: '不能为空'
        isMobile: '请输入手机号'
      validate_code:
        required: '不能为空'
      password:
        required: '不能为空'
        minlength: $.format("密码需要最少{0}位")
        maxlength: '密码不能超过20位'
      password2:
        equalTo: '密码不一致'
      agreement:
        required: '请勾选注册协议'


    errorPlacement: (error, element) ->
      error.appendTo $(element).parents('.form-row').children('.form-row-error')

    submitHandler: (form) ->
      $('input[name="identifier"]').trigger('keyup')
      $.ajax
        url: $(form).attr('action')
        type: "POST"
        data: $(form).serialize()
      .done (data,textStatus) ->
          location.reload()
      .fail (xhr)->
        result = JSON.parse xhr.responseText
        message = result.message
        error_message = _.chain(message).pairs().map((e)->e[1]).flatten().value()
        alert error_message

  $('input, textarea').placeholder()

  checkMobile = (identifier) ->
      re = undefined
      re = /^1\d{10}$/
      re.test identifier

  $("#reg_identifier").keyup (e) ->
      isMobile = undefined
      value = undefined
      value = $(this).val()
      isMobile = checkMobile(value)
      if isMobile
        $("#id_type").val "phone"
        $("#validate-code-container").show()

  $("#reg_identifier").keyup()

  _showModal = ()->
    $('#login-modal').modal()

  $("#button-get-validate-code-modal").click (e) ->
      e.preventDefault()
      element = this
      phoneNumber = $.trim($("#reg_identifier").val())
      if checkMobile(phoneNumber)
        if console?
          console.log "Phone number checked, now send the valdiation code"

        $.ajax
          url: "/api/phone_validation_code/register/" + phoneNumber + "/"
          type: "POST"
        .fail (xhr)->
          $.modal.close()
          clearInterval(intervalId)
          $(element).text('重新获取')
          $(element).removeAttr 'disabled'
          $(element).addClass 'button-red'
          $(element).removeClass 'button-gray'
          result = JSON.parse xhr.responseText
          if xhr.status > 400
            tool.modalAlert({title: '温馨提示', msg: result.message, callback_ok: _showModal})

        intervalId
        count = 180

        $(element).attr 'disabled', 'disabled'
        $(element).removeClass 'button-red'
        $(element).addClass 'button-gray'
        $('.voice-validate').attr 'disabled', 'disabled'

        timerFunction = ()->
          if count >= 1
            count--
            $(element).text('已经发送(' + count + ')')
          else
            clearInterval(intervalId)
            $(element).text('重新获取')
            $(element).removeAttr 'disabled'
            $(element).addClass 'button-red'
            $(element).removeClass 'button-gray'
            $('.voice').removeClass('hidden')
            $('.voice-validate').removeAttr 'disabled'
            $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>')

        # Fire now and future
        timerFunction()
        intervalId = setInterval timerFunction, 1000
        # Add the validate rule function emailOrPhone

  $.validator.addMethod "isMobile", (value, element)->
      return checkMobile(value)

  @COMPLEXIFY_BANLIST = '123456|password|12345678|1234|pussy|12345|dragon|qwerty|696969|mustang|letmein|baseball|master|michael|football|shadow|monkey|abc123|pass|fuckme|6969|jordan|harley|ranger|iwantu|jennifer|hunter|fuck|2000|test|batman|trustno1|thomas|tigger|robert|access|love|buster|1234567|soccer|hockey|killer|george|sexy|andrew|charlie|superman|asshole|fuckyou|dallas|jessica|panties|pepper|1111|austin|william|daniel|golfer|summer|heather|hammer|yankees|joshua|maggie|biteme|enter|ashley|thunder|cowboy|silver|richard|fucker|orange|merlin|michelle|corvette|bigdog|cheese|matthew|121212|patrick|martin|freedom|ginger|blowjob|nicole|sparky|yellow|camaro|secret|dick|falcon|taylor|111111|131313|123123|bitch|hello|scooter|please|porsche|guitar|chelsea|black|diamond|nascar|jackson|cameron|654321|computer|amanda|wizard|xxxxxxxx|money|phoenix|mickey|bailey|knight|iceman|tigers|purple|andrea|horny|dakota|aaaaaa|player|sunshine|morgan|starwars|boomer|cowboys|edward|charles|girls|booboo|coffee|xxxxxx|bulldog|ncc1701|rabbit|peanut|john|johnny|gandalf|spanky|winter|brandy|compaq|carlos|tennis|james|mike|brandon|fender|anthony|blowme|ferrari|cookie|chicken|maverick|chicago|joseph|diablo|sexsex|hardcore|666666|willie|welcome|chris|panther|yamaha|justin|banana|driver|marine|angels|fishing|david|maddog|hooters|wilson|butthead|dennis|fucking|captain|bigdick|chester|smokey|xavier|steven|viking|snoopy|blue|eagles|winner|samantha|house|miller|flower|jack|firebird|butter|united|turtle|steelers|tiffany|zxcvbn|tomcat|golf|bond007|bear|tiger|doctor|gateway|gators|angel|junior|thx1138|porno|badboy|debbie|spider|melissa|booger|1212|flyers|fish|porn|matrix|teens|scooby|jason|walter|cumshot|boston|braves|yankee|lover|barney|victor|tucker|princess|mercedes|5150|doggie|zzzzzz|gunner|horney|bubba|2112|fred|johnson|xxxxx|tits|member|boobs|donald|bigdaddy|bronco|penis|voyager|rangers|birdie|trouble|white|topgun|bigtits|bitches|green|super|qazwsx|magic|lakers|rachel|slayer|scott|2222|asdf|video|london|7777|marlboro|srinivas|internet|action|carter|jasper|monster|teresa|jeremy|11111111|bill|crystal|peter|pussies|cock|beer|rocket|theman|oliver|prince|beach|amateur|7777777|muffin|redsox|star|testing|shannon|murphy|frank|hannah|dave|eagle1|11111|mother|nathan|raiders|steve|forever|angela|viper|ou812|jake|lovers|suckit|gregory|buddy|whatever|young|nicholas|lucky|helpme|jackie|monica|midnight|college|baby|cunt|brian|mark|startrek|sierra|leather|232323|4444|beavis|bigcock|happy|sophie|ladies|naughty|giants|booty|blonde|fucked|golden|0|fire|sandra|pookie|packers|einstein|dolphins|chevy|winston|warrior|sammy|slut|8675309|zxcvbnm|nipples|power|victoria|asdfgh|vagina|toyota|travis|hotdog|paris|rock|xxxx|extreme|redskins|erotic|dirty|ford|freddy|arsenal|access14|wolf|nipple|iloveyou|alex|florida|eric|legend|movie|success|rosebud|jaguar|great|cool|cooper|1313|scorpio|mountain|madison|987654|brazil|lauren|japan|naked|squirt|stars|apple|alexis|aaaa|bonnie|peaches|jasmine|kevin|matt|qwertyui|danielle|beaver|4321|4128|runner|swimming|dolphin|gordon|casper|stupid|shit|saturn|gemini|apples|august|3333|canada|blazer|cumming|hunting|kitty|rainbow|112233|arthur|cream|calvin|shaved|surfer|samson|kelly|paul|mine|king|racing|5555|eagle|hentai|newyork|little|redwings|smith|sticky|cocacola|animal|broncos|private|skippy|marvin|blondes|enjoy|girl|apollo|parker|qwert|time|sydney|women|voodoo|magnum|juice|abgrtyu|777777|dreams|maxwell|music|rush2112|russia|scorpion|rebecca|tester|mistress|phantom|billy|6666|albert|111111|11111111|112233|121212|123123|123456|1234567|12345678|131313|232323|654321|666666|696969|777777|7777777|8675309|987654|abcdef|password1|password12|password123|twitter'.split('|')

  container = $('.password-strength-container')
  $('#reg_password').complexify {minimumChars:6, strengthScaleFactor:1}, (valid, complexity)->
      if complexity == 0
        container.removeClass 'low'
        container.removeClass 'soso'
        container.removeClass 'strong'
      else if complexity < 30
        container.removeClass 'soso'
        container.removeClass 'strong'
        container.addClass 'low'
      else if complexity < 60
        container.removeClass 'low'
        container.removeClass 'strong'
        container.addClass 'soso'
      else
        container.removeClass 'low'
        container.removeClass 'soso'
        container.addClass 'strong'


  $('.login-modal').click (e)->
    $("#tab-login").addClass('active')
    $("#tab-register").removeClass('active')
    $("#login-modal-form").show()
    $("#register-modal-form").hide()
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)

    e.preventDefault()
    $(this).modal()

  $('.register-modal').click (m)->
    $("#tab-login").removeClass('active')
    $("#tab-register").addClass('active')
    $("#login-modal-form").hide()
    $("#register-modal-form").show()

    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())
    $.getJSON url, {}, (json)->
      $('input[name="captcha_0"]').val(json.key)
      $('img.captcha').attr('src', json.image_url)

    m.preventDefault()
    $(this).modal()

  $('.captcha-refresh').click ->
    $form = $(this).parents('form')
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v="+(+new Date())

    $.getJSON url, {}, (json)->
      $form.find('input[name="captcha_0"]').val(json.key)
      $form.find('img.captcha').attr('src', json.image_url)

  $('.login-modal-tab>li').click (e)->
    $('.login-modal-tab>li').removeClass('active')
    $(this).addClass('active')
    if $("#tab-login").attr('class') == 'active'
      $("#login-modal-form").show()
      $("#register-modal-form").hide()
    else
      $("#login-modal-form").hide()
      $("#register-modal-form").show()

  $("#agreement").change (value)->
    if $(this).attr "checked"
      $("#register_submit").addClass("disabled")
      $(this).removeAttr "checked"
    else
      $("#register_submit").removeClass("disabled")
      $(this).attr "checked", "checked"

  $("#register_submit").click (e)->
    if $(this).hasClass("disabled")
      e.preventDefault()
      return

  $('.nologin').click (e)->
    e.preventDefault()
    $('.login-modal').trigger('click')

  $("input:password").bind "copy cut paste", (e) ->
    element = this
    setTimeout (->
      text = $(element).val()
      if(!/[^\u4e00-\u9fa5]+/ig.test(text) || /\s+/ig.test(text))
        $(element).val('')
      return
    ), 100
    #return false

  msg_count = $('#message_count').html()
  if msg_count > 0
    backend.loadMessageCount('unread')
      .done (data)->
        if data.count > 0
          $('#message_count').show()
          $('#message_count').html(data.count)
  #author: hetao; time: 2014.10.15
#  $(window).load (e) ->
#    $.getScript "http://wpa.b.qq.com/cgi/wpa.php", (data, textStatus, jqxhr) ->
#      BizQQWPA.addCustom [
#        {
#          aty: "1" #指定工号类型
#          a: "1001" #指定的工号企业 WPA OpenAPI
#          nameAccount: "4008588066" #营销 QQ 号码
#          selector: "qq-container" #WPA 被放置的元素
#        }
#        {
#          aty: "1" #指定工号类型
#          a: "1001" #指定的工号企业 WPA OpenAPI
#          nameAccount: "4008588066" #营销 QQ 号码
#          selector: "top-qq" #WPA 被放置的元素
#        }
#      ]
  #author: hetao; time: 2014.11.20; description: 语音验证事件绑定
  $(".voice").on 'click', '.voice-validate', (e)->
    e.preventDefault()
    isMobile = checkMobile($("#reg_identifier").val().trim())
    if !isMobile
      $("#id_type").val "phone"
      $("#validate-code-container").show()
      return

    if($(this).attr('disabled') && $(this).attr('disabled') == 'disabled')
      return

    element = $('.voice .span12-omega')

    url = $(this).attr('href')
    $.ajax
      url: url
      type: "POST"
      data: {
        phone: $("#reg_identifier").val().trim()
      }
    .success (json)->
      if(json.ret_code == 0)
        #TODO

        intervalId
        count = 180
        button = $("#button-get-validate-modal")

        button.attr 'disabled', 'disabled'
        button.addClass 'button-gray'

        $('.voice').addClass 'tip'
        timerFunction = ()->
          if count >= 1
            count--
            element.text('语音验证码已经发送，请注意接听（' + count + '）')
          else
            clearInterval(intervalId)
            element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>')
            element.removeAttr 'disabled'
            button.removeAttr 'disabled'
            button.addClass 'button-red'
            button.removeClass 'button-gray'
            $('.voice').removeClass 'tip'

        # Fire now and future
        timerFunction()
        intervalId = setInterval timerFunction, 1000
      else
        #TODO
        element.html('系统繁忙请尝试短信验证码')
    .fail (xhr)->
      if xhr.status > 400
        tool.modalAlert({title: '温馨提示', msg: result.message, callback_ok: _showModal})

