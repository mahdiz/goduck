# GoDuck
# Mahdi Zamani (mahdi.zamani@yale.edu)

import sys, bs4, argparse, httplib2, subprocess, os, time

def removeTag(soup, name, id=None, text=None):
    tag = soup.find(name, id=id, text=text)
    if tag is not None:
        tag.replaceWith('')

def removeSlash(soup, name, field):
    for tag in soup.findAll(name):
        if field in tag.attrs and tag[field] != '' and tag[field][0] == '/':
            tag[field] = tag[field][1:]

def beautifyPage(soup, depth):
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
    removeTag(soup, name="a", text="Documents")
    removeTag(soup, name="a", text="Help")
    removeTag(soup, name="a", text="Blog")
    removeTag(soup, name="input", id="search")

def duckify(http, url, saveDir, depth=1):
    print('Duckifying ' + url)

    s, content = http.request(url)
    soup = bs4.BeautifulSoup(content, 'html.parser')
    beautifyPage(soup, depth)

    subName = url.rsplit('/', 2)[1]
    newSaveDir = saveDir + subName + '/'
    if not os.path.exists(newSaveDir):
        os.makedirs(newSaveDir)

    # Duckify the children
    for link in soup.findAll('a'):
        if link.has_attr('href') and link['href'] != '..' and link['href'] != '#' and \
                link['href'] != '/' and link['href'][0] != '/' and \
                link['href'][0] != '#' and link['href'][:7] != 'http://' and \
                link['href'][:8] != "https://" and link['href'][0:4] != 'www':
            duckify(http, url + link['href'], newSaveDir, depth + 1)
            link['href'] = link['href'] + 'index.html'

    with open(newSaveDir + 'index.html', 'w') as outf:
        outf.write(str(soup))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='GoDuck - Generate offline godoc htmls')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-d', help='directory to goduck', required=True)
    parser.add_argument('-t', help='package title')
    args = parser.parse_args()

    dir = 'http://localhost:6060/pkg/' + args.d
    if dir[-1] != '/':
        dir += '/'
    libTitle = args.t

    print('Starting godoc server on port 6060...')
    p = subprocess.Popen(['/usr/local/bin/godoc', '-http=:6060'])
    time.sleep(2)

    saveDir = '/Users/mahdiz/goduck/'
    http = httplib2.Http()
    duckify(http, dir, saveDir)

    print('Terminating godoc server...')
    p.terminate()

    print('Package goducked successfully.')