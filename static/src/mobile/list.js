import { ajax } from './mixins/api'
import { signModel } from './mixins/ui'


(()=> {
    const
        windowHeight = $(window).height(),
        $swiperSlide = $('.swiper-slide');

    let
        canGetPage = true, //防止多次请求
        FETCH_PAGE_SIZE = 10, //每次请求的个数
        FETCH_PAGE = 2,
        AUTOPLAY_TIME = 5000, //焦点图切换时间
        LOOP = true;


    ~function banner() {
        if ($swiperSlide.length / 2 < 1) {
            AUTOPLAY_TIME = 0;
            LOOP = false;
        }
        var myswiper = new Swiper('.swiper-container', {
            pagination: '.swiper-pagination',
            loop: LOOP,
            lazyLoading: true,
            autoplay: AUTOPLAY_TIME,
            autoplayDisableOnInteraction: true,
        });
    }();

    const fetch_data = ()=> {
        ajax({
            type: 'GET',
            url: '/api/p2ps/wx/',
            data: {
                page: FETCH_PAGE,
                pagesize: FETCH_PAGE_SIZE
            },
            beforeSend () {
                canGetPage = false;
                $('.load-text').html('加载中...');
            },
            success (data) {
                $('#list-body').append(data.html_data);
                FETCH_PAGE++;
                canGetPage = true;
            },
            error () {
                alert('Ajax error!')
            },
            complete () {
                $('.load-text').html('点击查看更多项目');
            }
        })
    }
    $('.load-body').on('click', () => {
        canGetPage && fetch_data();
    })

})()