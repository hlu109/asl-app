from bs4 import BeautifulSoup
import requests
import os
import logging

sources = ['SIGNINGSAVVY', 'LIFEPRINT']
SIGNINGSAVVY = 'https://www.signingsavvy.com'
LIFEPRINT_PREFIX = 'https://lifeprint.com/asl101/pages-signs'
LIFEPRINT_SUFFIX = '.htm'
CURRENT_PAGE_LINK_SUFFIX = 'javascript:;'

def get_terms(word, source='SIGNINGSAVVY'):
    """ if no signs exist, returns None. Otherwise, returns list of 3-tuples 
        (term, url_suffixes, descriptions) for the various terms
    """
    
    if source=='SIGNINGSAVVY':
        search_url = os.path.join(SIGNINGSAVVY, 'search', word)
        r_search = requests.get(search_url)
        page_soup = BeautifulSoup(r_search.content, "html.parser")
        
        search_results_div = page_soup.find("div", class_="search_results")
        if search_results_div == None:
            if page_soup.find("div", class_ = "sign_module"): 
                # word is unique
                return [(word, 'search/' + word, None)]
            else: 
                # word does not exist
                return None
        
        # multiple search results 
        results = []
        terms_li = search_results_div.ul.find_all('li')

        for term in terms_li:
            if term.em is not None:
                description = term.em.text.replace("&quot", "\"").split("\"")[1]
            else:
                description = None
            results.append((term.a.text.title(), term.a['href'], description))
    
    return results

def get_media(word, url_suffix=None, source='SIGNINGSAVVY'):
    """ returns list of .mp4 links and list of labels
        arguments: 
            word, the string to look up in the dictionary
            url_suffix, string with the format "sign/{TERM}/{ID}{/OPTIONAL VARIATION INDEX}" (e.g. "sign/RUN/10423/1")
            source, the asl website to search. must be from the list sources"""

    mp4s = []
    labels = []

    if source=='SIGNINGSAVVY':
        if not url_suffix:
            search_url = os.path.join(SIGNINGSAVVY, 'search', word)
        else:
            search_url = os.path.join(SIGNINGSAVVY, url_suffix)
        var_urls = []

        r_search = requests.get(search_url)
        page_soup = BeautifulSoup(r_search.content, "html.parser")

        # get links for all variations of the sign
        # if there is a single result, the html will contain a div tag with the 
        # class "signing_header"; 
        # if there are multiple results, then we need to look through the 
        # "search_results" div to pick which term we actually want.
      
        # header_div = page_soup.findAll("div", {"class": "signing_header"})
        header_div = page_soup.find("div", class_="signing_header")

        variations_li = header_div.ul.find_all('li')

        for var in variations_li:
            link_suffix = var.a['href']

            # TODO: i was thinking about getting the button label (e.g. "ASL 
            # 1", "finger spell", etc) but it doesn't seem like that 
            # information is in the html (my guess is it's in the CSS or JS 
            # somehow?) so this code for labels is pretty much pointless for now
            var_label = var.a.text
            labels.append(var_label)


            # signingsavvy's website changed their class attribute value
            if var.a.has_attr('class') and var.a['class'][0] == 'current':
                # or
                # if link_suffix == CURRENT_PAGE_LINK_SUFFIX:
                var_urls.append(search_url)
            else:
                var_urls.append(os.path.join(SIGNINGSAVVY, link_suffix))

        # iterate through variations of the sign, then save the mp4 link along
        # with the variation label
        for url in var_urls:
            r = requests.get(url)
            page_soup = BeautifulSoup(r.content, "html.parser")
            vid_div = page_soup.find("div", class_="videocontent")

            # updating since signingsavvy changed their links from relative to 
            # absolute
            # media_url = os.path.join(SIGNINGSAVVY, vid_div.source['src'])
            media_url = vid_div.source['src']
            mp4s.append(media_url)
    
    elif source == 'LIFEPRINT': 
        search_url = os.path.join(LIFEPRINT_PREFIX, word[0], word,
                                    LIFEPRINT_SUFFIX)
        
        r_search = requests.get(search_url)
        page_soup = BeautifulSoup(r_search.content, "html.parser")

        # TODO: figure out way to parse natural language on the web page and
        # label media variations

    return mp4s, labels

if __name__ == "__main__":
    ## testing ##
    # print(get_media('happy'))
    print('testing get_media()\n-------------------')
    print(get_media('avocado'))
    print(get_media('math'))
    print(get_media('computer science'))
    print(get_media('run', url_suffix='sign/RUN/10423/1'))
    # get_media('cat', source='LIFEPRINT')

    print('\ntesting get_terms()\n------------------------')
    print(get_terms('run'))
