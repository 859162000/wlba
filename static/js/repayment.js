$(function() {
    $('#repayment-calculate').click(function(e) {
        var form = $('#repayment').serialize();
        $.ajax({
            type: 'post',
            url: '/api/repayment/',
            data: form,
            dataType: 'json'
        }).done(function(data) {
            console.log('data', data, arguments);
            for(var key in data) {
                $('.repayment_'+key).html(data[key]);
                console.log(key)
            }
        });
    });

    $('#repayment-btn').click(function(e) {
        var form = $('#repayment').serialize();
        $.ajax({
            type: 'post',
            url: '/api/repayment/',
            data: form,
            dataType: 'json'
        }).done(function(data) {
            console.log('data', data, arguments);
            for(var key in data) {
                $('.repayment_'+key).html(data[key]);
                console.log(key)
            }
        });
    });
});
