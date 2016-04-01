/**
 * author wangxiaoqing
 * last update 2016-3-27
 */

var pubsub = {};

(function (q) {

    var topics = {},
        subUid = -1;
    q.publish = function (topic, args) {

        if (!topics[topic]) {
            return false;
        }

        setTimeout(function () {
            var subscribers = topics[topic],
                len = subscribers ? subscribers.length : 0;

            while (len--) {
                subscribers[len].func(topic, args);
            }
        }, 0);

        return true;

    };

    q.subscribe = function (topic, func) {

        if (!topics[topic]) {
            topics[topic] = [];
        }

        var token = (++subUid).toString();
        topics[topic].push({
            token: token,
            func: func
        });
        return token;
    };
}(pubsub));


var wlb = (function (pubsub) {

    var unique;

    function Mixin(bridge) {
        this.bridge = bridge;  //WebViewJavascriptBridge对象
    }

    Mixin.isAPP = function () {
        var u = navigator.userAgent;
        if (u.indexOf('wlbAPP') > -1) {
            return true
        }
        return false
    };

    Mixin.filterJSON = function (target) {
        var
            u = navigator.userAgent,
            toString = Object.prototype.toString,
            newJSON = target;

        if (u.indexOf('Android') > -1 && toString.call(newJSON) == '[object String]') {
            try {
                newJSON = eval("(" + target + ")");
            } catch (e) {
                return newJSON
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
         * 跳到发现页  app2.7.6版本
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
                var responseData = Mixin.filterJSON(response);
                options.callback && options.callback(responseData);
            });
        },
        /**
         * 获取分享信息 app2.7.6版本
         * @param data {title: 活动标题, content: 活动描述, shareUrl:'指定分享的url', image: ''}
         */
        shareData: function (data) {
            this.bridge.registerHandler('shareData', function (backdata, responseCallback) {
                responseCallback(data);
            });
        },
        /**
         * 调用分享按钮 app2.7.6版本
         * @function touchShare
         * @param data 自定义分享信息
         * @param callback 回调 {title: 活动标题, content: 活动描述, shareUrl:'指定分享的url', image: ''}
         */
        touchShare: function (data, callback) {
            var options = this._setData(data, callback);
            this.bridge.callHandler('touchShare', options.post, function (response) {
                var responseData = Mixin.filterJSON(response);
                options.callback && options.callback(responseData);
            });
        },
        shareStatus: function (callback) {
            this.bridge.registerHandler('shareStatus', function (backdata, responseCallback) {
                var responseData = Mixin.filterJSON(backdata);
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
                var responseData = Mixin.filterJSON(response);

                options.callback && options.callback(responseData);

            });
        }
    }

    function getMixin(bridge) {
        if (unique === undefined) {
            unique = new Mixin(bridge);
        }
        return unique;
    }

    function ready(dics) {
        /**
         * 处理webview初始化问题
         * Mixin为单例模式
         * 检查user-agent： 如果是app就保持侦听
         *
         */
        var debug  =  dics.debug ? (dics.debug.switch || false) : false;

        var socket;
        if (debug) websocket(listen);

        function listen() {
            if (Mixin.isAPP()) {
                if (window.WebViewJavascriptBridge) {
                    run({callback: 'app', data: WebViewJavascriptBridge});
                } else {
                    document.addEventListener('WebViewJavascriptBridgeReady', function () {
                        run({callback: 'app', data: WebViewJavascriptBridge})
                    }, false)
                }
            } else {
                run({callback: 'other', data: null})
            }
        }

        if (!debug) listen();

        function run(target) {
            var mixins;

            if (debug) pubsub.publish('log', {type: 'success', message: '当前执行环境为:' + target.callback});

            if (target.callback && target.callback == 'app') {
                mixins = getMixin(target.data);
                if (debug) Interception(mixins);
                mixins._init();
            }
            try {

                if (debug) pubsub.publish('log', {type: 'success', message: '执行回调:' + target.callback});
                dics[target.callback](mixins);

            } catch (e) {
                if (debug) pubsub.publish('log', {type: 'error', message: '异常:' + target.callback});
            }

        }

        function Interception(albert) {

            for (var property in  albert) {

                (function (property) {

                    var original = albert[property];
                    if (typeof original === 'function') {
                        albert[property] = function (data, callback) {
                            pubsub.publish('log', {type: 'success',  message: '开始动作:' + property + '\n接收参数:\ndata:' + data + "\ncallback:" + callback});
                            return original.call(albert, data, callback);
                        };
                    }

                })(property)
            }
        }

        function websocket(callback) {
            var host = dics.debug.host, link;

            host = host == '' ? 'localhost' : host;
            if(host == 'staging.wanglibao.com'){
                link = 'wss://' + host + ':3000'
            }else{
                link = 'ws://' + host + ':3000'
            }
            socket = new WebSocket(link);

            socket.onopen = function () {
                pubsub.subscribe('log', function (topics, result) {
                    socket.send(JSON.stringify({type: result.type, message: result.message}));
                });
                callback && callback()
            };
            socket.onmessage = function (ev) {
                var obj = JSON.parse(ev.data);
                alert(obj.message)
            }
        }
    }

    return {
        ready: ready
    }

})(pubsub);

//wlb.ready({
//
//    debug: {
//      switch: true  //debug开关
//      host: '',    //本地ip
//    },
//    app: function(mixins){
//        回调参数是app接口实例对象.
//        console.log('app场景')
//    },
//    other: function(){
//       console.log('其他场景的业务逻辑')
//    }
//})