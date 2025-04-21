
module.exports = function override(config, env) {
    
    config.plugins = config.plugins.filter(
      plugin => plugin.constructor.name !== 'ReactRefreshPlugin'
    );
  
    
    const oneOfRule = config.module.rules.find(rule => Array.isArray(rule.oneOf));
    if (oneOfRule) {
      oneOfRule.oneOf.forEach(rule => {
        if (rule.loader && rule.loader.includes('babel-loader') && rule.options && Array.isArray(rule.options.plugins)) {
          rule.options.plugins = rule.options.plugins.filter(
            plugin => {
              if (typeof plugin === 'string') {
                return !plugin.includes('react-refresh');
              }
              if (Array.isArray(plugin) && typeof plugin[0] === 'string') {
                return !plugin[0].includes('react-refresh');
              }
              return true;
            }
          );
        }
      });
    }
  
    return config;
  };