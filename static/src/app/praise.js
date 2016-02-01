
wlb.ready({
    app: function (mixins) {
        $('.client-praise-submit').on('touchend', function(){
            $('.praise-mask-warp').show()
        })
        $('.praise-mask-warp').on('touchend', function(){
            $(this).hide()
        })
        mixins.shareData({title: '冲刺8000年终奖，集赞越多，奖金越高！', content: '分享集赞可领年终奖，集一个赞，可领500！'})

    },
    other: function () {
        console.log('请在微信用打开')
    }
})

