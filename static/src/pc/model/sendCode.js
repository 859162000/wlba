 define(['jquery'], function ($) {
    var sendSMSCode ={}
    jQuery.extend(sendSMSCode, {
        defaults :{
            sendCodeBtn :'button-get-code-btn',   //绑定按钮ID
            hasCallBack : false  //回调
        },
        initFun : function(){
            //获取图片验证码弹框
            var alertSter = '<div id="img-code-div" class="modalStyle modal">'
                          +'<div class="form-row">'
                          +'<label class="img-code-label">请输入验证码：</label>'
                          +'<input type="hidden" id="id_captcha_0" name="captcha_0" autocomplete="off" value="">'
                          +'<input type="text" id="id_captcha_1" name="captcha_1" autocomplete="off" placeholder="请输入计算结果" maxlength="4" class="captcha valid">'
                          +'<img alt="captcha" src="" class="captcha captcha-img">'
                          +'<button type="button" style="color:rgb(16, 93, 195)" class="captcha-refresh">刷新</button>'
                          +'</div><div class="code-img-error"></div><div class="clearfix tc"><span id="submit-code-img" class="submit-code-img">确定</span></div></div>'
            $('body').append(alertSter);
        },
        sendImgCode : function(){  //弹框
            $submit = $('#'+this.defaults.sendCodeBtn);
            $submit.on('click',function(){
                $('#img-code-div').modal();
                $('#img-code-div').find('#id_captcha_1').val('');
                this.captchaRefresh();
            })
        },
        captchaRefreshClick : function(){
            $('#img-code-div').delegate('.captcha-refresh','click',function() {
                this.captchaRefresh();
            })
        },
        captchaRefresh : function(){         //刷新验证码
            var url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
            $.getJSON(url, {}, function(json) {
                $('input[name="captcha_0"]').val(json.key);
                $('img.captcha').attr('src', json.image_url);
            });
        },
        sendValidateCode : function(){
            $('#submit-code-img').on('click',function(){
                var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction, par;
                element = $('#'+self.defaults.sendCodeBtn);
                if ($(element).attr('disabled')) {
                    return;
                }
                phoneNumber = $(element).attr("data-phone");
                par =  $('#img-code-div');
                captcha_0 = par.find('#id_captcha_0').val();
                captcha_1 = par.find('.captcha').val();
                $.ajax({
                    url: "/api/phone_validation_code/" + phoneNumber + "/",
                    type: "POST",
                    data: {
                      captcha_0: captcha_0,
                      captcha_1: captcha_1
                    }
                }).fail(function(xhr) {
                    clearInterval(intervalId);
                    $(element).text('重新获取').removeAttr('disabled').addClass('button-red').removeClass('button-gray');
                    var result = JSON.parse(xhr.responseText);
                    if (result.type === 'captcha') {
                      $("#submit-code-img").parent().parent().find('.code-img-error').html(result.message);
                    } else {
                      if (xhr.status >= 400) {
                        return tool.modalAlert({
                          title: '温馨提示',
                          msg: result.message
                        });
                      }
                    }
                }).success(function() {
                    element.attr('disabled', 'disabled').removeClass('button-red').addClass('button-gray');
                    $('.voice-validate').attr('disabled', 'disabled');
                    $.modal.close();
                });
                intervalId;
                count = 60;
                $(element).attr('disabled', 'disabled').addClass('disabled');
                $('.voice-validate').attr('disabled', 'disabled');
                timerFunction = function() {
                    if (count >= 1) {
                      count--;
                      return $(element).text('重新获取(' + count + ')');
                    } else {
                      clearInterval(intervalId);
                      $(element).text('重新获取').removeAttr('disabled').removeClass('button-gray');
                      $('.voice').removeClass('hidden');
                      $('.voice-validate').removeAttr('disabled');
                      return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            })
        },
        setup : function(options){  //初始化
            this.sendCodeBtn = options.sendCodeBtn;
            this.initFun();
            this.sendImgCode();
            this.captchaRefreshClick();
            this.sendValidateCode();
        },
        sendSMSCodeInit : function(options) {
            sendSMSCode.setup(options);
        }
    })
    return {

    }


    ////图片验证码
    //$('#button-get-code-btn').click(function() {
    //  var url;
    //  $('#img-code-div2').modal();
    //  $('#img-code-div2').find('#id_captcha_1').val('');
    //  url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
    //  return $.getJSON(url, {}, function(json) {
    //    $('input[name="captcha_0"]').val(json.key);
    //    return $('img.captcha').attr('src', json.image_url);
    //  });
    //});
    ////刷新验证码
    //$('.captcha-refresh').on('click',function(){
    //    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
    //  return $.getJSON(url, {}, function(json) {
    //    $('input[name="captcha_0"]').val(json.key);
    //    return $('img.captcha').attr('src', json.image_url);
    //  });
    //})
    ////短信验证码
    //$("#submit-code-img4").click(function(e) {
    //  var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction;
    //  element = $('#button-get-code-btn');
    //  if ($(element).attr('disabled')) {
    //    return;
    //  }
    //  phoneNumber = $(element).attr("data-phone");
    //  captcha_0 = $(this).parents('form').find('#id_captcha_0').val();
    //  captcha_1 = $(this).parents('form').find('.captcha').val();
    //  $.ajax({
    //    url: "/api/phone_validation_code/" + phoneNumber + "/",
    //    type: "POST",
    //    data: {
    //      captcha_0: captcha_0,
    //      captcha_1: captcha_1
    //    }
    //  }).fail(function(xhr) {
    //    var result;
    //    clearInterval(intervalId);
    //    $(element).text('重新获取');
    //    $(element).removeAttr('disabled');
    //    $(element).addClass('button-red');
    //    $(element).removeClass('button-gray');
    //    result = JSON.parse(xhr.responseText);
    //    if (result.type === 'captcha') {
    //      return $("#submit-code-img4").parent().parent().find('.code-img-error').html(result.message);
    //    } else {
    //      if (xhr.status >= 400) {
    //        return tool.modalAlert({
    //          title: '温馨提示',
    //          msg: result.message
    //        });
    //      }
    //    }
    //  }).success(function() {
    //    element.attr('disabled', 'disabled');
    //    element.removeClass('button-red');
    //    element.addClass('button-gray');
    //    $('.voice-validate').attr('disabled', 'disabled');
    //    return $.modal.close();
    //  });
    //  intervalId;
    //  count = 60;
    //  $(element).attr('disabled', 'disabled');
    //  $(element).addClass('disabled');
    //  $('.voice-validate').attr('disabled', 'disabled');
    //  timerFunction = function() {
    //    if (count >= 1) {
    //      count--;
    //      return $(element).text('重新获取(' + count + ')');
    //    } else {
    //      clearInterval(intervalId);
    //      $(element).text('重新获取');
    //      $(element).removeAttr('disabled');
    //      $(element).removeClass('disabled');
    //      $(element).removeClass('button-gray');
    //      $('.voice').removeClass('hidden');
    //      $('.voice-validate').removeAttr('disabled');
    //      return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
    //    }
    //  };
    //  timerFunction();
    //  return intervalId = setInterval(timerFunction, 1000);
    //});
    //$(".voice").on('click', '.voice-validate', function(e) {
    //  var element, url;
    //  e.preventDefault();
    //  if ($(this).attr('disabled') && $(this).attr('disabled') === 'disabled') {
    //    return;
    //  }
    //  element = $('.voice .span12-omega');
    //  url = $(this).attr('href');
    //  return $.ajax({
    //    url: url,
    //    type: "POST",
    //    data: {
    //      phone: $("#button-get-code-btn").attr('data-phone').trim()
    //    }
    //  }).success(function(json) {
    //    var button, count, intervalId, timerFunction;
    //    if (json.ret_code === 0) {
    //      intervalId;
    //      count = 60;
    //      button = $("#button-get-code-btn");
    //      button.attr('disabled', 'disabled');
    //      button.addClass('button-gray');
    //      $('.voice').addClass('tip');
    //      timerFunction = function() {
    //        if (count >= 1) {
    //          count--;
    //          return element.text('语音验证码已经发送，请注意接听（' + count + '）');
    //        } else {
    //          clearInterval(intervalId);
    //          element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
    //          element.removeAttr('disabled');
    //          button.removeAttr('disabled');
    //          button.addClass('button-red');
    //          button.removeClass('button-gray');
    //          return $('.voice').removeClass('tip');
    //        }
    //      };
    //      timerFunction();
    //      return intervalId = setInterval(timerFunction, 1000);
    //    } else {
    //      return element.html('系统繁忙请尝试短信验证码');
    //    }
    //  }).fail(function(xhr) {
    //    if (xhr.status > 400) {
    //      return tool.modalAlert({
    //        title: '温馨提示',
    //        msg: result.message
    //      });
    //    }
    //  });
    //});
});