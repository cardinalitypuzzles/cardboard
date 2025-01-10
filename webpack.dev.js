const { merge } = require("webpack-merge");
const common = require("./webpack.common.js");

module.exports = merge(common, {
  mode: "development",
  devtool: "source-map",
  // TODO: hot reload isn't working anyway, figure out how to restore it
  // this line causes some other race-condition issues with compilation
  // watch: true,
});
