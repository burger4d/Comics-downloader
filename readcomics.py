import requests
import os
from fuzzywuzzy import process


url="https://readcomicsonline.ru/comic-list"
r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
List = str(r.content)
n=List.find(".jpg")-50
print(List[n:n+54])
List=List[List.find('<a href="https://readcomicsonline.ru/comic-list/tag'):List.find('<div class="text-version-sidebar" style="display: none;">')]

comics = []
urls = {}

while 1:
    url=List[List.find("https"):List.find('">')]
    if not "https" in url:
        break
    else:
        List=List[List.find('">')+2:]
        title=List[:List.find("<")]
        comics.append(title)
        urls[title]=url

def download_image(url, name):
    r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    with open(name+".jpg", "wb") as file:
        file.write(r.content)
        file.close()
    print("ok")

def search(name):
    global urls, comics, results, List2
    url="https://readcomicsonline.ru/comic-list"
    results=[]
    for result in process.extract(name, comics, limit=20):
        results.append(result[0])
    r=requests.get(urls[results[0]])
    List2=str(r.content)
    List2=List2[List2.find("/comic/")+10:]
    comics=[]
    while 1:
        List2=List2[List2.find('"chart-title"><strong>')+22:]
        title=List2[:List2.find("</strong>")]
        List2=List2[List2.find("<a href"):]
        urls[title]=url
        List2=List2[List2.find("https://readcomicsonline.ru/comic/"):]
        url=List2[:List2.find('">')]
        if "https://readcomicsonline.ru/comic/" in url:
            print(title)
            comics.append(title)
            urls[title]=url
        else:
            break


def comicschoice(n):
    global url2, title, minititle
    title=comics[n]
    title.replace(":","")
    print(title)
    os.makedirs(title, exist_ok=True)
    url=urls[title]
    url2=url[url.find("comic/")+6:]
    issues=int(url2[url2.find("/")+1:])
    url2=url[:-len("/"+str(issues))]
    minititle=url2[url2.find("comic/")+6:]
    print(minititle)
    print(url2)

def chapterschoice(first, last):
    for issue in range(first, last+1):
        url3=url2+"/"+str(issue)
        r=requests.get(url3)
        content=str(r.content)
        for i in range(1, 100):
            integer=str(i)
            if len(integer)==1:
                integer="0"+integer
            url4="https://readcomicsonline.ru/uploads/manga/"+minititle+"/chapters/"+str(issue)+"/"+integer+".jpg"
            if url4 in content:
                download_image(url4, title+"/"+title+"_"+str(issue)+"_"+str(i))
            else:
                break

if __name__ == "__main__":
    name = input("name:")
    search(name)
    n=int(input("which one?:"))
    comicschoice(n)
    chapterschoice(int(input("first:")), int(input("last:")))
