(function(){
    var u = navigator.userAgent,
        ua = navigator.userAgent.toLowerCase(),
        isAndroid = u.indexOf('Android') > -1 || u.indexOf('Linux') > -1,
        isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);

    $('#js-down-btn').on('click', function () {
        if (ua.match(/MicroMessenger/i) == "micromessenger") {
            window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
        } else {
            if (isiOS) {
                window.location.href = 'https://appsto.re/cn/YS_H0.i';
            } else if (isAndroid) {
                window.location.href = 'http://wanglibao1.oss-cn-beijing.aliyuncs.com/apk/app-baidudsp-release.apk';
            } else {
                window.location.href = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.wljr.wanglibao&g_f=991653';
            }
        }
    });
})();
