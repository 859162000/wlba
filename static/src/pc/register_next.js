require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder',
        'jquery.modal': 'lib/jquery.modal.min',
        tools: 'lib/modal.tools'
    },
    shim: {
        'jquery.placeholder': ['jquery'],
        'jquery.modal': ['jquery']
    }
});
require(['jquery','jquery.placeholder',"tools"], function( $ ,placeholder, tool) {
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

    _getQueryStringByName = function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
    }

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
    /*实名认证*/
    $('#realName').on('click',function(){
        var userName = $('#userName'),nameId = $('#nameId');
        if($.trim(userName.val()) == ''){
            userName.next().html('<i></i>请输入姓名');
            return false;
        }else{
            userName.next().html('');
        }
        if($.trim(nameId.val()) == ''){
            nameId.next().html('<i></i>身份证号');
            return false;
        }else{
            reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
            if(!reg.test(nameId.val())){
                nameId.next().html('<i></i>身份证信息有误');
                return false;
            }else{
                nameId.next().html('');
            }
        }
       $.ajax({
            type: 'POST',
            url : '/api/id_validate/',
            data : {
                name: userName.val(),
                id_number: nameId.val()
            },
            success:function(data){
                if(!data.validate == 'true'){
                    return tool.modalAlert({title: '温馨提示',msg: '<div class="tc">认证失败</div>'});
                }else{
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: '<div class="tc">认证成功</div>',
                        callback_ok: function() {
                            window.location.href = '/pay/banks_for_register/';
                        }
                      });
                }
            },
            error:function(xhr){
                result = JSON.parse(xhr.responseText);
                return tool.modalAlert({title: '温馨提示',msg: result.message});
            }
        })
    })

    /*下拉框*/
    $('.select_bank').focus(function(){
        $(this).addClass('selected');
    })
    $('.select_bank').blur(function(){
        if($(this).val() == ''){
            $(this).removeClass('selected');
        }
    })

    /*绑卡*/
    $('#tieOnCard').on('click',function(){
        if(!$(this).hasClass('bunsNo')) {
            var checkStatus = true;
            $.each($('.checkCodeStatus'), function (i, o) {
                if ($(o).val() == '') {
                    $('.error-box').text($(o).attr('placeholder'));
                    checkStatus = false;
                    return false;
                }
            })
            if ((checkStatus) && ($('.error-box').text() == '')) {
                if ($('#order_id').val() === '') {
                    $('.error-box').text('请发送验证码');
                } else {
                    var bankId = $('.cardId').val(),
                        self = $(this);
                    self.addClass('bunsNo');
                    $.ajax({
                        url: '/api/pay/cnp/dynnum_new/',
                        data: {
                            Storable_no: bankId.substr(0, 4) + bankId.substr(bankId.length - 4),
                            card_no: bankId,
                            vcode: $('.checkSEMCode').val(),
                            order_id: $('#order_id').val(),
                            token: $('#token').val(),
                            phone: $('.mobileCode').val(),
                            device_id: ''
                        },
                        type: 'post'
                    }).done(function (xhr) {
                        if (xhr.ret_code === 0 || xhr.ret_code === 22000) {
                            window.location.href = '/accounts/register/three/';
                        } else {
                            $('.error-box').text(xhr.message);
                            self.removeClass('bunsNo');
                        }
                    }).fail(function (xhr) {
                        $('.error-box').text(xhr.message);
                        self.removeClass('bunsNo');
                    });
                }
            }
        }
    })
    /*输入框*/
    $('.checkCodeStatus').on('keyup change blur',function(){
        var checkStatus = true,error = $('.error-box');
        $.each($('.checkCodeStatus'),function(i,o){
            if($(o).val() == ''){
                $('.get-code-btn').removeClass('getCodeBtn');
                if(!$(o).hasClass('checkSEMCode')){
                    checkStatus = false;
                }
            }
            if($(o).hasClass('cardId')){
                var re = /^\d{11,20}$/;
                if (!re.test($(o).val().replace(/[ ]/g, ""))) {
                  $(o).val() == '' ?  error.text('请输入银行卡号') : error.text('输入的卡号有误');
                  checkStatus = false;
                }else{
                    error.text('');
                    var re = /^1\d{10}$/;
                    if (!re.test($('.mobileCode').val().replace(/[ ]/g, ""))) {
                      $('.mobileCode').val() == '' ?  error.text('请输入银行预留手机号') : error.text('输入的手机号有误');
                      checkStatus = false;
                    }else{
                      error.text('');
                    }
                }
            }
            if( checkStatus){
                $('.get-code-btn').addClass('getCodeBtn');
            }
        });
        $(this).attr('placeholder') == $('.error-box').text() ? $('.error-box').text('') : '';
    })


    /*短信验证码 */
    $('.codeParent').delegate('.getCodeBtn','click', function() {
      var count, element, intervalId, phoneNumber, timerFunction;
      element = $('.getCodeBtn');
      if ($(element).attr('disabled')) {
        return;
      }
      phoneNumber = $('.mobileCode').val();
      $.ajax({
        url: "/api/pay/deposit_new/",
        type: "POST",
        data: {
          card_no: $('.cardId').val(),
          phone: phoneNumber,
          amount: 0.01,
          gate_id: $('.select_bank').val(),
          device_id: ''
        }
      }).fail(function(xhr) {
        clearInterval(intervalId);
        $(element).text('重新获取').removeAttr('disabled').addClass('getCodeBtn');
        $('.error-box').text(xhr.message)
      }).success(function(xhr) {
        if (xhr.ret_code === 0) {
          element.attr('disabled', 'disabled').removeClass('getCodeBtn');
          $('#order_id').val(xhr.order_id);
          $('#token').val(xhr.token);
          intervalId;
          count = 60;
          $(element).attr('disabled', 'disabled');
          timerFunction = function() {
            if (count >= 1) {
              count--;
              return $(element).text('重新获取(' + count + ')');
            } else {
              clearInterval(intervalId);
              $(element).text('重新获取').removeAttr('disabled').addClass('getCodeBtn');
            }
          };
          timerFunction();
          return intervalId = setInterval(timerFunction, 1000);
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取').removeAttr('disabled').addClass('getCodeBtn');
          $('.error-box').text(xhr.message)
        }
      });
    });
});