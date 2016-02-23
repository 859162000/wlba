
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
        list: path.resolve(JS_PATH, 'list'),
        vendor: [path.resolve(JS_PATH, 'lib/zepto/zepto')]
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
        ]
    },
    resolve: {
        modulesDirectories: ['./src/mobile'],
        alias: {
            zepto: 'lib/zepto/zepto.js'
        },
        extensions: ['', '.js']
    },
    plugins: [
        new webpack.ProvidePlugin({zepto: 'zepto', $: 'zepto'}),  //第三方库暴露到全局 不用import
        new webpack.optimize.CommonsChunkPlugin({   //第三方库生成的文件
            name: ['vendor'],
           filename: "vendor.zepto.js"
        })
    ]
};
