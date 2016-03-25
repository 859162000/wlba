define(['jquery','tools', 'csrf'], function ($, tool) {

    function Message(options) {
        this.target = options.target;
        //captcha_0， captcha_1短信验证码才有的参数
        this.captcha_0 = options.captcha_0;
        this.captcha_1 = options.captcha_1;
        this.phoneNumber= options.phoneNumber;
        this.startCallback = options.startCallback;
        this.doneCallback= options.doneCallback;
        this.failCallback = options.failCallback;
        this.timerEndCallback = options.timerEndCallback;

    }

    Message.prototype.setOptions = function(options){
        this.target = options.target || this.target;

        this.captcha_0 = options.captcha_0 || this.captcha_0;
        this.captcha_1 = options.captcha_1 || this.captcha_1;

        this.phoneNumber= options.phoneNumber || this.phoneNumber;
        this.doneCallback = options.doneCallback || this.doneCallback;
        this.failCallback = options.failCallback;
        this.timerEndCallback = options.timerEndCallback || this.timerEndCallback;
    }

    //语音验证码
    Message.prototype.voice_render = function () {
        var _self = this;
        //_self.target.attr('disabled', 'disabled').val('发送中..');

        $.post( "/api/ytx/send_voice_code/2/", {phone: _self.phoneNumber})
            .done(function (result) {
                if (result.ret_code === 0) {
                    _self.timerFunction('voice');
                    _self.doneCallback && _self.doneCallback(result);
                }else{
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: '系统繁忙'
                    });
                }
            })
            .fail(function (xhr) {
                var result = JSON.parse(xhr.responseText);
                _self.failCallback && _self.failCallback(result)
                if (xhr.status > 400) {
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: result.message
                    });
                }
            })
    };

    //短信验证码验证码
    Message.prototype.message_render = function () {
        var _self = this;
        _self.target.attr('disabled', 'disabled').val('发送中..');


        $.ajax({
            url: "/api/phone_validation_code/" + _self.phoneNumber + "/",
            type: "POST",
            data: {
                captcha_0: _self.captcha_0,
                captcha_1: _self.captcha_1
            }
        })
            .done(function (result) {
                _self.timerFunction('message');
                _self.doneCallback && _self.doneCallback(result)
            })
            .fail(function (xhr) {
                clearInterval(_self.intervalId);
                _self.target.val('重新获取').removeAttr('disabled');
                var result = JSON.parse(xhr.responseText);
                _self.failCallback && _self.failCallback(result)
                if (xhr.status >= 400) {
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: result.message
                    });
                }
            })
    };

    Message.prototype.timerFunction = function (type) {
        var _self = this, intervalId, count = 60;

        var timerInside = function () {
            if (count > 1) {
                count--;
                if(type == 'voice'){
                    return _self.target.html('<span class="fee">语音验证码已经发送，请注意接听（' + count + '）</span>');
                }
                return _self.target.val(count + '秒后可重发');
            } else {
                clearInterval(intervalId);
                if(type == 'voice') {
                    _self.target.html('没有收到验证码？请尝试<a href="javascript:void(0)" class="voice c-cash-blue">语音验证</a>').removeAttr('disabled');
                }else{
                    _self.target.val('重新获取').removeAttr('disabled');
                }
                return _self.timerEndCallback && _self.timerEndCallback()
            }
        };
        timerInside();
        intervalId = setInterval(timerInside, 1000);
        return this.intervalId = intervalId
    }
    return Message
});