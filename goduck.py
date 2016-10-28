# GoDuck
# Mahdi Zamani (mahdi.zamani@yale.edu)

import sys, bs4, argparse

def removeTag(soup, name, id=None, text=None):
    tag = soup.find(name, id=id, text=text)
    if tag is not None:
        tag.replaceWith('')

def removeSlash(soup, name, field):
    for tag in soup.findAll(name):
        if field in tag.attrs and tag[field] != '' and tag[field][0] == '/':
            tag[field] = tag[field][1:]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='GoDuck - Generate offline godoc htmls')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', help='html file to goduck', required=True)
    parser.add_argument('-t', help='package title')
    args = parser.parse_args()

    filePath = args.f
    libTitle = args.t
    print('Loading ' + filePath)

    # Load the file
    with open(filePath) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, "html.parser")

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

    # Remove the slash from the beginning of all urls
    removeSlash(soup, 'link', 'href')
    removeSlash(soup, 'a', 'href')
    removeSlash(soup, 'script', 'src')

    # Save the file again
    with open(filePath, "w") as outf:
        outf.write(str(soup))

    print('File goducked successfully.')