/**
 *
 * 引入fuel_alert.jade
 * @param text 文字说明
 * @param callback 回调函数
 */
window.alert = function(text, callback){

    const $alert =$('.fuel-alert'), $button =$('.fuel-submit');

    $alert.css('display','-webkit-box').find('.fuel-text').text(text)

    $button.on('click', () => {
        $alert.hide();
        callback && callback()
    })
}

/**
 * 引入fuel_alert.jade
 * @param title confim文字说明
 * @param certainName 左边按钮文字
 * @param callback  回调函数
 * @param callbackData 回调函数的数据
 */
window.confirm = function(title, certainName = '确定', callback = null, callbackData = null){
    const $confirm = $('.confirm-warp')
    if($confirm.length <= 0 ) return
    $confirm.show();
    $confirm.find('.confirm-text').text(title);
    $confirm.find('.confirm-certain').text(certainName);

    $confirm.find('.confirm-cancel').on('click', () => {
        $confirm.hide();
    })

    $confirm.find('.confirm-certain').on('click', () => {
        $confirm.hide();
        if(callback){
            callbackData ? callback(callbackData): callback();
        }
    })
}


