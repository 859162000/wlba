
require(['jquery', 'echarts', 'tools', './model/pager', './model/date', 'csrf'], function ($, echarts, tools, pager) {





    var $startDate = $('#start-date'), $endDate = $('#end-date');

    var startPicker= $startDate.pickadate({
        hiddenPrefix: 'start'
    })
    var start_picker__value = startPicker.pickadate( 'picker' )

    var endPicker =  $endDate.pickadate({
        hiddenPrefix: 'end'
    })
    var end_picker__value = endPicker.pickadate( 'picker' )

    var pagerListen = function(page){
        var filterData = {
            start_submit: start_picker__value.get(),
            end_submit: end_picker__value.get(),
            page: page,
        }

        filterDate(filterData)
    };

    var filterDate = function(data){
        $.post('/api/uc/repayment_plan/',
            {
                start_submit: data.start_submit,
                end_submit: data.end_submit,
                page: data.page,
                pagesize: 10
            })
            .done(function(result){
                if(result.html_data == ''){
                    $('.center-from-home').html("<div class='tc'>null data</div>")
                }else{
                    $('.center-from-home').html(result.html_data);

                    pager({
                        page: result.page,
                        pagenumber: result.pagenumber,
                        callback: pagerListen
                    })
                }

            })
            .fail(function(){

            })
    }


    $('.filter-submit').on('click', function(){
        filterDate({
            start_submit: start_picker__value.get('value'),
            end_submit: end_picker__value.get('value'),
            page: 1
        })
    });

    $('.filter-submit').trigger('click');

    var type = echarts.init(document.getElementById('type'));
    var limit = echarts.init(document.getElementById('limit'));
    var earning = echarts.init(document.getElementById('earning'));


    var a = 1
    option = {
        title: {
            text: '项目类型',
            top: 160,
            left: 40,
            textStyle: {
                fontSize: 14,
                color: '#666',
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{b}{c}个",
            padding: [5, 20]
        },
        legend: {
            itemGap: 5,
            itemWidth: 10,
            top: 185,
            left: 40,
            icon: 'circle',
            orient: 'vertical',
            data:["散标投资",'月利宝','债权转让'],
            formatter: function(name){
                a++;
                return a + name
            },
            textStyle: {
             color: '#b2b2b2'
            },

        },
        series: [
            {
                type:'pie',
                radius: ['50%%', '80%'],
                center: ['50%', '30%'],
                hoverAnimation: true,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },

                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {
                        value:35,
                        name:'散标投资',
                        itemStyle: {
                            normal: {
                                color: '#f2b98b'
                            }

                        }
                    },
                    {
                        value:310,
                        name:'月利宝',
                        itemStyle: {
                            normal: {
                                color: '#a0c2f2'
                            }

                        }
                    },
                    {
                        value:310,
                        name:'债权转让',
                        itemStyle: {
                            normal: {
                                color: '#c9d8a0',
                            }
                        }
                    }
                ],

            }
        ]
    };

    type.setOption(option);
    limit.setOption(option);
    earning.setOption(option);

});