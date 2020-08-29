# Disable Jest's Auto-generated Coverage Reports

Enabling [Jest's coverage option](https://jestjs.io/docs/en/cli#--coverageboolean) is great. Receiving alerts for untested blocks of code is important, pragmatic, and can give us confidence in the code we write!

But a tradeoff of enablting test coverage with Jest is that it generates _a lot_ of files. The files that Jest generates are report files that allow us to view our coverge in a variety of formats e.g. JSON, HTML, etc. While this is convenient, sometimes these files aren't necessary and we just want direct coverage alerts to standard out.

Luckily, coverage reports are easy to disable with Jest's `coverageReporters` [option](https://jestjs.io/docs/en/configuration#coveragereporters-arraystring--string-options). Set the value of `coverageReporters` to `["text", "text-summary"]` in your `package.json` or `jest.config.js` and then Jest will only output coverage results to the terminal wihtout generating any report files.
