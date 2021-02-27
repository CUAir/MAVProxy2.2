module.exports = {
    "env": {
        "browser": true,
        "es6": true
    },
    "extends": "eslint:recommended",
    "installedESLint": true,
    "parser": "babel-eslint",
    "parserOptions": {
        "ecmaFeatures": {
            "experimentalObjectRestSpread": true,
            "jsx": true
        },
        "sourceType": "module"
    },
    "plugins": ["react", "flowtype"],
    "rules": {
        "react/jsx-uses-vars": 1,
        "indent": ["error", 2],
        "linebreak-style": ["error", "unix"],
        "quotes": ["error", "single"],
        "semi": ["error", "always"],
        "accessor-pairs": "error",
        "default-case": "error",
        "no-eval": "error",
        "space-before-blocks": "error",
        "space-in-parens": ["error", "never"],
        "no-template-curly-in-string": "error",
        "no-unsafe-negation": "error",
        "flowtype/define-flow-type": 1,
        "flowtype/use-flow-type": 1,
        "eol-last": "error",
        "no-template-curly-in-string": "error",
        "no-prototype-builtins": "error",
        "no-unsafe-negation": "error",
        "array-bracket-spacing": ["error", "never"],
        "block-spacing": ["error", "always"],
        "comma-dangle": ["error", "never"]
    },
    "settings": {
        "flowtype": {
            "onlyFilesWithFlowAnnotation": true
        }
    }
};
