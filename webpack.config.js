const path = require('path')
const webpack = require("webpack");
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const staticPath ='./bauble/static'

module.exports = {
    entry: {
        app_js: [staticPath + "/app.js"],
        styles: [staticPath + "/styles/main.scss"],
    },
    output: {
        path: './bauble/static/dist',
        filename: "bundle.[chunkhash].js",
    },
    module: {
        loaders: [{
            test: /\.js$/,
            exclude: /(node_modules|bower_components)/,
            loaders: ['uglify', 'babel-loader', 'ng-annotate']
        },{
            test: /\.scss$/,
            loader: ExtractTextPlugin.extract('css!sass')
        }]
    },
    sassLoader: {
        includePaths: [path.resolve('./node_modules/bootstrap-sass/assets/stylesheets')]
    },
    plugins:[
        new ExtractTextPlugin('[name].[chunkhash].css'),
    ]
};
