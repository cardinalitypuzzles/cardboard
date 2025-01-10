const path = require("path");

module.exports = {
  entry: "./hunts/src/index.tsx",
  output: {
    path: path.resolve(__dirname, "hunts/static"),
    filename: "main.js",
  },
  resolve: {
    extensions: [".js", ".jsx", ".ts", ".tsx"],
  },
  module: {
    rules: [
      {
        test: /\.(m?)(js|jsx|ts|tsx)$/,
        enforce: "pre",
        use: ["source-map-loader"],
      },
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
};
