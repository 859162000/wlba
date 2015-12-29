
var path = require('path');
var webpack = require('webpack');
var outpath = 'scripts/mobile_fuelcard/dev';

if(process.env.NODE_ENV == 'pro'){
    outpath = 'scripts/mobile_fuelcard/pro';
}

module.exports = {
    entry: {
        /**
         * 路径相对于webpack.fuel.js
         */
        buy: './src/mobile_fuelcard/buy',
        login: './src/mobile_fuelcard/login',
        regist: './src/mobile_fuelcard/regist',
        regist_authentication: './src/mobile_fuelcard/regist_authentication',
        regist_bank: './src/mobile_fuelcard/regist_bank',
        reset_password: './src/mobile_fuelcard/reset_password',
        recharge: './src/mobile_fuelcard/recharge',
        vendor: ['./src/mobile_fuelcard/lib/zepto']
    },
    output: {
        path: path.join(__dirname, outpath),
        publicPath: outpath + '/',
        filename: '[name].js'
    },
    module: {
        loaders: [
            { test: /\.js$/, exclude: /(node_modules)/, loader: 'babel', query: { presets: ['es2015'] }},
            { test: /zepto(\.min)?\.js$/, loader: "exports?Zepto; delete window.$; delete window.Zepto;" },
        ]
    },
    resolve: {
        modulesDirectories: ['./src/mobile_fuelcard'],
        alias: {
            zepto: 'lib/zepto.js'
        },
        extensions: ['', '.js']
    },
    plugins: [
        new webpack.ProvidePlugin({zepto: 'zepto', $: 'zepto'}),  //第三方库暴露到全局 不用import
        new webpack.optimize.CommonsChunkPlugin({   //第三方库生成的文件
            name: ['vendor'],
           filename: "vendor.zepto.js"
        }),
    ]
};
