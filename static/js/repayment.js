$(function() {
    $('#repayment-calculate').click(function(e) {
        var form = $('#repayment').serialize();
        $.ajax({
            type: 'post',
            url: '/api/repayment/',
            data: form,
            dataType: 'json'
        }).done(function(data) {
            if(data.errno == 1) {
                alert('不能提前还款，请检查还款计划');
                return;
            }
            for(var key in data) {
                if(key == 'errno') {
                    continue;
                }
                $('.repayment_'+key).html(data[key]);
            }
        });
    });

    $('#repayment-btn').click(function(e) {
        if(!confirm('操作将不能恢复，确认提前还款吗？')) {
            return;
        }
        var form = $('#repayment').serialize() + '&' + $('#repayment-form').serialize() + '&now=1';
        $.ajax({
            type: 'post',
            url: '/api/repayment/',
            data: form,
            dataType: 'json'
        }).done(function(data) {
            if(data.errno == 0) {
                alert(['提前还款成功，本金：', data.principal, '利息：', data.interest, '罚息：', data.penalinterest].join(''))
            } else {
                alert('不能提前还款，请检查还款计划');
            }
        });
    });
});
