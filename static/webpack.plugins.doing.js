/**
 * [{jade: 'jadesouth', script: ['script1','script2']}]
 * @param options
 * @constructor
 */
var fs = require("fs");


function FileListPlugin(options) {
    // Setup the plugin instance with options...
    //console.log(options)
    this.options = options
}
FileListPlugin.prototype.south = function(){

}

FileListPlugin.prototype.apply = function (compiler) {
    var _self = this;
    compiler.plugin('this-compilation', function (compilation) {
        fs.open("new.txt","w",function(err,fd){
            var buf = new Buffer("你好啊");
            fs.write(fd,buf,0,buf.length,0,function(err,written,buffer){});
        })
    });


};

module.exports = FileListPlugin;