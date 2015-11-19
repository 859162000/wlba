var wlb = (function () {

    function Mixin (bridge) {
        this.bridge = bridge;
    }
    Mixin.checkArguments = function(target){
        return toString.call(target)
    }

    Mixin.prototype = {
        init: function(){
            this.bridge.init(function (message, responseCallback) {
                var data = {'init': 'true'}
                responseCallback(data);
            });
        },
        loginApp: function(data, callback){

            var ops = {
                refresh: data.refresh || 1,
                url: data.url || ''
            };

            this.bridge.callHandler('loginApp', ops, function (response) {
                if(Mixin.checkArguments(data) == '[object function]'){
                    data.callback(response)
                }else{
                    callback && callback(response);
                }
            });
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
            if(target.callback && target.callback == 'app'){
                var mixins = new Mixin(target.data).init();
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
         document.getElementById('buttons').onclick = function(){
            window.location.href= '/weixin/login/'
        }
    },
})
