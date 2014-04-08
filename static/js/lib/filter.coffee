define ["underscore"], (_)->
  arrayToFilter = (names, field, defaultName='不限')->
    filters = _.map names, (val, index)->
      {
        name: val
        values:
          _.object([[field, val]])
      }
    [{
      name: defaultName
    }].concat filters

  arrayToFilter: arrayToFilter