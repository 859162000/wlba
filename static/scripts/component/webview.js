// author wangxiaoqing
// last update 2015-11-20
var wlb = (function () {

    function Mixin(bridge) {
        this.bridge = bridge;  //WebViewJavascriptBridge对象
    }

    Mixin.filterJSON = function(target){
        var
            u = navigator.userAgent,
            newJSON = target;

        if(u.indexOf('Android')){
            try{
                newJSON = eval("(" + target + ")");
            }catch(e){

            }

        }

        return newJSON;
    }

    Mixin.prototype = {
        _init: function () {
            this.bridge.init(function (message, responseCallback) {
                var data = {'init': 'true'}
                responseCallback(data);
            });
        },
        _setData: function (ops, callback) {
            var data = {'post': {}, 'callback': null};
            var toString = Object.prototype.toString;

            if (toString.call(ops) == '[object Object]') {
                for (var p in ops) {
                    data.post[p] = ops[p];
                }
            }

            if (toString.call(ops) == '[object Function]') {
                data.callback = ops;
                return data
            }

            data.callback = toString.call(callback) == '[object Function]' ? callback : null;
            return data
        },
        /**
         * 登陆
         * @param data  {refresh: 1||0, url: url||''}
         * @param callback
         */
        loginApp: function (data, callback) {

            var options = this._setData(data, callback);

            this.bridge.callHandler('loginApp', options.post, function (response) {
                options.callback && options.callback(response);
            });
        },
        /**
         * 注册
         * @param data {refresh: 1||0, url: url||''}
         * @param callback
         */
        registerApp: function (data, callback) {

            var options = this._setData(data, callback);

            this.bridge.callHandler('registerApp', options.post, function (response) {
                options.callback && options.callback(response);
            });
        },
        /**
         * 数据埋点
         * @param data {name: 活动名称||''}
         * @param callback
         */
        firstLoadWebView: function (data, callback) {

            var options = this._setData(data, callback);
            this.bridge.callHandler('firstLoadWebView', options.post, function (response) {
                options.callback && options.callback(response);
            });
        },
        /**
         * 跳到理财专区
         * @param callback
         */
        jumpToManageMoney: function (callback) {
            this.bridge.callHandler('jumpToManageMoney', function (response) {
                callback && callback(response)
            });
        },
        /**
         * 跳到发现页
         * @param callback
         */
        jumpToDiscoverView: function (callback) {
            this.bridge.callHandler('jumpToDiscoverView', function (response) {
                callback && callback(response)
            });
        },
        /**
         * 判断是否登陆
         * 目前该接口有问题，暂不使用，用senduserinfo先替代
         * @param data  可不传
         * @param callback 返回 [login, ph, tk]
         */
        authenticated: function (data, callback) {
            var options = this._setData(data, callback);
            this.bridge.callHandler('authenticated', options.post, function (response) {
                var responseData  = Mixin.filterJSON(response);
                options.callback && options.callback(responseData);
            });
        },
        /**
         * 获取分享信息
         * @param data {title: 活动标题, content: 活动描述, shareUrl:'指定分享的url'}
         */
        shareData: function (data) {
            this.bridge.registerHandler('shareData', function (backdata, responseCallback) {
                responseCallback(data);
            });
        },
        /**
         * 调用分享按钮
         * @function touchShare
         * @param data 自定义分享信息
         * @param callback 回调
         */
        touchShare: function(data, callback){
            var options = this._setData(data, callback);
            this.bridge.callHandler('touchShare', options.post, function (response) {
                var responseData  = Mixin.filterJSON(response);
                options.callback && options.callback(responseData);
            });
        },
        /**
         * 注册登录取消
         * @param data {title: 活动标题, content: 活动描述, shareUrl:'指定分享的url'}
         */
        cancel: function (data, callback) {
            this.bridge.registerHandler('cancel', function (backdata, responseCallback) {
                responseCallback(data);
                var responseData  = Mixin.filterJSON(backdata);
                callback && callback(responseData)
            });
        },
        /**
         * 获取用户信息
         * @param data 可不传
         * @param callback 返回[secretToken, ts, ph, tk]
         */
        sendUserInfo: function (data, callback) {
            var options = this._setData(data, callback);

            this.bridge.callHandler('sendUserInfo', {}, function (response) {

                var responseData  = Mixin.filterJSON(response);
                options.callback && options.callback(responseData);
            });
        }
    }


    function ready(dics) {
        /**
         * 临时处理webview初始化问题
         */
        window.onload = function(){
            setTimeout(function(){
                listen();
            },200);
        }

        function listen(){
            if (window.WebViewJavascriptBridge) {
                run({callback: 'app', data: WebViewJavascriptBridge});
            } else {
                document.addEventListener('WebViewJavascriptBridgeReady', function () {
                    run({callback: 'app', data: WebViewJavascriptBridge})
                }, false)
                run({callback: 'other', data: null})
            }
        }


        function run(target) {
            var mixins;
            if (target.callback && target.callback == 'app') {
                mixins = new Mixin(target.data);
                mixins._init();
            }

            try {
                dics[target.callback](mixins);
            } catch (e) {
                console.log('请传入正确的参数格式如{app: function(){}, other: function(){}}, 目前却少 ' + target.callback);
            }

        }
    }

    return {
        ready: ready
    }

})();

 //wlb.ready({
 //    app: function(mixins){
 //        //mixins.loginApp()
 //        ///document.getElementById('refresh').onclick= function(){
 //        //    window.location.href=window.location.href;
 //        //}
 //       mixins.sendUserInfo(function(data){
 //           document.getElementById('log').innerHTML = JSON.stringify(data)
 //       })
 //    },
 //    other: function(){
 //       console.log('其他场景的业务逻辑')
 //    }
 //})





