
var path = require('path');
var webpack = require('webpack');

var ROOT_PATH = path.resolve(__dirname);
var JS_PATH = path.resolve(ROOT_PATH, "src/mobile");
var BUILD_PATH = path.resolve(ROOT_PATH, "scripts/mobile/dev");


if(process.env.NODE_ENV == 'pro'){
    BUILD_PATH = 'scripts/mobile/pro';
}


module.exports = {
    entry: {
        login: path.resolve(JS_PATH, 'login'),
        regist: path.resolve(JS_PATH, 'regist'),
        list: path.resolve(JS_PATH, 'list'),
        detail: path.resolve(JS_PATH, 'detail'),
        buy: path.resolve(JS_PATH, 'buy'),
        calculator: path.resolve(JS_PATH, 'calculator'),
        bankOneCard: path.resolve(JS_PATH, 'bankOneCard'),
        recharge: path.resolve(JS_PATH, 'recharge'),
        trade_retrieve: path.resolve(JS_PATH, 'trade_retrieve'),
        received_all: path.resolve(JS_PATH, 'received_all'),
        received_detail: path.resolve(JS_PATH, 'received_detail'),
        received_month: path.resolve(JS_PATH, 'received_month'),
        process_authentication: path.resolve(JS_PATH, 'process_authentication'),
        process_addbank: path.resolve(JS_PATH, 'process_addbank'),

        vendor: [path.resolve(JS_PATH, 'lib/zepto/zepto'),path.resolve(JS_PATH, 'lib/polyfill.min')]
    },
    output: {
        path: BUILD_PATH,
        publicPath: '/',
        filename: '[name].js'
    },
    module: {
        loaders: [
            { test: /\.js$/, exclude: /(node_modules)/, loader: 'babel', query: { presets: ['es2015'] }},
            { test: /zepto(\.min)?\.js$/, loader: "exports?Zepto; delete window.$; delete window.Zepto;" },
            { test: /wx(\.min)?\.js$/, loader: "exports?wx" },
        ]
    },
    resolve: {
        modulesDirectories: ['./src/mobile'],
        alias: {
            zepto: 'lib/zepto/zepto.js',
            wx: 'lib/weixin/wx.js'
        },
        extensions: ['', '.js']
    },
    plugins: [
        new webpack.ProvidePlugin({zepto: 'zepto', $: 'zepto'}),  //第三方库暴露到全局 不用import
        new webpack.optimize.CommonsChunkPlugin({
            name: ['vendor'],
           filename: "vendor.zepto.js"
        })

    ]
};
