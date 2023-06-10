import requests
import os
from fuzzywuzzy import process


url="https://readcomicsonline.ru/comic-list"
r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
List = str(r.content)
List=List[List.find('<a href="https://readcomicsonline.ru/comic-list/tag'):List.find('<div class="text-version-sidebar" style="display: none;">')]

def download_image(url, name):
    r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    with open(name+".jpg", "wb") as file:
        file.write(r.content)
        file.close()
    print("ok")

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

name = input("name:")
results=[]
for result in process.extract(name, comics, limit=20):
    results.append(result[0])
#print(results)
#print(urls[results[0]])
r=requests.get(urls[results[0]])
List2=str(r.content)
List2=List2[List2.find("/comic/")+10:]

comics=[]
urls = {}

while 1:
    List2=List2[List2.find('"chart-title"><strong>')+22:]
    title=List2[:List2.find("</strong>")]
    List2=List2[List2.find("<a href"):]
    urls[title]=url
    List2=List2[List2.find("https://readcomicsonline.ru/comic/"):]
    url=List2[:List2.find('">')]
    if "https://readcomicsonline.ru/comic/" in url:
        print(title)
        #print(url)
        comics.append(title)
        urls[title]=url
    else:
        break

n=int(input("which one?:"))
title=comics[n]
print(title)
os.makedirs(title, exist_ok=True)
url=urls[title]
url2=url[url.find("comic/")+6:]
issues=int(url2[url2.find("/")+1:])
url2=url[:-len("/"+str(issues))]
minititle=url2[url2.find("comic/")+6:]
print(minititle)
print(url2)
first=int(input("first:"))
last=int(input("last:"))

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
