import './mixins/ui'
import { list } from './mixins/received_ui'
import { ajax, getQueryStringByName } from './mixins/api'


(()=>{
    let page =  1, num =  10;

    $('.received-more').on('click', function(){
        fetch({ page: page, num: num });
    })

    const renderList = (result) => {
        let slide = [], $item = $('.received-item');

        for(let i =0; i< result.data.length; i++){
            slide.push(list(result.data[i]))
        }
        $item.append(slide.join(''))
    }

    const $more = $('.received-more');

    const fetch = (data) => {
        ajax({
            url: '/api/m/repayment_plan/all/',
            type: 'POST',
            data: data,
            beforeSend (){
                $more.attr('disabled',true).html('加载中，请稍后...')
            },
            success (data){
                if(data.count === 0 ){
                    $('.received-default').show()
                }
                data.count - data.page > 0 ?  $more.show():$more.hide();
                page = page + 1;
                renderList(data);
                $('.received-loding').hide()
            },
            complete (){
                $more.removeAttr('disabled').html('加载更多')
            }

        })
    }

    fetch({ page: page, num: num });
})()

