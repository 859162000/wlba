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
        var userName = $('#userName');
        var nameId = $('#nameId');
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
    /*充值*/
    $('#recharge').on('click',function(){
        var amount = $('#amount');
        var cardSelect = $('#card-select');
        if($.trim(amount.val()) == ''){
            amount.next().html('<i></i>请输入充值金额');
            return false;
        }else{
            if($.trim(amount.val()) >= 0.01){
                amount.next().html('');
            }else{
                amount.next().html('<i></i>充值金额不正确');
                amount.val('');
                return false;
            }
        }
        if(cardSelect.val() == ''){
            cardSelect.next().html('<i></i>请选择银行');
            return false;
        }
        $('#rechargeAlert').modal();
    })
    /*下拉框*/
    $('#card-select').focus(function(){
        $('#card-select').addClass('selected');
    })
    $('#card-select').blur(function(){
        if($(this).val() == ''){
            $('#card-select').removeClass('selected');
        }
    })
});