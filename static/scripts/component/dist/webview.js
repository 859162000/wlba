var wlb=function(){function Mixin(a){this.bridge=a}function getMixin(a){return void 0===unique&&(unique=new Mixin(a)),unique}function ready(a){function b(){Mixin.isAPP()?window.WebViewJavascriptBridge?c({callback:"app",data:WebViewJavascriptBridge}):document.addEventListener("WebViewJavascriptBridgeReady",function(){c({callback:"app",data:WebViewJavascriptBridge})},!1):c({callback:"other",data:null})}function c(b){var c;b.callback&&"app"==b.callback&&(c=getMixin(b.data),c._init());try{a[b.callback](c)}catch(d){console.log("请传入正确的参数格式如{app: function(){}, other: function(){}}, 目前缺少 "+b.callback)}}b()}var unique;return Mixin.isAPP=function(){var a=navigator.userAgent;return a.indexOf("wlbAPP")>-1?!0:!1},Mixin.filterJSON=function(target){var u=navigator.userAgent,toString=Object.prototype.toString,newJSON=target;if(u.indexOf("Android")>-1&&"[object String]"==toString.call(newJSON))try{newJSON=eval("("+target+")")}catch(e){return newJSON}return newJSON},Mixin.prototype={_init:function(){this.bridge.init(function(a,b){var c={init:"true"};b(c)})},_setData:function(a,b){var c={post:{},callback:null},d=Object.prototype.toString;if("[object Object]"==d.call(a))for(var e in a)c.post[e]=a[e];return"[object Function]"==d.call(a)?(c.callback=a,c):(c.callback="[object Function]"==d.call(b)?b:null,c)},loginApp:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("loginApp",c.post,function(a){c.callback&&c.callback(a)})},registerApp:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("registerApp",c.post,function(a){c.callback&&c.callback(a)})},firstLoadWebView:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("firstLoadWebView",c.post,function(a){c.callback&&c.callback(a)})},jumpToManageMoney:function(a){this.bridge.callHandler("jumpToManageMoney",function(b){a&&a(b)})},jumpToDiscoverView:function(a){this.bridge.callHandler("jumpToDiscoverView",function(b){a&&a(b)})},authenticated:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("authenticated",c.post,function(a){var b=Mixin.filterJSON(a);c.callback&&c.callback(b)})},shareData:function(a){this.bridge.registerHandler("shareData",function(b,c){c(a)})},touchShare:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("touchShare",c.post,function(a){var b=Mixin.filterJSON(a);c.callback&&c.callback(b)})},shareStatus:function(a){this.bridge.registerHandler("shareStatus",function(b,c){var d=Mixin.filterJSON(b);a&&a(d)})},sendUserInfo:function(a,b){var c=this._setData(a,b);this.bridge.callHandler("sendUserInfo",{},function(a){var b=Mixin.filterJSON(a);c.callback&&c.callback(b)})}},{ready:ready}}();