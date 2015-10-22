


org.test = (function(org){
    var lib = {
        init:function(){
          /*var test = {"secretToken":"cd0d8da1be93f30e213a347886af3e73","ts":"1445409483.325864","ph":"15110253648","tk":"8331f0f403f0e82dd6695a90dc046885df92fc3f"}
            org.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data:{
                  token: test.tk,
                  secret_key: test.secretToken,
                  ts: test.ts
                },
                success: function(data){
                  console.log(data)
                }
            })*/
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
            })

            log('user-Agent', navigator.userAgent);

            bridge.callHandler('sendUserInfo', {'1': '1'}, function (response) {
              log('JS', response)
              $.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data:{
                  token: response.tk,
                  secret_key: response.secretToken,
                  ts: response.ts
                },
                success: function(data){
                  window.location.href = $("input[name='next']").val();
                },
                error: function(){
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
                 bridge.callHandler('loginApp', function (response) {
                    log('loginApp', response)
                 });
              });
            //注册
              $('#regist').on('click',function(){
                bridge.callHandler('registerApp', function (response) {
                    log('registerApp', response)
                 });
              });
            //投资
              $('#p2p').on('click',function(){
                bridge.callHandler('jumpToManageMoney', function (response) {
                    log('jumpToManageMoney', response)
                });
              });
            //分享
              bridge.registerHandler('shareData', function(data, responseCallback) {
                var responseData = { title:'呱呱卡test', content: '呱呱卡test' };
                responseCallback(responseData)
              })

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