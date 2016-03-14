
const _setShareData =  (ops, suFn, canFn) => {
    let setData = {};
    if (typeof ops == 'object') {
        for (var p in ops) {
            setData[p] = ops[p];
        }
    }
    typeof suFn == 'function' && suFn != 'undefined' ? setData.success = suFn : '';
    typeof canFn == 'function' && canFn != 'undefined' ? setData.cancel = canFn : '';
    return setData
}
/**
 * 分享到微信朋友
 */
export const onMenuShareAppMessage = (ops, suFn, canFn) => {
    wx.onMenuShareAppMessage(_setShareData(ops, suFn, canFn));
}
/**
 * 分享到微信朋友圈
 */
export const onMenuShareTimeline = (ops, suFn, canFn) => {
    wx.onMenuShareTimeline(_setShareData(ops, suFn, canFn));
}

export const onMenuShareQQ = () => {
    wx.onMenuShareQQ(_setShareData(ops, suFn, canFn));
}