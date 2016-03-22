(function () {

    require(['jquery', 'tools', 'jquery.zclip'], function ($, tool) {
        var token = $('input[name=promotiontoken]').val()
        var _share_title = encodeURI('“邀请好友送话费”活动');
        var _share_content = encodeURI("来网利宝投资，让钱生钱！现在受邀注册理财即可获得28888元体验金及最高300元现金红包，APP投资分享还送加息券。IDG资本、百亿A股上市公司超4000万美金投资平台，100%本息保障，100元起投资，立即去看看～ 戳这里>>https://www.wanglibao.com/?promo_token="+token+"");
        var _share_url = encodeURIComponent("https://www.wanglibao.com/?promo_token="+token+"");
        var _share_pic = 'https://staging.wanglibao.com/static/images/share_pic.jpg';
        $(document).ready(function () {
            $(".wlb_tsina").click(function () {
                window.open("http://v.t.sina.com.cn/share/share.php?url=&title=" + _share_content);
            });
            $(".wlb_kaixin001").click(function () {
                window.open("http://www.kaixin001.com/repaste/share.php?rurl=&rcontent=" + _share_content);
            });
            $(".wlb_douban").click(function () {
                window.open("http://www.douban.com/recommend/?url=" + _share_url + "&title=" + _share_content);
            });
            $(".wlb_renren").click(function () {
                window.open("http://widget.renren.com/dialog/share?resourceUrl=" + _share_url + "&title=" + _share_title + "&pic=" + _share_pic + "&description=" + _share_content);
            });
            $(".wlb_qzone").click(function () {
                window.open("http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=" + _share_url + "&title=" + _share_title + "&pics=" + _share_pic + "&desc=" + _share_content);
            });
            if (navigator.plugins) {
                var isFlashPlugin = 0;
                $.each(navigator.plugins, function (x, y) {
                    if (navigator.plugins[x].name == "Shockwave Flash") {
                        isFlashPlugin = 1;
                    }
                });
                if (isFlashPlugin == 1) {
                    $(".inviteCopyButton[data-target='invite-textarea']").zclip({
                        path: "/static/images/ZeroClipboard.swf",
                        copy: $.trim($('.invite-textarea').text()),
                        afterCopy: function () {
                            return tool.modalAlert({
                                title: '温馨提示',
                                msg: '复制成功！\</br>你可以粘贴到QQ或论坛中发送给好友'
                            });
                        }
                    });
                    $(".inviteCopyButton[data-target='invite-input']").zclip({
                        path: "/static/images/ZeroClipboard.swf",
                        copy: $.trim($('.invite-input').text()),
                        afterCopy: function () {
                            return tool.modalAlert({
                                title: '温馨提示',
                                msg: '复制成功！\</br>你可以粘贴到QQ或论坛中发送给好友'
                            });
                        }
                    });
                } else {
                    $(".inviteCopyButton").click(function () {
                        return tool.modalAlert({
                            title: '温馨提示',
                            msg: '你的浏览器不支持直接复制。！\</br>请选中文案后点击鼠标右键复制。'
                        });
                    });
                }
            }
        });


    });

}).call(this);