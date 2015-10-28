


org.test = (function(org){
    var lib = {
        init:function(){
          lib.webview();
        },
        webview: function(){
          function connectWebViewJavascriptBridge(callback) {
            if (window.WebViewJavascriptBridge) {
              callback(WebViewJavascriptBridge)
            } else {
              document.addEventListener('WebViewJavascriptBridgeReady', function() {
                callback(WebViewJavascriptBridge)
              }, false)
            }
          }

          connectWebViewJavascriptBridge(function(bridge) {
            var uniqueId = 1
            function log(message, data) {
              var log = document.getElementById('log')
              var el = document.createElement('div')
              el.className = 'logLine'
              el.innerHTML = uniqueId++ + '. ' + message + ':<br/>' + JSON.stringify(data)
              if (log.children.length) { log.insertBefore(el, log.children[0]) }
              else { log.appendChild(el) }
            }

            bridge.init(function(message, responseCallback) {
              log('JS got a message', message)
              var data = { 'Javascript Responds':'收到' }
              log('JS responding with', data)
              $('#log1').html('初始化了');
              responseCallback(data);
            });
            $('#log2').html('进到webview了');

            bridge.callHandler('sendUserInfo', {'1': '1'}, function (response) {
              var responsejson = typeof response == 'string' ? JSON.parse(response): response;

              $('#log1').html(JSON.stringify(responsejson));
              org.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data:{
                  token: responsejson.tk,
                  secret_key: responsejson.secretToken,
                  ts: responsejson.ts
                },
                success: function(data){
                  $('#log2').html(JSON.stringify(data));
                  window.location.href = $("input[name='next']").val();
                },
                error: function(data){
                  $('#log3').html(JSON.stringify(data));
                  window.location.href = $("input[name='next']").val() + "nologin/";
                }
              })
            });
          })
        }

    }
    return {
        init : lib.init
    }
})(org);


org.scratch = (function(org){
    var lib = {
        init:function(){
          lib.webview();
        },
        webview: function(){

          function connectWebViewJavascriptBridge(callback) {
            if (window.WebViewJavascriptBridge) {
              callback(WebViewJavascriptBridge)
            } else {
              document.addEventListener('WebViewJavascriptBridgeReady', function() {
                callback(WebViewJavascriptBridge)
              }, false)
            }
          }

          connectWebViewJavascriptBridge(function(bridge) {
            var uniqueId = 1
            function log(message, data) {
              var log = document.getElementById('log')
              var el = document.createElement('div')
              el.className = 'logLine'
              el.innerHTML = uniqueId++ + '. ' + message + ':<br/>' + JSON.stringify(data)
              if (log.children.length) { log.insertBefore(el, log.children[0]) }
              else { log.appendChild(el) }
            }

            bridge.init(function(message, responseCallback) {
              log('JS got a message', message)
              var data = { 'Javascript Responds':'收到' }
              log('JS responding with', data)
              responseCallback(data)
            });

            //登陆
              $('#login').on('click',function(){
                 bridge.callHandler('loginApp',{refresh: 1, url: ''}, function (response) {
                   $('.test-log').html(JSON.stringify(response))
                 });
              });
             //url
            $('#url').html(window.location.href)
            //注册
              $('#regist').on('click',function(){
                bridge.callHandler('registerApp', {refresh: 1, url: ''}, function (response) {
                   $('.test-log').html(JSON.stringify(response));
                 });
              });

            //投资
              $('#p2p').on('click',function(){
                bridge.callHandler('jumpToManageMoney', function (response) {
                    log('jumpToManageMoney', response);
                });
              });
            //埋点
              bridge.callHandler('firstLoadWebView', {name: 'test firstLoadWebView'},function (response) {
                    log('firstLoadWebView', response);
              });
            //分享
              bridge.registerHandler('shareData', function(data, responseCallback) {
                  var responseData = { title:'呱呱卡test', content: '呱呱卡test' };
                  responseCallback(responseData);
              });

              //判断client 是否登录，  并且在该方法传递数据埋点
              bridge.registerHandler('authenticated', function(data, responseCallback) {
                $('.test-log').html(JSON.stringify(data))
                var activity = {name: 'guaguaka'}
                responseCallback(activity)

              });
          })
        }

    }
    return {
        init : lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);