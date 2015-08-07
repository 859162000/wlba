require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder'
    },
    shim: {
        'jquery.placeholder': ['jquery']
    }
});
require(['jquery','jquery.placeholder'], function( $ ,placeholder) {
    //初始化
    pageInitFun = function(){
        var  csrfSafeMethod, getCookie,sameOrigin,
        getCookie = function(name) {
            var cookie, cookieValue, cookies, i;
            cookieValue = null;
            if (document.cookie && document.cookie !== "") {
                cookies = document.cookie.split(";");
                i = 0;
                while (i < cookies.length) {
                  cookie = $.trim(cookies[i]);
                  if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                  }
                  i++;
                }
            }
            return cookieValue;
        };
        csrfSafeMethod = function(method) {
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        };
        sameOrigin = function(url) {
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = "//" + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
        };
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });

         //切换Nav
        $('.minNavBtn').on('click',function(){
            $('.minNax').find('.curr').removeClass('curr');
            var self = $(this);
            self.addClass('curr')
            var tag = self.attr('tag');
            if(tag == '1'){
                $('.logonFormDiv').show();
                $('.registerFormDiv').hide();
            }else{
                $('.logonFormDiv').hide();
                $('.registerFormDiv').show();
                self.hasClass('selectEd') ? '' : self.addClass('selectEd');
            }
        })

        //文本框的得到和失去光标
        var zhi;
        $('.placeholderInput').on("focus", function () {
            var self = $(this)
            if (self.attr('placeholder')) {
              zhi = self.attr('placeholder');
            }
            self.attr('placeholder', '');
            self.parent().addClass('selectEdLi')
        });

        $('.placeholderInput').on('blur', function () {
            var self = $(this);
            self.attr('placeholder', zhi);
            self.parent().removeClass('selectEdLi')
        })

        $(this).keydown(function(event){
            if(event.keyCode == '13'){
                if($('.minNavLeft').hasClass('curr')){
                    $('#loginSubmit').click();
                }else{
                    $('#loginSubmit').click();
                }
            }
        });
    }
    pageInitFun();

    //验证手机号
    checkMobileFun = function(form){
        var checkStatus = false,form =$('#'+form),self = $.trim(form.find('.checkMobile').val());
        if(! checkMobile(self)){
            form.find('.loginError').text('请输入正确手机号');
            checkStatus = false;
        }else{
            form.find('.loginError').text('');
            checkStatus = true;
        }
        return checkStatus;
    }
    //验证密码
    checkPwdFun = function(form){
        var loginError = $('#'+form).find('.loginError');
        var checkStatus = false,self = $.trim($('#'+form).find('.checkPwd').val());
        if(self == ''){
           loginError.text('请输入密码');
           checkStatus = false;
        }else if(self.length < 6){
           loginError.text('密码最少6位');
           checkStatus = false;
        }else if(self.length > 20){
           loginError.text('密码最多20位');
           checkStatus = false;
        }else{
           loginError.text('');
           checkStatus = true;
        }
        return checkStatus;
    }
    //验证码
    checkCodedFun = function(form,re){
        var checkStatus = false
        if(re == 're'){
            var self = $.trim($('#'+form).find('#registerSMSCode').val());
        }else{
            var self = $.trim($('#'+form).find('.checkCode').val());
        }
        if(self == '') {
            $('#'+form).find('.loginError').text('请输入验证码');
            checkStatus = false;
        }else{
            $('#'+form).find('.loginError').text('');
            checkStatus = true;
        }
        return checkStatus;
    }
    //手机和正则
    checkMobile = function(identifier) {  //验证手机号
      var re = /^1\d{10}$/;
      return re.test(identifier);bb
    }
    //刷新验证码
    imgCodeRe = function(form){
        url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
        $.getJSON(url, {}, function(json) {
          $('#'+form).find('input[name="captcha_0"]').val(json.key);
          $('#'+form).find('img.captchaImg').attr('src', json.image_url);
        });
    }

    //登录模块初始化
    loginInitFun = function(){
        $('#loginMobile').on('blur',function() {
            checkMobileFun('loginForm');
        })
        $('#loginPwd').on('blur',function() {
            checkPwdFun('loginForm');
        })
        $('#loginCode').on('blur',function() {
            checkCodedFun('loginForm');
        })
        imgCodeRe('loginForm');
        $('#loginRefresh').on('click',function(){
            imgCodeRe('loginForm');
        })
        //提交登录表单
        $('#loginSubmit').on('click',function(){
            if(checkMobileFun('loginForm') && checkPwdFun('loginForm') && checkCodedFun('loginForm')){
                if($('#remember_me').is(':checked')){
                    var remember_me = 'remember_me';
                }
                $.ajax({
                  url: '/accounts/login/ajax/',
                  type: "POST",
                  data: {
                      identifier : $('#loginMobile').val(),
                      password : $('#loginPwd').val(),
                      captcha_0 : $('#id_captcha_0').val(),
                      captcha_1 : $('#loginCode').val(),
                      remember_me : remember_me
                  }
                }).done(function() {
                  var next_url = '';
                  var arr = /\?next=(\/.+)$/ig.exec(window.location);
                  if (arr && arr[1]) {
                    next_url = arr[1];
                    window.location.href = next_url;
                  } else {
                    location.reload();
                  }
                }).fail(function(xhr) {
                    var result = JSON.parse(xhr.responseText);
                    if(result.message.__all__ != undefined){
                        $('#loginForm').find('.loginError').text(result.message.__all__[0]);
                    }else if(result.message.captcha != undefined){
                        $('#loginForm').find('.loginError').text(result.message.captcha[0]);
                    }
                });
            }
        })
    }
    loginInitFun();
    registerInitFun = function(){
       //密码type
        $('.pwdStatus').on('click',function(){
            var self = $(this);
            if(self.hasClass('icon-eye03')){
                self.removeClass('icon-eye03').addClass('icon-eye02');
                $('#registerPwd').attr('type','text')
            }else{
                self.removeClass('icon-eye02').addClass('icon-eye03');
                $('#registerPwd').attr('type','password')
            }
        })
        //注册手机号验证
        $('#registerMobile').on('blur',function() {
            checkMobileFun('registerForm');
            if(checkMobileFun('registerForm') && ($.trim($('#registerCode').val()) != '')){
                imgCodeRe('registerForm');
                $('#registerCode').val('');
            }else{
               $('.getCodeBtn').removeClass('getCodeBtnTrue')
            }
        })
        //注册密码验证
        $('#registerPwd').on('blur',function() {
            checkPwdFun('registerForm');
        })
        //注册图片验证码
        $('#registerCode').on('blur',function() {
            var getCodeBtn = $('.getCodeBtn');
            if(checkCodedFun('registerForm') && checkMobileFun('registerForm')){
                var phoneNumber = $.trim($("#registerMobile").val());
                var captcha_0 = $('#registerForm').find('input[name="captcha_0"]').val();
                var captcha_1 = $('#registerForm').find('#registerCode').val();
                $.ajax({
                    url: "/api/captcha_validation/",
                    type: "POST",
                    data: {
                        captcha_0: captcha_0,
                        captcha_1: captcha_1
                    }
                }).success(function() {
                    getCodeBtn.addClass('getCodeBtnTrue')
                }).fail(function(xhr) {
                    getCodeBtn.removeClass('getCodeBtnTrue')
                    var result = JSON.parse(xhr.responseText);
                    $('#registerForm').find('.loginError').text(result.message)
                });
            }else{
                getCodeBtn.removeClass('getCodeBtnTrue')
            }
        })
        //注册短信验证码
        $('#registerSMSCode').on('blur',function() {
            checkCodedFun('registerForm','re');
        })
        //刷新图片验证码
        $('#registerRefresh').on('click',function(){
            imgCodeRe('registerForm');
        })
    }


    imgCodeRe('registerForm');

    $('.SMELI').delegate('.getCodeBtnTrue','click',function(){
      var count, element, intervalId, phoneNumber, timerFunction;
      element = $('.getCodeBtnTrue');
      phoneNumber = $.trim($("#registerMobile").val());
      $.ajax({
        url: "/api/phone_validation_code/register/" + phoneNumber + "/",
        type: "POST"
      }).done(function() {
        count = 5;
        $(element).attr('disabled', 'disabled').addClass('buttonGray');
        $('.voiceValidate').attr('disabled', 'disabled');
        timerFunction = function() {
            if (count >= 1) {
              count--;
              return $(element).text('已经发送(' + count + ')');
            } else {
              clearInterval(intervalId);
              $(element).text('重新获取').removeAttr('disabled').removeClass('buttonGray');
              $('.voice').show();
              $('.voiceValidate').removeAttr('disabled');
              return $('.voice').html('没有收到验证码？请尝试<a href="" class="voiceValidate">语音验证</a>');
            }
        };
        timerFunction();
        return intervalId = setInterval(timerFunction, 1000);
        intervalId;
      }).fail(function(xhr) {
        clearInterval(intervalId);
        $(element).text('重新获取').removeAttr('disabled').removeClass('buttonGray');
        var result = JSON.parse(xhr.responseText);
        $('#registerForm').find('.loginError').text(result.message);
      });
    })

    $('.voice').delegate('.voiceValidate','click',function(e){
        e.preventDefault();
        var element = $('.voice');
        return $.ajax({
            url: '/api/ytx/send_voice_code/',
            type: "POST",
            data: {
                phone: $.trim($("#registerMobile").val())
            }
        }).success(function(json) {
            var button, count, intervalId, timerFunction;
            if (json.ret_code === 0) {
                count = 60;
                button = $(".voiceValidate");
                button.attr('disabled', 'disabled').addClass('buttonGray');
                timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return element.text('语音验证码已经发送，请注意接听（' + count + '）');
                    } else {
                        clearInterval(intervalId);
                        element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voiceValidate">语音验证</a>');
                        button.removeAttr('disabled').removeClass('buttonGray');
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            } else {
                return element.html('系统繁忙请尝试短信验证码');
            }
        });
    })

    $('#registerSubmit').on('click',function(){
        var error = $('#registerForm').find('.loginError');
         if(checkMobileFun('registerForm') && checkCodedFun('registerForm') && checkPwdFun('registerForm') && checkCodedFun('registerForm','re')){
            if($("#agreement").is(':checked')) {
                error.text('');
                var identifier, captcha_0,captcha_1,password, validate_code,invitecode;
                identifier = $('#registerMobile').val();
                captcha_0 = $('#registerForm').find('input[name="captcha_0"]').val();
                captcha_1 = $('#registerForm').find('#registerCode').val();
                password = $('#registerPwd').val();
                validate_code = $('#registerSMSCode').val();
                invitecode = $('#invitecode').val();
                $.ajax({
                    url: '/accounts/register/ajax/',
                    type: "POST",
                    data: {
                        identifier : identifier,
                        captcha_0 : captcha_0,
                        captcha_1 : captcha_1,
                        password: password,
                        validate_code: validate_code,
                        invitecode : invitecode
                    }
                }).done(function () {
                    location.reload();
                }).fail(function (xhr) {
                    var result = JSON.parse(xhr.responseText);
                    if(result.message.invitecode != undefined){
                        error.text(result.message.invitecode)
                    }else{
                        error.text(result.message.validate_code)
                    }
                });
            }else{
                error.text('请查看网利宝注册协议');
            }
         }
    })
});