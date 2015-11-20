var wlb = (function () {

    function Mixin (bridge) {
        this.bridge = bridge;
    }

    Mixin.prototype = {
        _init: function(){
            this.bridge.init(function (message, responseCallback) {
                var data = {'init': 'true'}
                responseCallback(data);
            });
        },
        _setData:function(ops,callback){
            var data = {'post': {}, 'callback': null};
            if(toString.call(ops) == '[object Object]'){
                for(var p in ops){
                    data.post[p] = ops[p];
                }
            }else if(toString.call(ops) == '[object Function]'){
                 data.callback = ops;
                return data
            }

            data.callback = toString.call(callback) == '[object Function]' ? callback : null;
            return data
        },
        loginApp: function(data, callback){

            var options = this._setData(data, callback);

            this.bridge.callHandler('loginApp', options.post, function (response) {
                options.callback && options.callback(response);
            });
        },
        registerApp: function(data, callback){

            var options = this._setData(data, callback);

            this.bridge.callHandler('registerApp', options.post, function (response) {
                options.callback && options.callback(response);
            });
        },
        firstLoadWebView: function(data, callback){

            var options = this._setData(data, callback);
            this.bridge.callHandler('firstLoadWebView', options.post,function (response) {
                options.callback && options.callback(response);
            });
        },
        jumpToManageMoney: function(callback){
            this.bridge.callHandler('jumpToManageMoney', function (response) {
                callback && callback(response)
            });
        },
        authenticated : function(data, callback){
            var options = this._setData(data, callback);
            this.bridge.callHandler('authenticated', options.post, function(response) {
                options.callback && options.callback(response);
            });
        },
        shareData: function(data){
            this.bridge.registerHandler('shareData', function(data, responseCallback) {
                responseCallback(data);
            });
        },
        sendUserInfo: function(data, callback){
            var options = this._setData(data, callback);

            this.bridge.callHandler('sendUserInfo', options.post, function (response) {
                options.callback && options.callback(response);
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
            var mixins ;
            if(target.callback && target.callback == 'app'){
                mixins = new Mixin(target.data);
                mixins._init();
            }
            try{
                dics[target.callback](mixins);
            }catch(e){
                console.log('传参类型{app: function(){}, other: function(){}}')
            }

        }
    }

    return {
        ready: ready
    }

})();



/*wlb.ready({
    app: function(mixins){
        
    },
    other: function(){

    }
})*/

