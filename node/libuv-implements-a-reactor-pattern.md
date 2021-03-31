# `libuv` Implements a Reactor Pattern

`libuv` is Node's low-level I/O engine. Other than abstracting underlying system calls, `libuv` also implements [the Reactor pattern](http://www.dre.vanderbilt.edu/~schmidt/PDF/reactor-siemens.pdf), which also provides an API for:

- creating event loops,
- managing the event queue,
- running async I/O operations, and
- queueing other tasks

![](https://static.packt-cdn.com/products/9781783287314/graphics/7314OS_01_03.jpg)

This pattern coordinates:

1. feeding asynchronous events into the queue,
2. executing those events as resources become available, and then
3. popping those events off of the queue to make requests to any callbacks provided by application code.

TODO:

- [What the heck is the event loop anyway?](https://www.youtube.com/watch?v=8aGhZQkoFbQ)
- [The Reactor Pattern](https://subscription.packtpub.com/book/web_development/9781783287314/1/ch01lvl1sec09/the-reactor-pattern)
