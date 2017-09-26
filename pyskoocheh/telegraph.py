""" 
    Telegraph Module

    Holds functions for working with telegra.ph API
"""
import re


def telegraph_tame_text(text):
    '''
        Identifies links and images in input and converts text telegraph-friendly
        text

        Args:
        text: source text in markdown

        Returns:
        Telegra.ph friendly content in list format
    '''

    if text is None:
        return []

    INLINE_IMAGE_RE = re.compile(r'\!\[\]\(([^\)]*)\)')
    pics = INLINE_IMAGE_RE.findall(text)
    res_list = []
    current_index = 0
    link_found = False

    if len(pics) > 0:
        link_found = True
        for pic in pics:
            subtext = text[current_index:]
            ind = current_index + subtext.index(pic) - 4
            res_list.append(text[current_index:ind])
            res_list.append({"tag": "br"})
            res_list.append({"tag": "img", "attrs": {"src": pic.encode('utf8')}})
            current_index = subtext.index(pic) + current_index + len(pic) + 1

        res_list.append(text[current_index:])

    if not link_found:
        res_list.append(text)

    INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    res_list_new = []

    for chunk in range(len(res_list)):
        if type(res_list[chunk]) == dict:
            res_list_new.append(res_list[chunk])
            continue

        current_index = 0
        links = INLINE_LINK_RE.findall(res_list[chunk])

        if len(links) > 0:
            link_found = True
            for link in links:
                subchunk = res_list[chunk][current_index:]
                ind = current_index + subchunk.index(link[0]) - 1
                res_list_new.append(res_list[chunk][current_index:ind].encode('utf8'))
                res_list_new.append(
                    {
                        'tag': 'a',
                        'attrs': {
                            'href': link[1].encode('utf8')
                        },
                        'children': [link[0].encode('utf8')]
                    }
                )
                current_index = subchunk.index(link[1]) + current_index + len(link[1]) + 1

            res_list_new.append(res_list[chunk][current_index:].encode('utf8'))
        else:
            res_list_new.append(res_list[chunk].encode('utf8'))
    res_list_new.append('\n')

    if link_found:
        return res_list_new

    return [text + '\n']


def telegraph_create_pages(cont_dic_list, sel, author):
    '''
        Creates and edits Telegr.ph pages through communicating with the
        Telegraph api

        Args:
        cont_dic_list: items for which telegraph pages should be modified. This arg
        is a list of objects with attributes: path, title, content and version
        sel: Telegraph object created with secret access token
        author: name of telegra.ph pages' author retrieved from settings
    '''

    for item in cont_dic_list:
        path = item['path']
        title = item['title']
        cont = item['content']
        header = item['header']
        urls = []

        if path and len(path) > 0:
            new_page = sel.edit_page(path, title, content=cont, author_name=author, author_url='https://paskoocheh.com/')

        else:
            new_page = sel.create_page(title=header, content=[{"tag": "p", "children": ["No content"]}], author_name='Anonymous', author_url='http://telegra.ph/', return_content='true')
            new_page = sel.edit_page(path=new_page['path'], title=title, content=cont, author_name=author, author_url='https://paskoocheh.com/')
            new_url = 'http://telegra.ph/' + new_page['path']
            urls.append(new_url)

    return urls
