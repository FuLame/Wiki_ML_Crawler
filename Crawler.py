import urllib
#from BeautifulSoup import *
from bs4 import BeautifulSoup
import time


class link(object):    
    def __init__(self,url="",title=""):
        if not url.startswith("https"):
            self.url = "https://en.wikipedia.org"+url
        else:
            self.url = url
        self.title = title
        
    def __str__(self):
        return self.title
        
    def get_url(self):
        return self.url[:]
        
    def set_title(self,title):
        self.title = title[:-12]

    def get_short_url(self):
        return self.url[:].replace("https://en.wikipedia.org","")
        
        
url2 = "https://en.wikipedia.org/robots.txt"
start_url = link("https://en.wikipedia.org/wiki/Machine_learning")
#start_url = link("https://en.wikipedia.org/wiki/Pedro_Domingos")

keywordList = [["machine learning", "robot learning", "computer learning"],\
               ["reinforced learning", "reinforcement learning",\
                "feature learning", "supervised learning"],\
               ["neural network", "neural","deep learning", "deep network",\
                "brain", "propagation"],\
               ["artificial intelligence", "AI", "computer intelligence"],\
               ["data mining", "big data", "azure", "hardoop"],\
               ["data analysis", "data analytics", "data science", "research",\
                "computer science", "data model"],\
               ["detection", "recognition", "computer vision", "correlation",\
                "correlate", "language processing", "image processing", "speech"],\
               ["clustering", "cluster", "anomaly", "recommend"],\
               ["biography"],\
               ["amazon", "netflix", "google", "baidu", "microsoft", "tesla",\
                "apple", "facebook", "alexa"],\
               ["neuron", "perceptron"],\
               ["bayes", "naive", "support vector machine", "svm", "svc",\
                "algorithm", "random forest", "kernel", "decision tree",\
                "nearest neighbors", "classifier", "regression"],\
                ["octave", "matlab", "mathematica", "python", "scala"],\
                ["tensor", "caffe", "sklearn", "scikit", "kaggle", "openai",\
                 "spark", "crowdai", "enigma", "theano", "torch", "apache"],\
                ["logistic", "activation", "sigmoid", "minima", "optimaliz",\
                 "matrix", "vector", "bias", "loss function", "cost function"]]


                      

def get_pagetitle(url):
    '''
    url: url to the target wikipedia webpage
    returns: title of the target wikipedia webpage
    '''
    return BeautifulSoup(urllib.urlopen(url).read()).title.string[1:-12]

def get_featureVector(soup, keywordList=keywordList):
    feature_vect = [0]*len(keywordList)
    #result[current_url] = feature_vect[:]
    #result_accumul[current_url] = feature_vect[:]
    
    text = soup.get_text().split('\n')
    
    for line in text:
        for idx, keyword in enumerate(keywordList):
            for key in keyword:
                if key.lower() in line:
                    feature_vect[idx] += 1
    return feature_vect
    
               

html = urllib.urlopen(start_url.get_url()).read()
soup = BeautifulSoup(html)             

result = dict()
result_accumul = dict()

start_url.set_title(soup.title.string)
urls_tovisit = [start_url]
urls_visited = list()

#while len(urls_tovisit) != 0:
for i in range(200):
    time.sleep(0.1)
    
    current_url = urls_tovisit[0]
    print("Searching "+str(current_url.get_short_url()))
    
    html = urllib.urlopen(current_url.get_url()).read()
    soup = BeautifulSoup(html)
    current_url.set_title(soup.title.string)
    
    urls_tovisit = urls_tovisit[1:]
    
    vect = get_featureVector(soup)
    if sum(vect) < 12:
        continue    
    result_accumul[current_url.get_short_url()] = vect



    tags = soup('a')
    urls_local = list()
    for tag in tags:
        href_param = tag.get('href', None)
        if href_param!=None and href_param.startswith("/wiki/") and (":" not in href_param):
            urls_local.append(tag.get('href', None))
    for url in set(urls_local):
        if url not in [x.get_short_url() for x in urls_visited+urls_tovisit]:
            urls_tovisit.append(link(url))
            
    current_url.set_title(soup.title.string)  
    urls_visited.append(current_url)


#for url in urls_tovisit:
 #   print url.url


