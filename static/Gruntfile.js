module.exports = function( grunt ) {
    "use strict";
    grunt.initConfig({
        compass: {
            dist: {
                options: {
                    config: 'config_weixin.rb'
                }
            }
        }
    });

    grunt.registerTask('default', ['compass']);
    grunt.loadNpmTasks('grunt-contrib-compass');

};


