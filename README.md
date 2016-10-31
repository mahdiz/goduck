# GoDuck

[Godoc](https://godoc.org/golang.org/x/tools/cmd/godoc) is a built-in tool in
[Go](https://golang.org/) that allows to extract and generate documentation
for Go programs automatically. Godoc can be either run as a webserver to view
the documentation as a website in a browser or be used to print text
or html output to standard output. The output can be, of course, redirected to
a file for an offline presentation of the documentation.

Unfortunately, if one wants to generate offline documentation for a complete
package, he/she has to godoc every Go file in the package and manage the links
between HTML files manually. This is what GoDuck does automatically.

GoDuck establishes a Godoc webserver automatically on a random port and
downloads the complete package documentation from the server. It corrects all
URLs in the downloaded HTML files to avoid broken links. It also removes
unnecessary links, buttons, etc from the downloaded Godoc pages to generate
good-looking HTML files that can be browsed completely offline from the Internet
and without requiring to establish a Godoc webserver on the target machine.

## Usage
To use GoDuck, you need Python 2.7+ with
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup)
and Go installed on your machine. You can install Beautiful Soup from [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
and Go from [here](https://golang.org/doc/install).

Once you have both of these installed run GoDuck using
```bash
python goduck.py -d [package to be goducked] -o [output directory] -t [project title]
```

For example,
```bash
python goduck.py -d github.com/dedis/cothority -o /Users/mahdiz/goduck -t "The Cothority Project"
```

You can then browse the package documentation by opening `index.html` from the
output directory. Clicking on links in this HTML page will take you to other
HTMLs that correspond to other Go source files in the package.

