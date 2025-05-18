# Useful HTTP Flags

## Hide Progress

`-s`, `--silent`

Enables silent/quiet mode and mutes curl. In this mode, curl won't show any progress meters or error messages.

## Verbose

`-v`, `--verbose`

Enables verbose mode. Useful for debugging.
A line beginning with `>` is header data sent by curl.
A line beginning with `<` is header data received by curl.
A line beginning with `*` is additional data that curl provides.
(All of these data are normally disable and not displayed by default.)

NB. This flag/option overrides `--trace` and `--trace-ascii <file>`. 
NB. If you only want HTTP headers in your output, then `-i`, `--inlude` is most likely the preferable flag/option.

## Extra Information

`-w <format>`, `--write-out <format>`

curl will display info via stdout after a completed transfer.
`<format>` is a string that can contain plain text, as well as a combination of any number of variables.
Output will be written to stdout by default. But using `%{stderr}` will write output to stderr instead.

There's (a long list)[https://curl.se/docs/manpage.html#-w] of variables to use with this flag/option.

## Output

`-o <file>`, `--output <file>`

Write output to `<file>` instead of stdout.

## Timeout

`-m <seconds>`, `--max-time <seconds>`

Maximum time (in `<seconds>`) that you'd like an entire operation to try before timing out.
This can be useful when running batch job(s) to ensure that the job(s) are prevented from hanging for extended periods of time due to slow networks or outages. 

## POST

`-d "string"`, `-d @file`

## Encoded POST

`--data-urlencode "[name]=val"`

## Multipart Form POST

`-F name=value`, `-F name=@file`

## PUT

`-T <file>`

## HEAD (ers too)

`-i`, `-I`

## Custom Method

`-X "METHOD"`

## Read Cookie Jar

`-b <file>`

## Write Cookie Jar

`-c <file>`

## Send Cookies

`-b "c=1; d=2"`

## User Agent

`-A "string"`

## Proxy

`-x <host:port>`

## Add & Remove Headers

`-H "name: value"`, `-H "name:"`

## Custom Address

`--resolve <host:port:addr>`

## Smaller Data

`--compressed`

## Insecure HTTPS

`-k`

## Basic Authentication

`-u user:password`

## Follow Redirects

`-L`

## Parallel

`-Z`

## Generate Code

`--libcurl <file>`

## List Options

`--help`

It's dangerous to go alone! Take this. 
