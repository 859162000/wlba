

export const slide = (data) => {
    let slide = "<div class='swiper-slide received-slide'>"
        slide += `<div class='received-slide-date'>${data.term_date.slice(0,4)}年${data.term_date.slice(5,7)}月</div>`;
        slide += "<div class='received-slide-data'>";
        slide += "<div class='received-data-list'>";
        slide += "<span class='received-left-center'>"
        slide += "<div class='data-name'>回款总额(元)</div>"
        if(data.total_sum == 0){
            slide += "<div class='data-value'>0.00</div>"
        }else{
            slide += `<div class='data-value'>${data.total_sum}</div>`
        }
        slide += "</span>"
        slide += "</div>"
        slide += "<div class='received-data-list'>";
        slide += "<span class='received-left-center'>"
        slide += "<div class='data-name'>回款笔数</div>"
        if(data.term_date_count == 0){
            slide += "<div class='data-value'>0</div>"
        }else{
            slide += `<div class='data-value'>${data.term_date_count}</div>`
        }
        slide += "</span>"
        slide += "</div>"
        slide += "</div>"
        slide += "</div>"

    return slide
}


export const list = (data) => {
    let list = `<a href='/weixin/received/detail/?productId=${data.product_id}' class='received-list'>`;
        list += "<div class='list-head-warp'>";
        list += "<div class='list-head arrow'>";
        list += "<div class='head-space'>&nbsp&nbsp</div>"
        list += `<span class='head-name'>${data.product_name}</span>`
        list += `<span class='head-process'>${data.term}/${data.term_total}</span>`
        list += "</div></div>";

        list += "<div class='list-cont'>";
        list += "<div class='list-flex'>";
        list += `<div class='cont-grey-2'>${data.term_date.slice(0,10)}</div>`;
        list += "<div class='cont-grey-1'>回款日期</div>";
        list += "</div>";
        list += "<div class='list-flex'>";
        list += `<div class='cont-red'>${data.principal}</div>`;
        list += "<div class='cont-grey-1'>本(元)</div>";
        list += "</div>";

        list += "<div class='list-flex'>";
        list += `<div class='cont-red'>${data.total_interest}</div>`;
        list += "<div class='cont-grey-1'>息(元)</div>";
        list += "</div>";

        list += "<div class='list-flex'>";
        list += `<div class='cont-grey-2'>${data.settlement_status}</div>`;
        if(data.settlement_status == '提前回款'){
            list += `<div class='cont-grey-1'>${data.settlement_time.slice(0,10)}</div>`;
        }
        list += "</div>";
        list += "</div>";
        list += "</div></a>";
    return list
}

export const detail = (data) => {
    let detail = "<div class='list-head-warp'>";
        detail += "<div class='list-head'>";
        detail += "<div class='head-space'>&nbsp&nbsp</div>";
        detail += `<span class='head-name head-allshow'>${data.equity_product_short_name}</span>`;
        detail += "</div></div>";

        detail += "<div class='list-nav'>";
        detail += "<ul><li class='item-date'>时间</li><li>本金(元)</li><li>利息(元)</li><li class='item-count'>总计(元)</li></ul>";
        detail += "</div>";
        detail += "<div class='detail-space-grep'></div>";

        for(var i=0; i< data.amortization_record.length;i++){

            detail += "<div class='detail-list'>";
            detail += `<div class='detail-item item-date'>${data.amortization_record[i].amortization_term_date.slice(0,10)}</div>`;
            detail += `<div class='detail-item'>${data.amortization_record[i].amortization_principal}</div>`;
            detail += `<div class='detail-item'>${data.amortization_record[i].amortization_amount_interest}`;
            if(data.amortization_record[i].amortization_coupon_interest > 0){
                detail += `<span>+</span><span class='blue-text'>${data.amortization_record[i].amortization_coupon_interest}</span><span class='blue-sign'>加息</span>`;
            }
            detail += "</div>";
            detail += `<div class= 'detail-item item-count'>${data.amortization_record[i].amortization_amount}</div>`;
            if(data.amortization_record[i].amortization_status== '提前回款' || data.amortization_record[i].amortization_status== '已回款'){
                detail += "<div class= 'repayment-icon'></div>";
            }
            detail += "</div>";
        }

    return detail;
};

