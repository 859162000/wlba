module.exports = function( grunt ) {
    "use strict";
    grunt.initConfig({
        compass: {
            dist: {
                options: {
                    //sassDir: 'm_sass',
                    //cssDir: 'stylesheets',
                    //environment: 'production'
                    config: 'config.rb'
                }
            }
        }
    });

    grunt.registerTask('default', ['compass']);
    grunt.loadNpmTasks('grunt-contrib-compass');

};

