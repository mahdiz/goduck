# GoDuck -- Generate offline godoc documentation
# Run with Python 2.7
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


def beautify(soup, depth):
    # Change style paths
    stylePath = '../' * depth + '.goduckstyle/'
    for link in soup.findAll('link'):
        if link.has_attr('href'):
            link['href'] = str(link['href']).replace('/lib/godoc/', stylePath)

    for script in soup.findAll('script'):
        if script.has_attr('src'):
            script['src'] = str(script['src']).replace('/lib/godoc/', stylePath)

    # Change html title
    if libTitle is not None:
        title = soup.find('title')
        title.string = title.text.split('-')[0] + '- ' + libTitle

    # Change page header
    header = soup.find(name="div", id="heading-wide")
    header.string = libTitle

    # Remove unused menu items
    remove_tag(soup, name="a", text="Documents")
    remove_tag(soup, name="a", text="Help")
    remove_tag(soup, name="a", text="Blog")
    remove_tag(soup, name="input", id="search")


def duckify(http, url, outDir, depth=1):
    print('Duckifying ' + url)

    s, content = http.request(url)
    soup = bs4.BeautifulSoup(content, 'html.parser')
    beautify(soup, depth)

    subName = url.rsplit('/', 2)[1]
    newOutDir = outDir + subName + '/'
    if not os.path.exists(newOutDir):
        os.makedirs(newOutDir)

    # Duckify the children
    for link in soup.findAll('a'):
        if link.has_attr('href') and link['href'] != '..' and link['href'] != '#' and \
                link['href'] != '/' and link['href'][0] != '/' and \
                link['href'][0] != '#' and link['href'][:7] != 'http://' and \
                link['href'][:8] != "https://" and link['href'][0:4] != 'www':
            duckify(http, url + link['href'], newOutDir, depth + 1)
            link['href'] = link['href'] + 'index.html'

    with open(newOutDir + 'index.html', 'w') as outf:
        outf.write(str(soup))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='GoDuck - Generate offline godoc documentation (run with Python 2.7)')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-d', help='package to goduck', required=True)
    required.add_argument('-o', help='output path', required=True)
    parser.add_argument('-t', help='project title')
    args = parser.parse_args()

    port = str(get_open_port())
    serverUrl = 'http://localhost:' + port + '/'
    dir = serverUrl + 'pkg/' + args.d
    if dir[-1] != '/':
        dir += '/'
    libTitle = args.t

    print('Starting godoc server on port ' + port + '...')
    p = subprocess.Popen(['/usr/local/bin/godoc', '-http=:' + port])
    time.sleep(2)

    outDir = args.o
    if outDir[-1] != '/':
        outDir += '/'

    # Download style files
    styleDir = outDir + '.goduckstyle' + '/'
    if not os.path.exists(styleDir):
        os.makedirs(styleDir)

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

    duckify(http, dir, outDir)

    print('Terminating godoc server...')
    p.terminate()

    print('Package goducked successfully.')