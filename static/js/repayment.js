$(function() {
    $('#repayment-calculate').click(function(e) {
        console.log('hello');
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
    console.log('hello');
});
