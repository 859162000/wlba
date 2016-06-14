(function() {
  require.config({
    paths: {
      'jquery.placeholder': 'lib/jquery.placeholder',
      tools: 'lib/modal.tools',
      'csrf' : 'model/csrf'
    },
    shim: {
      'jquery.placeholder': ['jquery']
    }
  });

  define(['jquery', "tools", 'jquery.placeholder', 'csrf'], function($, tool, placeholder) {
    var _showModal,activityRegister ={};
    $('#check-tag').val('');
    jQuery.extend(activityRegister, {
        registerTitle :'',    //注册框标语
        isNOShow : '1',      //是否显示
        hasCallBack : false, //回调
        buttonFont : '',
        activityUrl : '',
        initFun : function(){
            var array= {}, statusV = 0, handler = {};
            $('.biaoyu').text(this.registerTitle);
            this.buttonFont != undefined ? $('#register_submit').text(this.buttonFont) : $('#register_submit').text('立即注册');

            var activityUrl = this.activityUrl
            $('#goLogin').on('click',function(){
                window.location.href = '/accounts/login/?next='+activityUrl;
            })

            this.fastTestOne();
        },
        //极验一次验证
        fastTestOne : function(type){
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
                    handler = function (captchaObj) {
                        captchaObj.appendTo("#captcha-box");
                        captchaObj.onSuccess(function () {
                            array = captchaObj.getValidate();
                            $('#captcha-status').val('true');
                            activityRegister.checkCodeIsNoFun();
                            statusV = 0;
                        });
                        captchaObj.onFail(function(){
                            $('#captcha-status').val(captchaObj.getValidate())
                        });
                        captchaObj.onRefresh(function(){
                            $('#captcha-status').val('');
                            activityRegister.heckCodeIsNoFun()
                        })
                        captchaObj.getValidate();
                    }
                    initGeetest(config, handler);
                    $('#check-tag').val('false');
                    statusV = 0;
                },
                error: function(XMLHttpRequest,status){
                    $('.captcha-box1').show();$('.captcha-box').hide();
                    $('#check-tag').val('falses');
                    $('#img-code').removeClass('button-orange').addClass('buttonDisabled');
                    $('#id_validate_code').val('');
                    statusV = 0;
                }
            });
        },
        //极验二次验证
        fastTestTwo : function(fun){
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
                    fun();statusV = 0;
                }).error(function (xhr) {
                    $('#aug-form-row-eroor').text('图片验证码错误');
                    $('#img-code').removeClass('button-orange').addClass('buttonDisabled');
                    $('#id_validate_code').val('');
                    $('.captcha-box1').show();$('.captcha-box').hide();
                    $('#check-tag').val('');
                    statusV = 0;
                })
            }else{
                $('#aug-form-row-eroor').text('图片验证码错误');
                return;
            }
        },
        checkCodeIsNoFun : function(){
          if(activityRegister.checkMobile($.trim($("#reg_identifier").val()))){
                if($('#captcha-status').val() == 'false' || $('#captcha-status').val() == ''){
                    $('#img-code').removeClass('button-orange').addClass('buttonDisabled');
                }else{
                    $('#img-code').removeClass('buttonDisabled').addClass('button-orange');
                }
            }else{
                $('#img-code').removeClass('button-orange').addClass('buttonDisabled');
            }
        },
        imgCodeCheck : function(){
            $('#registerCode').on('keyup',function() {
                var getCodeBtn = $('#img-code');
                if($('#registerCode').val() != ''){
                    if(activityRegister.checkMobileFun())
                    {
                        getCodeBtn.removeClass('buttonDisabled').addClass('button-orange');
                    }
                }else{
                    getCodeBtn.removeClass('button-orange').addClass('buttonDisabled');
                }
            })
        },
        imgCodeFunNew : function(){
            activityRegister.imgCodeRe('register-modal-form');
        },
        checkMobileFun : function(){
            var checkStatus = false, self = $.trim($('#reg_identifier').val());
            if(!activityRegister.checkMobile(self)){
                $('#aug-form-row-eroor').text('请输入正确手机号');
                checkStatus = false;
            }else{
                $('#aug-form-row-eroor').text('');
                checkStatus = true;
            }
            return checkStatus;
        },
       checkPwdFun : function(){
            var registError = $('#aug-form-row-eroor');
            var checkStatus = false,self = $.trim($('#reg_password').val());
            if(self == ''){
               registError.text('请输入密码');
               checkStatus = false;
            }else if(self.length < 6){
               registError.text('密码最少6位');
               checkStatus = false;
            }else if(self.length > 20){
               registError.text('密码最多20位');
               checkStatus = false;
            }else{
               registError.text('');
               checkStatus = true;
               statusV = 0;
            }
            return checkStatus;
        },
        checkCodedFun : function(form,re){
            var checkStatus = false,str = ''
            if(re == 're'){
                var self = $.trim($('#'+form).find('#id_validate_code').val());
                str = '短信';
            }
            else{
                var self = $.trim($('#'+form).find('#registerCode').val());
                str = '图片';
            }
            if(self == '') {
                $('#'+form).find('#aug-form-row-eroor').show().text('请输入'+ str +'验证码');
                checkStatus = false;
            }else{
                $('#'+form).find('#aug-form-row-eroor').text('');
                checkStatus = true;
            }
            return checkStatus;
        },
        registerMobileKeyUp : function(){
            //注册手机号验证
            $('#reg_identifier').on('keyup',function() {
                activityRegister.checkCodeIsNoFun();
            })
        },
        checkMobile : function(identifier) {  //验证手机号
          var re = /^1\d{10}$/;
          return re.test(identifier);
        },
        captchaRefresh : function(){   //刷新图片验证码
            $('.captcha-refresh').click(function() {
              activityRegister.imgCodeRe();
            });
        },
        registerMobile : function(){
            activityRegister.checkCodeIsNoFun();
        },
        //input验证
        inputValidateFun : function(){
            var errorLabel = $('#aug-form-row-eroor');
            $('#reg_identifier,#id_validate_code').on('keyup',function(){
              errorLabel.text('')
            })
            $('input, textarea').placeholder();
             //文本框的得到和失去光标
            var zhi;
            $('.com-tu').on("focus", function () {
                var self = $(this)
                if (self.attr('placeholder')) {
                  zhi = self.attr('placeholder');
                }
                self.attr('placeholder', '');
            });

            $('.com-tu').on('blur', function () {
                $(this).attr('placeholder', zhi)
            })
        },
        //刷新验证码
        imgCodeRe : function(form){
            url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
            $.getJSON(url, {}, function(json) {
              $('#'+form).find('input[name="captcha_0"]').val(json.key);
              $('#'+form).find('img.captcha').attr('src', json.image_url);
            });
        },
        //发送验证码
        imgCodePost : function(){
            $('#img-code').click(function() {
                var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction;
                element = $('#img-code');
                phoneNumber = $.trim($("#reg_identifier").val());
                captcha_0 = $('#register-modal-form').find('input[name="captcha_0"]').val();
                captcha_1 = $('#register-modal-form').find('input[name="captcha_1"]').val();
                if($('#check-tag').val() == 'false'){
                    datas = 'type=geetest'+'&geetest_validate='+array.geetest_validate+'&geetest_seccode='+array.geetest_seccode+'&geetest_challenge='+array.geetest_challenge;
                }else{
                    datas = 'captcha_0='+captcha_0+'&captcha_1='+captcha_1;
                }
                $.ajax({
                    url: "/api/phone_validation_code/register/" + phoneNumber + "/",
                    type: "POST",
                    data: datas
                }).success(function() {
                    element.attr('disabled', 'disabled').addClass('buttonDisabled');
                    $('.voice-validate').attr('disabled', 'disabled');
                    $('#aug-code,#aug-center').hide();
                }).fail(function(xhr) {
                    clearInterval(intervalId);
                    $(element).text('重新获取').removeAttr('disabled').removeClass('buttonDisabled');
                    var result = JSON.parse(xhr.responseText);
                    if (result.type === 'captcha') {
                        $('#aug-form-row-eroor').text(result.message)
                    } else {
                        if (xhr.status >= 400) {
                            $('#aug-code,#aug-center').hide();
                            return tool.modalAlert({
                                title: '温馨提示',
                                msg: result.message,
                                callback_ok: _showModal
                            });
                        }
                    }
                });
                count = 180;
                $(element).attr('disabled', 'disabled').addClass('buttonDisabled');
                $('.voice-validate').attr('disabled', 'disabled');
                timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $(element).text('已经发送(' + count + ')');
                    } else {
                        clearInterval(intervalId);
                        $(element).text('重新获取').removeAttr('disabled').removeClass('buttonDisabled');
                        $('.span12-omega').removeClass('hidden');
                        $('.voice-validate').removeAttr('disabled');
                        return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            });
        },
        //语音验证码
        voiceValidateFun : function(){
            return $(".voice").on('click', '.voice-validate', function(e) {
                var element, isMobile, url;
                e.preventDefault();
                isMobile = activityRegister.checkMobile($("#reg_identifier").val().trim());
                if (!isMobile) {
                    $("#id_type").val("phone");
                    $("#validate-code-container").show();
                    return;
                }
                if ($(this).attr('disabled') && $(this).attr('disabled') === 'disabled') {
                    return;
                }
                element = $('.voice .span12-omega');
                url = $(this).attr('href');
                return $.ajax({
                    url: url,
                    type: "POST",
                    data: {
                        phone: $("#reg_identifier").val().trim()
                    }
                }).success(function(json) {
                    var button, count, intervalId, timerFunction;
                    if (json.ret_code === 0) {
                        count = 60;
                        button = $("#button-get-validate-modal");
                        button.attr('disabled', 'disabled').addClass('buttonDisabled');
                        button.addClass('button-gray');
                        $('.voice').addClass('tip');
                        timerFunction = function() {
                            if (count >= 1) {
                                count--;
                                return element.text('语音验证码已经发送，请注意接听（' + count + '）');
                            } else {
                                clearInterval(intervalId);
                                element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
                                element.removeAttr('disabled');
                                button.removeAttr('disabled').removeClass('buttonDisabled');
                                button.addClass('button-red');
                                button.removeClass('button-gray');
                                return $('.voice').removeClass('tip');
                            }
                        };
                        timerFunction();
                        return intervalId = setInterval(timerFunction, 1000);
                    } else {
                        return element.html('系统繁忙请尝试短信验证码');
                    }
                });
            });
        },
        //提交表单
        registerSubmitFun : function(){
            $('#register_submit').on('click',function(){
                if (statusV == 0) {
                  var errorLabel = $('#aug-form-row-eroor');
                  if($('#check-tag').val() == 'false'){
                        if (activityRegister.checkMobileFun() && activityRegister.checkPwdFun() && activityRegister.checkCodedFun('register-modal-form', 're')) {
                            if ($("#agreement").is(':checked')) {
                                errorLabel.text('');statusV = 1;
                                $('#check-tag').val() == 'falses' ?  activityRegister.submitRegist() : activityRegister.fastTestTwo(activityRegister.submitRegist);
                            } else {
                                errorLabel.text('请查看网利宝注册协议');
                            }
                        }
                    }else{
                        if (activityRegister.checkMobileFun() && activityRegister.checkCodedFun('register-modal-form') && activityRegister.checkPwdFun() && activityRegister.checkCodedFun('register-modal-form', 're')) {
                            if ($("#agreement").is(':checked')) {
                                errorLabel.text('');statusV = 1;
                                activityRegister.submitRegist();
                            } else {
                                errorLabel.text('请查看网利宝注册协议');
                            }
                        }
                    }
                }

            })
        },
        submitRegist : function(){
                var identifier = $('#reg_identifier').val(),
                    captcha_0 = $('#register-modal-form').find('input[name="captcha_0"]').val(),
                    captcha_1 = $('#register-modal-form').find('#registerCode').val(),
                    password = $('#reg_password').val(),
                    validate_code = $('#id_validate_code').val();
            $.ajax({
                url: '/accounts/register/ajax/',
                type: "POST",
                data: {
                    identifier: identifier,
                    captcha_0: captcha_0,
                    captcha_1: captcha_1,
                    password: password,
                    validate_code: validate_code
                }
            }).done(function () {
                if(activityRegister.hasCallBack == true){
                    activityRegister.callBack();
                }else{
                    return location.reload();
                }

            }).fail(function (xhr) {
                var result = JSON.parse(xhr.responseText);
                $('#aug-form-row-eroor').text('* ' + result.message.validate_code)
                statusV = 0;
            });
        },
        setup : function(options){  //初始化
            this.registerTitle = options.registerTitle;
            this.isNOShow = options.isNOShow;
            this.hasCallBack = options.hasCallBack;
            this.buttonFont = options.buttonFont;
            this.callBack = options.callBack;    //回调函数
            this.activityUrl = options.activityUrl;

            if(this.isNOShow == '1'){
                activityRegister.initFun();
                activityRegister.imgCodeFunNew();
                activityRegister.imgCodePost();
                activityRegister.registerSubmitFun();
                activityRegister.captchaRefresh();
                activityRegister.voiceValidateFun();
                activityRegister.inputValidateFun();
                activityRegister.registerMobile();
                activityRegister.imgCodeCheck();
                activityRegister.registerMobileKeyUp();
            }else{
                $('#denglu').hide();
            }
        },
        activityRegisterInit : function(options) {
            activityRegister.setup(options);
        }
    })
      return {
        activityRegister : activityRegister
      }
  });
}).call(this);

