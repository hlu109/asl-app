from bs4 import BeautifulSoup
import requests
import os

sources = ['SIGNINGSAVVY', 'LIFEPRINT']
SIGNINGSAVVY = 'https://www.signingsavvy.com'
LIFEPRINT_PREFIX = 'https://lifeprint.com/asl101/pages-signs'
LIFEPRINT_SUFFIX = '.htm'

def get_media(word, source='SIGNINGSAVVY'):
    """ returns list of .mp4 links
        arguments: 
            word, the string to look up in the dictionary
            source, the asl website to search. must be from the list sources"""
    
    mp4s = []
    labels = []

    if source=='SIGNINGSAVVY':
        search_url = os.path.join(SIGNINGSAVVY, 'search', word)
        var_urls = [search_url]

        r_search = requests.get(search_url)
        page_soup = BeautifulSoup(r_search.text, "lxml")

        # get links for all variations of the sign
        # if there is a single result, the html will contain a div tag with the 
        # class "signing_header"; 
        # if there are multiple results, then we need to look through the 
        # "search_results" div to pick which term we actually want.
        header_div = page_soup.findAll("div", {"class": "signing_header"})

        variations_li = header_div[0].ul.findAll('li')

        for var in variations_li:
            link_suffix = var.a['href']
            var_label = var.a.text
            labels.append(var_label)
            if 'javascript:;' not in link_suffix:
                var_urls.append(os.path.join(SIGNINGSAVVY, link_suffix))

        # iterate through variations of the sign, then save the mp4 link along
        # with the variation label
        for url in var_urls:
            r = requests.get(url)
            page_soup = BeautifulSoup(r.text, "lxml")
            vid_div = page_soup.findAll("div", {"class": "videocontent"})

            media_url = os.path.join(SIGNINGSAVVY, vid_div[0].source['src'])
            mp4s.append(media_url)
    
    elif source == 'LIFEPRINT':
        search_url = os.path.join(LIFEPRINT_PREFIX, word[0], word,
                                    LIFEPRINT_SUFFIX)
        
        r_search = requests.get(search_url)
        page_soup = BeautifulSoup(r_search.text, "lxml")

        # TODO: figure out way to parse natural language on the web page and
        # label media variations

    return mp4s, labels

# testing 
# print(get_media('happy'))
# print(get_media('avocado'))
# print(get_media('math'))
# print(get_media('computer science'))
# get_media('cat', source='LIFEPRINT')