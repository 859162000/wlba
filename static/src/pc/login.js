require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder',
        'csrf' : 'model/csrf',
        //'jquery.cookie': 'lib/jquery.cookie'
    },
    shim: {
        'jquery.placeholder': ['jquery']
    }
});
require(['jquery','jquery.placeholder', 'csrf'], function( $ ,placeholder) {
    var statusV = 0
    //-------------初始化----------//
    pageInitFun = function(){
        //文本框的得到和失去光标
        $('.placeholderInput').placeholder();
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
        //Enter事件
        $(this).keydown(function(event){
            if(event.keyCode == '13'){
                if($('.i-mod-content').hasClass('curr')){
                    $('#loginSubmit').click();
                }else{
                    $('#registerSubmit').click();
                }
            }
        });
    }
    pageInitFun();
    //-------------初始化END----------//

    //极验一次验证
    var array= {};
    fastTestOne = function(type){
        statusV = 1;
        $.ajax({
            type: 'POST',
            url: '/api/geetest/',
            dataType: 'json',
            timeout: 5000,
            data:{
                type : 'get'
            },
            success: function (data) {
                var config = {
                    gt: data.gt,
                    challenge: data.challenge,
                    product: "float",
                    offline: !data.success
                }
                $('.captcha-box').show();
                initGeetest(config, function (captchaObj) {
                    captchaObj.appendTo("#captcha-box");
                    captchaObj.onSuccess(function () {
                        array = captchaObj.getValidate();
                        $('#captcha-status').val('true');
                        type == 'regist' ? checkCodeIsNoFun() : null;
                        statusV = 0;
                    });
                    captchaObj.onFail(function(){
                        $('#captcha-status').val(captchaObj.getValidate())
                    });
                    captchaObj.onRefresh(function(){
                        $('#captcha-status').val('');
                        type == 'regist' ? checkCodeIsNoFun() : null;
                    })
                    captchaObj.getValidate();
                })
                $('#check-tag').val('false');
                statusV = 0;
            },
            error: function(XMLHttpRequest,status){
                type == 'regist' ? $('.captcha-box1').show() : $('.captcha-box').hide();
                $('#check-tag').val('falses');
               if(type == 'regist'){
                   $('.getCodeBtn').removeClass('getCodeBtnTrue').addClass('buttonGray');
                   $('#registerSMSCode').val('');
                }
                statusV = 0;
            }
        });
    }
    //极验二次验证
    fastTestTwo = function(fun,type){
        if($('#captcha-status').val() == 'true') {
            statusV = 1;
            $.ajax({
                type: 'POST',
                url: '/api/geetest/',
                dataType: 'json',
                timeout: 5000,
                data: {
                    type: 'validate',
                    geetest_validate: array.geetest_validate,
                    geetest_seccode: array.geetest_seccode,
                    geetest_challenge: array.geetest_challenge
                }
            }).success(function (data) {
                fun();
                statusV = 0;
            }).error(function (xhr) {
                if(type=='login'){
                    fun();
                }else{
                    $('.loginError').text('图片验证码错误');
                    $('.getCodeBtn').removeClass('getCodeBtnTrue').addClass('buttonGray');
                    $('#registerSMSCode').val('');
                    $('.captcha-box1').show();$('.captcha-box').hide();
                    $('#check-tag').val('');
                }
                statusV = 0;
            })
        }else{
            $('.loginError').text('图片验证码错误');
            return;
        }
    }

    //-------------表单验证----------//
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
        var checkStatus = false,str = ''
        if(re == 're'){
            var self = $.trim($('#'+form).find('#registerSMSCode').val());
            str = '短信';
        }
        else{
            var self = $.trim($('#'+form).find('.checkCode').val());
            str = '图片';
        }
        if(self == '') {
            $('#'+form).find('.loginError').text('请输入'+ str +'验证码');
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
      return re.test(identifier);
    }
    //刷新验证码
    imgCodeRe = function(form){
        url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
        $.getJSON(url, {}, function(json) {
          $('#'+form).find('input[name="captcha_0"]').val(json.key);
          $('#'+form).find('img.captchaImg').attr('src', json.image_url);
        });
    }

    //-------------表单验证END----------//


    //验证图片验证码
    checkImgCodeFun = function(getCodeBtn){
        var phoneNumber = $.trim($("#registerMobile").val());
        var captcha_0 = $('#registerForm').find('input[name="captcha_0"]').val();
        var captcha_1 = $('#registerForm').find('#registerCode').val();
        $.ajax({
            url: "/api/captcha_validation/" + phoneNumber + "/",
            type: "POST",
            data: {
                captcha_0: captcha_0,
                captcha_1: captcha_1
            }
        }).success(function() {
            getCodeBtn.addClass('getCodeBtnTrue').removeClass('buttonGray');
        }).fail(function(xhr) {
            getCodeBtn.removeClass('getCodeBtnTrue').addClass('buttonGray');
            var result = JSON.parse(xhr.responseText);
            $('#registerForm').find('.loginError').text(result.message)
        });
    }
    //短信验证
    checkSEMFun = function(){
        var count, element, intervalId, phoneNumber, timerFunction;
        element = $('.getCodeBtnTrue');
        phoneNumber = $.trim($("#registerMobile").val());
        var captcha_0 = $('#registerForm').find('input[name="captcha_0"]').val();
        var captcha_1 = $('#registerForm').find('#registerCode').val();
        if($('#check-tag').val() == 'false'){
            datas = 'type=geetest'+'&geetest_validate='+array.geetest_validate+'&geetest_seccode='+array.geetest_seccode+'&geetest_challenge='+array.geetest_challenge;
        }else{
            datas = 'captcha_0='+captcha_0+'&captcha_1='+captcha_1;
        }
        $.ajax({
            url: "/api/phone_validation_code/register/" + phoneNumber + "/",
            type: "POST",
            data: datas
        }).done(function() {
            count = 60;
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
            var result = JSON.parse(xhr.responseText);
            $('#registerForm').find('.loginError').text(result.message);
            imgCodeRe('registerForm');
            $('#registerCode').val('').focus();
            $('.getCodeBtn').addClass('buttonGray').removeClass('getCodeBtnTrue');
        });
    }
    //语音验证码
    setVoidCodeFun = function(){
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
    }


    //-------------登录模块初始化-------------//
    loginInitFun = function(){
        $('#loginMobile').on('blur',function() {
            checkMobileFun('loginForm');
        })
        $('#loginPwd').on('blur',function() {
            checkPwdFun('loginForm');
        })
        //alert($.cookie("counts"))
        //设置cookie
        //if ($.cookie("counts") == null || $.cookie("counts") == 'null') {
        //    var o = {name: "counts", value: 0},
        //        str = JSON.stringify(o);
        //    $.cookie("counts", str, { path: '/'});
        //}else{
        //    var str = $.cookie("counts"),
        //        o = JSON.parse(str);
        //    if(o.value >= 2){
        //        fastTestOne('login');
        //    }
        //}
        //刷新图片验证码
        $('#loginRefresh').on('click',function(){
            imgCodeRe('loginForm')
        })
        //提交登录表单
        $('#loginSubmit').on('click',function(){
            if(statusV == 0){
                statusV = 1;
                if(checkMobileFun('loginForm') && checkPwdFun('loginForm')){
                    if($('#check-tag').val() == 'false'){
                        fastTestTwo(loginSubmitFun,'login');
                    }else{
                        loginSubmitFun();
                    }
                }
            }
        })
        //登录
        var loginSubmitFun = function(){
            statusV = 1;
            if($('#remember_me').is(':checked')){
                var remember_me = 'remember_me';
            }
            $.ajax({
                url: '/accounts/login/ajax/',
                type: "POST",
                data: {
                    identifier: $('#loginMobile').val(),
                    password: $('#loginPwd').val(),
                    remember_me: remember_me
                }
            }).done(function (xhr) {
                //var o = {name: "counts", value: 0},
                //str = JSON.stringify(o);
                //$.cookie("counts", str, { path: '/'});
                //xhr.ret_code == '7001' ? fastTestOne('login') : null ;
                if(xhr.ret_code == '7001'){
                    if($('#check-tag').val() == '') {
                        fastTestOne('login')
                        //statusV = 0;
                    }
                    if (xhr.message != undefined) {
                        $('#loginForm').find('.loginError').text(xhr.message);
                    }
                }else{
                    var next = _getQueryStringByName('next') == '' ? '/' : _getQueryStringByName('next');
                    window.location.href = next;
                }
            }).fail(function (xhr) {
                //var str1 = $.cookie("counts");
                //if (($.cookie("counts") != null) && ($.cookie("counts") != 'null')) {
                //    var o1 = JSON.parse(str1),
                //        clickCount = o1.value + 1,
                //        o = {name: "counts", value: clickCount},
                //        str = JSON.stringify(o);
                //    $.cookie("counts", str, { path: '/'});
                //    if (clickCount == 2) {
                //        fastTestOne('login');
                //    }
                //}
                var result = JSON.parse(xhr.responseText);
                if (result.message.__all__ != undefined) {
                    $('#loginForm').find('.loginError').text(result.message.__all__[0]);
                } else if (result.message.captcha != undefined) {
                    $('#loginForm').find('.loginError').text(result.message.captcha[0]);
                }
                statusV = 0;
            });
        }
    }
    //-------------登录模块初始化END-------------//



    //-------------注册模块初始化-------------//
    registerInitFun = function(){
        //极验一次验证
        fastTestOne('regist')
       //密码type
        $('.pwdStatus').on('click',function(){
            var self = $(this);
            if(self.hasClass('icon-eye03')){
                $('#textPwdInput').show();
                $('#passWordInput').hide();
            }else{
                $('#passWordInput').show();
                $('#textPwdInput').hide();
            }
        })
        $('.registerPwd').on('change',function(){
            var val = $(this).val();
            $('#registerForm').find('input[name="password"]').val(val)
        })
        //注册手机号验证
        $('#registerMobile').on('keyup',function() {
            checkCodeIsNoFun();
        })

        checkCodeIsNoFun = function(){
            if(checkMobileFun('registerForm')){
                //$('#registerCode').val() != '' ? $('.getCodeBtn').removeClass('buttonGray').addClass('getCodeBtnTrue') : $('.getCodeBtn').removeClass('getCodeBtnTrue').addClass('buttonGray');
                if($('#captcha-status').val() == 'false' || $('#captcha-status').val() == ''){
                    $('.getCodeBtn').removeClass('getCodeBtnTrue').addClass('buttonGray');
                }else{
                    $('.getCodeBtn').removeClass('buttonGray').addClass('getCodeBtnTrue');
                }
            }else{
                $('.getCodeBtn').removeClass('getCodeBtnTrue').addClass('buttonGray');
            }
        }

        //注册密码验证
        $('.registerPwd').on('blur',function() {
            checkPwdFun('registerForm');
        })
        //注册图片验证码
        $('#registerCode').on('keyup',function() {
            var getCodeBtn = $('.getCodeBtn');
            if($('#registerCode').val() != ''){
                if(checkMobileFun('registerForm'))
                {
                    getCodeBtn.removeClass('buttonGray').addClass('getCodeBtnTrue');
                }
            }else{
                getCodeBtn.removeClass('getCodeBtnTrue').addClass('buttonGray');
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
        //初始化图片验证码
        imgCodeRe('registerForm');
        //发送短信验证码
        $('.SMELI').delegate('.getCodeBtnTrue','click',function(){
            if(checkMobileFun('registerForm')){
                checkSEMFun();
            }
        })
        //发送语音验证
        $('.voice').delegate('.voiceValidate','click',function(e){
            e.preventDefault();
            setVoidCodeFun()
        })
        //提交注册表单
        var btnSelf = $('#registerSubmit'),error = $('#registerForm').find('.loginError');
        $('#registerSubmit').on('click',function(){
            var btnSelf = $(this);
            if (statusV == 0) {
                if($('#check-tag').val() == 'false'){
                    if (checkMobileFun('registerForm') && checkPwdFun('registerForm') && checkCodedFun('registerForm', 're')) {
                        if ($("#agreement").is(':checked')) {
                            error.text('');statusV = 1;
                            $('#check-tag').val() == 'falses' ?  submitRegist() : fastTestTwo(submitRegist);
                        } else {
                            error.text('请查看网利宝注册协议');
                        }
                    }
                }else{
                    if (checkMobileFun('registerForm') && checkCodedFun('registerForm') && checkPwdFun('registerForm') && checkCodedFun('registerForm', 're')) {
                        if ($("#agreement").is(':checked')) {
                            error.text('');statusV = 1;
                            submitRegist();
                        } else {
                            error.text('请查看网利宝注册协议');
                        }
                    }
                }
            }
        })

        //注册
        var submitRegist = function(){
            var identifier = $('#registerMobile').val(),
                captcha_0 = $('#registerForm').find('input[name="captcha_0"]').val(),
                captcha_1 = $('#registerForm').find('#registerCode').val(),
                password = $('.registerPwd').val(),
                validate_code = $('#registerSMSCode').val(),
                invitecode = $('#invitecode').val();
            $.ajax({
                url: '/accounts/register/ajax/',
                type: "POST",
                data: {
                    identifier: identifier,
                    captcha_0: captcha_0,
                    captcha_1: captcha_1,
                    password: password,
                    validate_code: validate_code,
                    invitecode: invitecode
                }
            }).done(function () {
                var next = _getQueryStringByName('next') == '' ? '/accounts/register/first/' : _getQueryStringByName('next');
                window.location.href = next;

            }).fail(function (xhr) {
                var result = JSON.parse(xhr.responseText);
                if (result.message.invitecode != undefined) {
                    error.text(result.message.invitecode)
                } else if (result.message.identifier != undefined) {
                    error.text(result.message.identifier)
                } else if (result.message.captcha_1 != undefined) {
                    error.text(result.message.captcha_1)
                } else {
                    error.text(result.message.validate_code)
                }
                statusV = 0;
            });
        }
    }
    //-------------登录模块初始化END-------------//
    $('.i-mod-content').hasClass('curr') ? loginInitFun() : registerInitFun();
});