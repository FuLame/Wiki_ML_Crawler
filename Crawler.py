import urllib
#from BeautifulSoup import *
from bs4 import BeautifulSoup
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText

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
        

keywordList = ["machine learning", "robot learning", "computer learning",\
               "reinforced learning", "reinforcement learning",\
                "feature learning", "supervised learning",\
               "neural network", "neural","deep learning", "deep network",\
                "brain", "propagation",\
               "artificial intelligence", "AI", "computer intelligence",\
               "data mining", "big data", "azure", "hardoop",\
               "data analysis", "data analytics", "data science", "research",\
                "computer science", "data model",\
               "detection", "recognition", "computer vision", "correlation",\
                "correlate", "language processing", "image processing", "speech",\
               "clustering", "cluster", "anomaly", "recommend",\
               "biography",\
               "amazon", "netflix", "google", "baidu", "microsoft", "tesla",\
                "apple", "facebook", "alexa",\
               "neuron", "perceptron",\
               "bayes", "naive", "support vector machine", "svm", "svc",\
                "algorithm", "random forest", "kernel", "decision tree",\
                "nearest neighbors", "classifier", "regression",\
                "octave", "matlab", "mathematica", "python", "scala",\
                "tensor", "caffe", "sklearn", "scikit", "kaggle", "openai",\
                 "spark", "crowdai", "enigma", "theano", "torch", "apache",\
                "logistic", "activation", "sigmoid", "minima", "optimaliz",\
                 "matrix", "vector", "bias", "variance", "accuracy", "precision",\
                 "loss function", "cost function"]

                      

def get_pagetitle(url):
    '''
    url: url to the target wikipedia webpage
    returns: title of the target wikipedia webpage
    '''
    return BeautifulSoup(urllib.urlopen(url).read()).title.string[1:-12]

def get_featureVector(soup, keywordList=keywordList):
    feature_vect = {}#[0]*len(keywordList)
    #result[current_url] = feature_vect[:]
    #result_accumul[current_url] = feature_vect[:]
    
    text = soup.get_text().split('\n')
    '''
    for line in text:
        for idx, keyword in enumerate(keywordList):
            for key in keyword:
                if key.lower() in line:
                    feature_vect[idx] += 1
    return feature_vect'''
    for line in text:
        for keyword in keywordList:
            if keyword.lower() in line.lower():
                feature_vect[keyword.replace(" ","_")] = 1+feature_vect.get(keyword, 0)
    return feature_vect

def initializeDB():
    '''
    Initializes the database.
    '''
    try:
        conn = sqlite3.connect('wikiDump.sqlite')
        cur = conn.cursor()
        cur.executescript('''
        DROP TABLE IF EXISTS features;''')
        cur.executescript('''
        DROP TABLE IF EXISTS links_visited;''')
        cur.executescript('''
        DROP TABLE IF EXISTS links_tovisit;''')
        conn.commit()
    except:
        print "Could not connect to database"
        return None    
    
    #Create table links_tovisit
    cur.execute('''CREATE TABLE IF NOT EXISTS links_tovisit (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            links TEXT)''')
    
    #Create table links_visited
    cur.execute('''CREATE TABLE IF NOT EXISTS links_visited (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            links TEXT)''')
    
    #Create table features
    command_init_DB = '''CREATE TABLE IF NOT EXISTS features (
                                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                link TEXT,                                
                                '''
    command_init_DB += " INTEGER, ".join([x.replace(" ","_") for x in keywordList])
    command_init_DB += " INTEGER)"
    cur.execute(command_init_DB)
    conn.commit()
    conn.close()
    print "Database initialized"
    
def savetoDB(vect,url):
    '''
    Saves a feature vector the database.
    '''
    try:
        conn = sqlite3.connect('wikiDump.sqlite')
        cur = conn.cursor()
    except:
        print "Could not connect to database"
        return None   
    
    #Add feature vector to features table
    vect['link'] = "'"+url+"'"
    col = list()
    placeH = list()
    for item in vect:
        col.append(item)
        placeH.append(str(vect.get(item,0)))
    command_db = '''INSERT OR IGNORE INTO features (%s)
    VALUES 
    (%s)'''% (", ".join(col), ", ".join(placeH)) 
    cur.execute(command_db)
    
    #Add url to links table
    command_db = '''INSERT OR IGNORE INTO links_visited (links)
    VALUES
    ('''+"'"+url+"')"
    cur.execute(command_db)
    conn.commit()
    conn.close()
    
def save_urls_tovisit(urls):
    '''
    Saves urls_tovisit to the database.
    '''
    try:
        conn = sqlite3.connect('wikiDump.sqlite')
        cur = conn.cursor()
    except:
        print "Could not connect to database"
        return None   
    try:
        for item in urls:
            command_db = '''INSERT OR IGNORE INTO links_tovisit (links)
            VALUES
            ('''+"'"+item.get_url()+"')"
            cur.execute(command_db)
    except:
        print "Error saving visited links"
        return None
    finally:
        conn.commit()
        conn.close()
        return None
    
url2 = "https://en.wikipedia.org/robots.txt"
def load_tovisit_URLS():
    start_urls = list()
    try:    
        conn = sqlite3.connect('wikiDump.sqlite')
        cur = conn.cursor()
        command = '''SELECT links FROM links_tovisit'''
        cur.execute(command)
        result = cur.fetchall()
        for item in result:
            start_urls.append(link(item[0]))
        conn.close()
    except:   
        start_urls = [link("https://en.wikipedia.org/wiki/Machine_learning")]
    finally:
        if len(start_urls) < 1:
            return [link("https://en.wikipedia.org/wiki/Machine_learning")]
        else:
            return start_urls
#start_url = link("https://en.wikipedia.org/wiki/Pedro_Domingos")
    
def load_visited_URLS():
    start_urls = list()
    try:    
        conn = sqlite3.connect('wikiDump.sqlite')
        cur = conn.cursor()
        command = '''SELECT links FROM links_visited'''
        cur.execute(command)
        result = cur.fetchall()
        for item in result:
            start_urls.append(link(item[0]))
        
    except:   
        return start_urls
    finally:
        conn.close()
        return start_urls

def getResult(n_pages=10):
    #initializeDB()
    #asd
    
    urls_tovisit = load_tovisit_URLS()
    urls_visited = load_visited_URLS()
    
    start_url = urls_tovisit[0]
    print start_url
    html = urllib.urlopen(start_url.get_url()).read()
    soup = BeautifulSoup(html)             
    
    start_url.set_title(soup.title.string)
    #urls_tovisit = [start_url]
    
    #while len(urls_tovisit) != 0:
    t0 = time.time()
    for i in range(n_pages):
        try:
            if len(urls_tovisit) == 0: break
            time.sleep(0.2)
            
            current_url = urls_tovisit[0]
            print(str(i)+"/10000 "+"Searching "+str(current_url.get_short_url()))
            
            html = urllib.urlopen(current_url.get_url()).read()
            soup = BeautifulSoup(html)
            current_url.set_title(soup.title.string)
            
            #Move the stack with URLs
            urls_tovisit = urls_tovisit[1:]
            urls_visited.append(current_url)
            
            #Get the feature vector from the text
            vect = get_featureVector(soup)
            
            '''Calculates if given page is relevant enough - 
                if it has less than 12 keywords in total 
                it is not added to database and links
                found on that page are skipped'''
            relevancy = 0
            for item in vect:
                try: relevancy += int(vect[item])
                except: continue
                      
            if relevancy < 12: continue    
            
            #Save features vector to database
            savetoDB(vect,current_url.get_short_url())
            
            #Get next links
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
            
            
        except: break
    save_urls_tovisit(urls_tovisit)    
    t = time.time()-t0
    log = '''Crawling finished.\n
    Visited pages: (%s)
    Relevant pages: (%s)
    Time: (%s)s''' % (i, len(urls_visited),t)    
    sendLog(log)
    #print log
   
def sendLog(log,email="pythontry123@gmail.com"):
    msg = MIMEText(log)
    msg['Subject'] = log.split()[1]
    msg['From'] = email
    msg['To'] = email
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com',587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(email, "uvtrmduitgywrtsq")
        smtpObj.sendmail(email, [email], msg.as_string())
        print("Log sent successfully")
    except:
        print("Error: unable to send log")
    finally:
        smtpObj.quit()


        
