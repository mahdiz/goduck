# GoDuck -- Generate offline godoc documentation
# Run using Python 2.7
# Mahdi Zamani (mahdi.zamani@yale.edu)

import sys, bs4, argparse, httplib2, subprocess, os, time


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def download(http, url, dest):
    s, req = http.request(url)
    with open(dest, 'w') as outf:
        outf.write(req)


def remove_tag(soup, name, id=None, text=None):
    tag = soup.find(name, id=id, text=text)
    if tag is not None:
        tag.replaceWith('')


def remove_slash(soup, name, field):
    for tag in soup.findAll(name):
        if field in tag.attrs and tag[field] != '' and tag[field][0] == '/':
            tag[field] = tag[field][1:]


def beautify(soup, depth=0, removeTOC=False):
    # Change style paths
    stylePath = '../' * depth + '.goduckstyle/'
    for link in soup.findAll('link'):
        if link.has_attr('href'):
            link['href'] = str(link['href']).replace('/lib/godoc/', stylePath)

    for script in soup.findAll('script'):
        if script.has_attr('src'):
            script['src'] = str(script['src']).replace('/lib/godoc/', stylePath)

    # Change image paths
    for img in soup.findAll('img'):
        if img.has_attr('src'):
            img['src'] = str(img['src']).replace('/doc/gopher/', stylePath)

    # Change html title
    if projTitle is not None:
        title = soup.find('title')
        title.string = title.text.split('-')[0] + '- ' + projTitle

    # Change page header
    header = soup.find(name="div", id="heading-wide")
    header.string = projTitle
    headerNarrow = soup.find(name="div", id="heading-narrow")
    headerNarrow.string = projTitle

    # Remove table of contents if requested
    if removeTOC:
        remove_tag(soup, name="div", id="nav")
        remove_tag(soup, name="div", id="manual-nav")

    # Remove unused menu items
    remove_tag(soup, name="a", text="Documents")
    remove_tag(soup, name="a", text="Help")
    remove_tag(soup, name="a", text="Blog")
    remove_tag(soup, name="a", text="The Project")
    remove_tag(soup, name="a", text="Packages")
    remove_tag(soup, name="input", id="search")
    remove_tag(soup, name="div", id="footer")


def duck(http, rootUrl, packageDir, package, depth=1):
    print('Ducking ' + rootUrl)

    s, content = http.request(rootUrl)
    soup = bs4.BeautifulSoup(content, 'html.parser')
    beautify(soup, depth)

    subName = rootUrl.rsplit('/', 2)[1]
    newOutDir = packageDir + subName + '/'
    if not os.path.exists(newOutDir):
        os.makedirs(newOutDir)

    # Duck the children
    for link in soup.findAll('a'):
        if link.has_attr('href') and link['href'] != '..' and link['href'] != '#' and \
                link['href'] != '/' and link['href'][0] != '/' and \
                link['href'][0] != '#' and link['href'][:7] != 'http://' and \
                link['href'][:8] != "https://" and link['href'][0:4] != 'www':
            duck(http, rootUrl + link['href'], newOutDir, package, depth + 1)
            link['href'] = link['href'] + 'index.html'

        elif str(link['href']).startswith('/pkg/builtin'):
            link['href'] = str(link['href']). \
                replace('/pkg/builtin', 'https://golang.org/pkg/builtin')

        elif str(link['href']).startswith('/pkg/'):
            link['href'] = str(link['href']).replace('/pkg/', '../' * depth). \
                replace('/#', '/index.html#')
            if link['href'][-1] == '/':
                link['href'] += 'index.html'

    with open(newOutDir + 'index.html', 'w') as outf:
        outf.write(str(soup))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
                                     'GoDuck - Generate offline godoc documentation (run with Python 2.7)')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-d', help='package to goduck', required=True)
    required.add_argument('-o', help='output path', required=True)
    parser.add_argument('-t', help='project title')
    args = parser.parse_args()

    port = str(get_open_port())
    package = args.d
    if package[-1] != '/':
        package += '/'

    serverUrl = 'http://localhost:' + port + '/'
    packageUrl = serverUrl + 'pkg/' + package
    projTitle = args.t

    print('Starting godoc server on port ' + port + '...')
    p = subprocess.Popen(['godoc', '-http=:' + port])
    time.sleep(3)

    rootDir = args.o
    if rootDir[-1] != '/':
        rootDir += '/'

    # Create go-like directory structure for the packages
    depth = 0
    packageDir = rootDir
    for dir in package.split('/')[:-2]:
        depth += 1
        packageDir += dir + '/'
        if not os.path.exists(packageDir):
            os.makedirs(packageDir)

    # Download style files
    styleDir = rootDir + '.goduckstyle' + '/'
    if not os.path.exists(styleDir):
        os.makedirs(styleDir)

    print('Downloading style and image files...')
    http = httplib2.Http()
    download(http, serverUrl + 'lib/godoc/style.css', styleDir + 'style.css')
    download(http, serverUrl + 'lib/godoc/godocs.js', styleDir + 'godocs.js')
    download(http, serverUrl + 'lib/godoc/jquery.treeview.css',
             styleDir + 'jquery.treeview.css')
    download(http, serverUrl + 'lib/godoc/jquery.js', styleDir + 'jquery.js')
    download(http, serverUrl + 'lib/godoc/jquery.treeview.edit.js',
             styleDir + 'jquery.treeview.edit.js')
    download(http, serverUrl + 'lib/godoc/jquery.treeview.js',
             styleDir + 'jquery.treeview.js')
    download(http, serverUrl + 'doc/gopher/pkg.png', styleDir + 'pkg.png')

    duck(http, packageUrl, packageDir, package, depth + 1)

    # Add packages list HTML to the root directory
    s, pkListContent = http.request(serverUrl + 'pkg/')
    soup = bs4.BeautifulSoup(pkListContent, 'html.parser')
    beautify(soup, removeTOC=True)

    # Remove missing packages' entries
    for link in soup.findAll('a'):
        if (
        not os.path.exists(rootDir + link['href'])) and link.parent.name == 'td' \
                and link.parent.parent.name == 'tr':
            link.parent.parent.replaceWith('')
        elif link.parent.name == 'td' and link.parent.parent.name == 'tr':
            if os.path.exists(rootDir + link['href'] + 'index.html'):
                link['href'] += 'index.html'
            else:
                link['href'] = '#'

    with open(rootDir + 'doc.html', 'w') as outf:
        outf.write(str(soup))

    print('Terminating godoc server...')
    p.terminate()

    print('Package goducked successfully.')