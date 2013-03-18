import urllib2
import bs4
import re
import datetime
import os
from bs4 import BeautifulSoup



def get_nonlink_length(soup_tag):
    total = len(soup_tag.get_text())
    link_total = 0
    for link in soup_tag.find_all('a'):
        link_total += len(link.get_text())
    return total - link_total

def filter_func(x):
    link_length = len(x)
    non_link_length = get_nonlink_length(x.parent)
    return non_link_length < 10

def remove_tag(soup):
    [script.decompose() for script in soup.find_all('script')]
    #[meta.extract() for meta in soup.find_all('meta')]
    [style.decompose() for style in soup.find_all('style')]
    #[table.extract() for table in soup.find_all('table')]
    [link.extract() for link in soup.head.find_all('link')]
    [select.decompose() for select in soup.find_all('select')]
    [comment.extract() for comment in soup.find_all(text=lambda text:isinstance(text,bs4.element.Comment))]
    #[dl.extract() for dl in soup.find_all('dl')]
    #[ol.extract() for ol in soup.find_all('ol')]
    #[ul.extract() for ul in soup.find_all('ul')]
    [iframe.extract() for iframe in soup.find_all('iframe')]
    del_block = set([link.parent for link in filter(filter_func, soup.find_all('a'))])
    for block in del_block:
        block.extract()
    """for remove_link in filter(filter_func,soup.find_all('a')):
        remove_link.parent.decompose()
    """
    
def has_src_no_hostname(tag):
    if tag.has_key('src'):
        src = tag['src']
        return re.match('^http://', src) == None
    return False

def add_site_prefix(soup, hostname):
    for content in soup.find_all(has_src_no_hostname): 
        origin_src = content['src']
        content['src'] = 'http://'+hostname+origin_src


def get_main_content(soup_tag):
    CONTENT_THRESHOLD = 0.5
    LINK_THRESHOLD = 10

    current_content = soup_tag
    current_length = len(current_content.get_text())
    current_list = current_content.contents
    candidate_list = []
    for content in current_list:
        if isinstance(content, bs4.element.Tag) and content.name != 'br':
            if len(content.get_text()) >= (current_length * CONTENT_THRESHOLD):
                candidate_list.append(content)
    if len(candidate_list) == 0:
        return current_content
    return get_main_content(candidate_list[0])
        
def remove_style(soup_tag):
    style_tag = soup_tag.find_all(style=True) 
    for tag in style_tag:
        del tag['style']


#def get_paragraph_list(main_content):

def format_string(string):
    string = re.sub('^[\s]+$|\xa0','',string)
    return re.sub('^[\s]+|\s*\r\n\s*|^\n\s*\n$','',string)
    
def format_filename(filename):
    return re.sub('[\\\/\:\*\?"\<\>\|\\r\\n\\t]','',filename)

def empty_string(str):
    return len(re.sub('\n|\s|\r|\xa0','',str)) == 0

def get_text(soup_tag):
    if isinstance(soup_tag, bs4.element.NavigableString):
        return format_string(soup_tag)
    contents = soup_tag.contents
    result = ''
    if soup_tag.name == 'br':
        result += '\n'
    for content in contents:
       result += get_text(content)
    if soup_tag.name == 'p':
        if not empty_string(soup_tag.get_text()):
            result += '\n\n'
    return result

def write_to_file(content_list, filename):
    cur_dt = datetime.datetime.today()
    dirname = cur_dt.strftime("%Y%m%d")

    WORK_PREFIX = 'c:\\Users\\t-luyaof\\Dropbox\\Python\\Tools\\'
    HOME_PREFIX = 'f:\\Dropbox\\Python\\Tools\\'
    path_prefix = WORK_PREFIX
    if not os.path.exists(path_prefix + 'Articles\\'+dirname):
        os.mkdir(path_prefix + 'Articles\\'+dirname)
    filename = format_filename(filename)
    file = open(path_prefix + 'Articles\\'+dirname+'\\'+filename+'.txt','w')
    count = 0
    text = ''
    for content in content_list:
        string = get_text(content)
        text += string
        count += 1
        if len(string) > 0:
            file.write(string.encode('utf8'))
    file.close()
    return text 
        

"""    
"""

class Article:
    """
    article parsed from HTML
    contains article title and content
    """
    def __init__(self, url):
        self.url = url

    def parse(self):
        (self.title, self.content,self.text) = get_article(self.url)

def get_article(url):
    #url = 'http://blog.renren.com/share/292736783/15249284190?from=0101010202&ref=hotnewsfeed&sfet=102&fin=11&fid=21271721492&ff_id=292736783&platform=0&expose_time=1359701503'
    WORK_PREFIX = 'c:\\Users\\t-luyaof\\Dropbox\\Python\\Tools\\'
    HOME_PREFIX = 'f:\\Dropbox\\Python\\Tools\\'
    log_prefix = WORK_PREFIX 
    log_file = open(log_prefix + 'Articles\\'+'parser_log.txt','a')
    log_dt = datetime.datetime.today()
    log_file.write(log_dt.isoformat()+'\t')
    log_file.write(url + '\n')
    log_file.close()

    print "log complete"
    req = urllib2.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    html = urllib2.urlopen(req)
    print 'get html from ' + url

    soup = BeautifulSoup(html.read())
    print 'parsed as soup'
    remove_tag(soup)

    main_content = get_main_content(soup.html.body)
    print 'get main content block'
    
    hostname = req.get_host()
    add_site_prefix(main_content, hostname)

    remove_style(main_content)
    article = main_content.prettify()
    #print main_content.find_previous_siblings()

    #print main_content.find_next_siblings()
   
    main_text_list = main_content.contents
    article_title = re.sub('\\r\\t\\n','',soup.title.text)
    text = write_to_file(main_text_list, article_title)
    return (article_title,article,text)
    #return main_text_list


