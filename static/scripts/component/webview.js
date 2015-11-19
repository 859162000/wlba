var wlb = (function () {

    function Mixin (bridge) {
        this.bridge = bridge;
    }

    Mixin.prototype = {
        init: function(){
            this.bridge.init(function (message, responseCallback) {
                var data = {'init': 'true'}
                responseCallback(data);
            });
        },
        loginApp: function(data, callback){
            this.bridge.callHandler('registerApp', {'12':12}, function (response) {

            });
            var ops = {
                refresh: data.refresh || 1,
                url: data.url || ''
            };

            this.bridge.callHandler('registerApp', {'1': 12}, function (response) {

               /* if(toString.call(data) == '[object function]'){
                    data.callback(response)
                }else{
                    callback && callback(response);
                }*/
            });
        },
        test: function(){
            document.getElementById('log').innerHTML ='test'
        }
    }



    function ready(dics){

        if (window.WebViewJavascriptBridge) {
            run({callback: 'app', data: WebViewJavascriptBridge })

        } else {
            document.addEventListener('WebViewJavascriptBridgeReady', function () {
                run({callback: 'app', data: WebViewJavascriptBridge })
            }, false)

            run({callback: 'other', data: null })
        }

        function run(target){
            var mixins ;
            if(target.callback && target.callback == 'app'){
                mixins = new Mixin(target.data);
                mixins.init();

            }
            dics[target.callback](mixins);
        }
    }

    return {
        ready: ready
    }

})();

wlb.ready({
    app: function(mixins){

        document.getElementById('buttons').onclick = function(){
            mixins.loginApp();
        }

    },
    other: function(mixins){
        var ops = {
                refresh: data.refresh || 1,
                url: data.url || ''
            };
         document.getElementById('buttons').onclick = function(){
            window.location.href= '/weixin/login/'
        }
    },
})

