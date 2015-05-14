/**
 * Created by rsj217 on 15-5-14.
 */
(function(validate){
//  安全证书
  getCookie = function (name) {
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

csrfSafeMethod = function (method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
};

sameOrigin = function (url) {
    var host, origin, protocol, sr_origin;
    host = document.location.host;
    protocol = document.location.protocol;
    sr_origin = "//" + host;
    origin = protocol + sr_origin;
    return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
};

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
    }
});
//校验手机号
  var checkMobile = function(identifier) {
      var re;
      re = void 0;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
//  获取验证码
   $("#btn-validate-code").click(function(e) {
      var count, element, intervalId, phoneNumber, timerFunction;
      e.preventDefault();
      element = this;
      phoneNumber = $.trim($("#phone").val());
      if (checkMobile(phoneNumber)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Phone number checked, now send the valdiation code");
        }
        $.ajax({
          url: "/api/phone_validation_code/register/" + phoneNumber + "/",
          type: "POST"
        }).fail(function(xhr) {
          var result;
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          $(element).css({'background':'#f44336','color':'#fff'});
          $(element).removeClass('huoqu-ma-gray');
          result = JSON.parse(xhr.responseText);
          if (xhr.status === 429) {
              $('#wx-mobel-box p').text('系统繁忙，请稍候重试');
              $('#wx-mobel-box').show();
          } else {
              $('#wx-mobel-box p').text(result.message);
              $('#wx-mobel-box').show();
          }
        });
        intervalId;
        count = 60;
        $(element).attr('disabled', 'disabled');
        $(element).removeClass('pptv-huoqu-ma');
        $(element).css({'background':'#ccc','color':'#000'});
        $('.voice-validate').attr('disabled', 'disabled');
        timerFunction = function() {
          console.log(count)
          if (count >= 1) {
            count--;
            return $(element).text('已经发送(' + count + ')');
          } else {
            clearInterval(intervalId);
            $(element).removeAttr('disabled');
            $(element).css({'background':'#f44336','color':'#fff'});
            $(element).text('重新获取')
          }
        };
        timerFunction();
        return intervalId = setInterval(timerFunction, 1000);
      } else {
        $('#wx-mobel-box p').text('手机号不正确');
        $('#wx-mobel-box').show();
      }
    });

//  网利宝协议是否勾选
  $("#id").change(function(value) {
    if ($(this).attr("checked")) {
      $("#registerd").addClass("disabled");
      return $(this).removeAttr("checked");
    } else {
      $("#registerd").removeClass("disabled");
      return $(this).attr("checked", "checked");
    }
  });
  $("#registerd").click(function(e) {
    if ($(this).hasClass("disabled")) {
      e.preventDefault();
    }
  });
  $.validator.addMethod("emailOrPhone", function(value, element) {
    return backend.checkEmail(value) || backend.checkMobile(value);
  });
//  注册
   $('#registerd').on('click',function(){
     if($('#pw').val().length <= 6 && $('#pw').val().length >= 20){
       $('#wx-mobel-box p').text('密码长度在6到20位之间');
       $('#wx-mobel-box').show();
     }else if($('#pw').val()!=$('#pw2').val()){
       $('#wx-mobel-box p').text('密码不一致');
       $('#wx-mobel-box').show();
     }else{
       $.ajax({
        url: '/api/register/',
        type: "POST",
        data: {identifier:$('#phone').val(), validate_code:$('#validate-code').val(), password: $('#pw').val(), invite_code: 'koudianying'},
        success: function(data){
          if(data.ret_code==0){
            var str='<b>您已注册成功，请到网利宝官网进行投资理财<b><br>官网网址：www.wanglibao.com';
            console.log($('#wx-mobel-box p').text());
            $('#wx-mobel-box p').html(str);
            $('#wx-mobel-box').show();
          }else{
            $('#wx-mobel-box p').text(data.message);
            $('#wx-mobel-box').show();
          }
        }
      });
     }

     return false;
    });
//  消除模态框
  $('body').on('click',function(){
    $('#wx-mobel-box').hide();
  })


})(jQuery.validate);