/**
 * Created by HeZhang on 15-2-3.
 */
$(function() {
    var init = function() {
        var categories = [], user_name = [], amount = [];
        var getNum = function(num) {
            return num ? parseFloat(num) : 0;
        };
        for(var key in result) {
            categories.push(result[key].phone);
            user_name.push(result[key].user_name);
            amount.push(getNum(result[key].amount));
        }
        drawChart({categories: categories, user: user_name, amount: amount});
        initCondition();
    },
        drawChart = function(result) {
            $('#container').highcharts({
                title: {
                    text: '网利宝每日运营数据',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Source: wanglibao.com',
                    x: -20
                },
                xAxis: {
                    categories: result.categories,
                    labels: {
                        rotation: 45
                    }
                },
                yAxis: {
                    title: {
                        text: '量'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    valueSuffix: ''
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series: [{
                    name: '注册数',
                    data: result.joined
                }, {
                    name: '新增交易数',
                    data: result.trade
                }, {
                    name: '新增交易额',
                    data: result.amount
                }]
            });
        },
        initCondition = function() {
            $('.input-daterange').datepicker({
                format: 'yyyy-mm-dd'
            });
        };
    init();

});