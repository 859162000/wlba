import './mixins/ui'
import { slide, list } from './mixins/received_ui'
import { ajax, getQueryStringByName } from './mixins/api'




const renderList = (result) =>  {
    let slide = [];
    const
        $item = $('.receive-body'),
        $default =$('.received-default');

    if(result.data.length === 0){
        $item.html('');
        return $default.show();
    }
    for(let i =0; i< result.data.length; i++){
        slide.push(list(result.data[i]))
    }
    $default.hide();
    $item.html(slide.join(''))
    $('.received-loading-warp').hide()
}

const renderSlide = (result)=> {
    let slides = [], INDEX = null;

    for(let i =0; i< result.month_group.length; i++){
        if(result.current_month == result.month_group[i].term_date){
            INDEX = i;
        }
        slides.push(slide(result.month_group[i]))
    }

    swiper_m.appendSlide(slides);
    swiper_m.slideTo(INDEX, 150, false);
    renderList(result)
    $('.received-loding').hide()
}

const fetch = (data, callback) => {
    ajax({
        url: '/api/m/repayment_plan/month/',
        type: 'POST',
        data: data,
        success (data){
            callback && callback(data)
        }
    })
}


let swiper_m = null;
const render = () => {
    swiper_m = new Swiper('.swiper-container', {
        direction: 'horizontal',
        loop: false,
        slidesPerView: 1.21,
        centeredSlides: true,
        paginationClickable: true,
        spaceBetween: 30,
        onSlideChangeStart:function(swiper){
            const
                slide_index = swiper.activeIndex,
                target = $('.swiper-slide').eq(slide_index).find('.received-slide-date').text(),
                year = target.slice(0,4),
                month = target.slice(5,-1);
            $('.received-loading-warp').show()
            fetch({ year: year,  month: month}, renderList)
        }
    });

    fetch({ year: '',  month: ''}, renderSlide);
}

//doing
render();