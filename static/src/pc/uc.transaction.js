
require(['jquery', './model/date'], function ($, initDate) {

    var
        $startDate = $('#start-date'),
        $endDate = $('#end-date'),
        initStartDate = $('input[name=startDate]').val() || '',
        initEndDate = $('input[name=endDate]').val() || '';

    initDate.definedDate($startDate, $endDate, initStartDate, initEndDate)
    var start_picker__value= $startDate.pickadate({
        hiddenPrefix: 'start'
    }).pickadate( 'picker' )


    var end_picker__value =  $endDate.pickadate({
        hiddenPrefix: 'end'
    }).pickadate( 'picker' )

    var status = $('input[name=p2p_status]').val()|| 'all';

    var startDate,endDate;
    $('.filter-submit').on('click', function(){
        startDate = start_picker__value.get();
        endDate = end_picker__value.get();
        window.location.href= "/accounts/transaction/?p2p_status="+status+"&start_date="+startDate+"&end_date="+endDate;
    })



});