# Use Logpoints to Log Messages to the Console

Are you a `console.log()` [debuggerer](http://tenderlovemaking.com/2016/02/05/i-am-a-puts-debuggerer.html) too?

With Logpoints, now you can easily debug and log messages to the DevTools Console without cluttering your IDE with `console.log()` statements.

(Some may say that using Logpoints also ensures that you'll never commit a leftover `console.log(~~~~~MADE IT HERE~~~~)` again, but ESLint's `no-console` [rule](https://eslint.org/docs/rules/no-console) should already be taking care of that.)

To add a logpoint:

1. Locate the your desired source in DevTools.
2. Right-click the line number where you'd like to add a logpoint.
3. Select `Add logpoint` and the Breakpoint Editor will appear.
4. In the Breakpoint Editor, enter the expression that you'd like to log.
5. Press `Enter` to save and an orange badge will appear on the line number for your logpoint.
6. The next time that badged line executes, DevTools logs the result of the logpoint expression to the console.

> Note: 
> When logging a variable, e.g. `myVar`, wrap the variable in an object .i.e `{ myVar }` to log both the variable's name and value.
> Keep "[Always log objects](https://medium.com/frontmen/art-of-debugging-with-chrome-devtools-ab7b5fd8e0b4#a4f3)" in mind and learn more about [Object Property Value Shorthand](https://alligator.io/js/object-property-shorthand-es6/).
