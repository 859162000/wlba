var path = require('path');
var webpack = require('webpack');
//var commonsPlugin = new webpack.optimize.CommonsChunkPlugin('common.js');
var deps = [
    'react/dist/react.min.js',
];


module.exports = {
    cache: true,
    entry: {
        home: './test/index.js',
        vendor: ['./test/lib/jquery.js']
    },
    output: {
        path: path.join(__dirname, 'testDist'),
        publicPath: 'testDist/',
        filename: '[name].js',
        chunkFilename: '[chunkhash].js'
    },
    module: {
        loaders: [
            {test: path.resolve('./lib/animateNumber.min'), loader: 'expose?animate'},
        ]
    },
    resolve: {
        alias: {
            jquery: './lib/jquery',
        },
        extensions: ['', '.js', '.json']
    },
    plugins: [
        new webpack.ProvidePlugin({Zepto: 'jquery', $: 'jquery'}),
/*new webpack.optimize.CommonsChunkPlugin({
 name: ['vendor'],
 filename: "vendor.bundle.js"
 }),
 ]
 };
