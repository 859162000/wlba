import './mixins/ui'
import { detail } from './mixins/received_ui'
import { ajax, getQueryStringByName } from './mixins/api'

(()=>{
    const renderDetail = (result) => {
        let slide = [],
            $item = $('.received-list');
        slide.push(detail(result));
        $item.append(slide.join(''))
        $('.received-loding').hide()
    }

    const fetch = (product_id) => {
        ajax({
            url: `/api/home/p2p/amortization/${product_id}`,
            type: 'get',
            success (result){
                renderDetail(result);
            }
        })
    }

    const render = () => {
        const product_id  = getQueryStringByName('productId')
        fetch(product_id);
    }

    render()
})()
