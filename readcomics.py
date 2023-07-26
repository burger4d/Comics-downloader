import requests
import os
from fuzzywuzzy import process
from PIL import Image as IMAGE
import threading
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.image import Image, AsyncImage
from kivy.uix.slider import Slider
from kivy.clock import Clock

def init():
    global url, r, List, n, comics, urls, title
    url="https://readcomicsonline.ru/comic-list"
    r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    List = str(r.content)
    n=List.find(".jpg")-50
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
    #print("ok")

def search_thread(N):
    global urls, comics
    url="https://readcomicsonline.ru/comic-list"
    r=requests.get(urls[results[N]])
    print("get", urls[results[N]])
    List2=str(r.content)
    List2=List2[List2.find("/comic/")+10:]
    #comics=[]
    while 1:
        List2=List2[List2.find('"chart-title"><strong>')+22:]
        title=List2[:List2.find("</strong>")]
        List2=List2[List2.find("<a href"):]
        urls[title]=url
        List2=List2[List2.find("https://readcomicsonline.ru/comic/"):]
        url=List2[:List2.find('">')]
        begin="https://readcomicsonline.ru/uploads/manga/"
        if "https://readcomicsonline.ru/comic/" in url:
            title=title.replace(":","")
            s=""":*"\/?<>"""
            #print(title)
            for i in title:
                if i in s:
                    #print(i)
                    title=title.replace(i, "")
                #print(title)
            if title not in comics:
                comics.append(title)
            urls[title]=url
            url42 = url[::-1]
            url42 = url42[url42.find("/"):]
            url42 = url42[::-1]+"chapters/1/01.jpg"
            url42 = url42.replace("comic/", "uploads/manga/")
            images[title] = url42
        else:
            break

def search(name):
    global urls, comics, results, List2, images
    url="https://readcomicsonline.ru/comic-list"
    results=[]
    images = {}
    for result in process.extract(name, comics, limit=20):
        if result[1]>89:
            results.append(result[0])
            #print(result)
    #print(results)
    comics=[]
    threads=[]
    for N in range(len(results)):
        t=threading.Thread(target=search_thread, args=(N,))
        threads.append(t)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(comics)
    return comics

def comicschoice(n):
    global url2, title, minititle, issues
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


class MyApp(App):
    def build(self):
        self.comicnumber=0
        self.layout = GridLayout(cols=1,
                            row_force_default=True,
                            row_default_height=80,
                            spacing=50,
                            padding=20)
        self.lbl=Label(text="Download comics from the website readcomicsonline.ru")
        self.layout.add_widget(self.lbl)
        #self.image=Image(source="Cover.jpg", size_hint_y=350)
        try:
            init()
        except Exception as err:
            error=""
            err2=""
            for c in str(err):
                if c==" " and len(err2)>30:
                    error+=err2+"\n"
                    err2=""
                else:
                    err2+=c
            self.lbl2=Label(text=error, color=(1, 0, 0, 1), font_size=13)
            self.layout.add_widget(self.lbl2)
        else:
            self.comics = TextInput(text="deadpool", multiline=False)
            self.Submit = Button(text="search",
                            bold=True,
                            background_color=(1, 0, 0, 1),
                            pos_hint={"center_x":0.5, "center_y":0.5},
                            color=(1, 1, 1, 1),
                            on_press=self.submit)
            #self.layout.add_widget(self.image)
            self.layout.add_widget(self.comics)
            self.layout.add_widget(self.Submit)
        return self.layout
    
    def submit(self, obj):
        global comics
        self.layout.remove_widget(self.lbl)
        self.lbl=Label(text="Loading...")
        self.layout.add_widget(self.lbl)
        #self.layout.add_widget(self.image)
        comic=self.comics.text
        self.layout.remove_widget(self.comics)
        self.layout.remove_widget(self.Submit)
        self.layout.do_layout()
        self.orientation="horizontal"
        self.layout.row_force_default=False
        self.layout.col_force_default=False
        #self.layout.row_default_height=350
        #self.layout.col_default_width=250
        self.layout.spacing=0
        self.layout.padding=0
        print(comic)
        search(comic)
        threading.Thread(target=self.search_covers).start()
    def search_covers(self):
        global comics
        os.makedirs("covers", exist_ok=True)
        for com in comics:
            link=images[com]
            download_image(link, "covers/"+com)
            if os.path.getsize("covers/"+com+".jpg")<200:
                os.remove("covers/"+com+".jpg")
                comics.remove(com)
            else:
                image = IMAGE.open("covers/"+com+".jpg")
                image.save("covers/"+com+".jpg", optimize=True, quality=50)
        #self.layout.remove_widget(self.lbl)
        self.selectedcomic = comics[0]
        Clock.schedule_once(self.submit2)
    def submit2(self, obj):
        global comics
        self.layout.remove_widget(self.lbl)
        self.btn = Button(
                     size_hint_y=350,
                     background_normal="covers/"+self.selectedcomic+".jpg",
                     pos_hint={"center_x":0.5, "center_y":0.5},
                     on_press=self.select_comic)
        self.lbl = Label(text = comics[0])
        self.btn2 = Button(text=">>>>",
                     bold=True,
                     color=(0, 1, 0, 1),
                     pos_hint={"center_x":0.5, "center_y":0.9},
                     on_press=self.next_comic)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.lbl)
        self.layout.add_widget(self.btn2)
        
    def next_comic(self, obj):
        self.comicnumber+=1
        if self.comicnumber == len(comics):
            self.comicnumber = 0
        self.selectedcomic = comics[self.comicnumber]
        self.layout.remove_widget(self.btn)
        self.layout.remove_widget(self.lbl)
        self.layout.remove_widget(self.btn2)
        self.btn = Button(
                     size_hint_y=350,
                     background_normal="covers/"+comics[self.comicnumber]+".jpg",
                     pos_hint={"center_x":0.5, "center_y":0.5},
                     on_press=self.select_comic)
        btn2 = Button(text=">>>>",
                     bold=True,
                     color=(0, 1, 0, 1),
                     pos_hint={"center_x":0.5, "center_y":0.9},
                     on_press=self.next_comic)
        self.lbl = Label(text = comics[self.comicnumber])
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.lbl)
        self.layout.add_widget(self.btn2)
        
    def select_comic(self, obj):
        self.layout.remove_widget(self.btn)
        self.layout.remove_widget(self.btn2)
        self.img = Image(source="covers/"+self.selectedcomic+".jpg")
        comicschoice(self.comicnumber)
        self.first_issue = 1
        self.last_issue = issues
        self.lbl2 = Label(text="Last released issue: "+str(issues)+"\n(But it is possible that there are less issues)\nselect the wanted issues")
        self.btn = Button(text="Next step",
                          background_color=(1, 0, 0, 1),
                          color = (0, 1, 0, 1),
                          on_press = self.lastissue)
        
        self.slider = Slider(min=1, max=issues, value=1)
        self.slider.bind(value=self.slider_change)
        self.lblslide = Label(text="First issue: "+str(self.slider.value))

        
        self.layout.add_widget(self.img)
        self.layout.add_widget(self.lbl2)
        self.layout.add_widget(self.slider)
        self.layout.add_widget(self.lblslide)
        self.layout.add_widget(self.btn)
        print(self.selectedcomic)
        print(issues)

    def slider_change(self, obj, value):
        self.lblslide.text = "First issue: "+str(int(value))
        self.first_issue = int(value)

    def slider_change2(self, obj, value):
        self.lblslide.text = "Last issue: "+str(int(value))+"(first issue: "+str(self.first_issue)+")"
        self.last_issue = int(value)

    def lastissue(self, obj):
        self.layout.remove_widget(self.btn)
        self.layout.remove_widget(self.slider)
        self.layout.remove_widget(self.lblslide)
        self.slider = Slider(min=self.first_issue, max=issues, value=issues)
        self.slider.bind(value=self.slider_change2)
        self.lblslide = Label(text="Last issue: "+str(self.slider.value)+"(first issue: "+str(self.first_issue)+")")
        self.layout.add_widget(self.slider)
        self.layout.add_widget(self.lblslide)
        self.btn = Button(text="Download",
                          background_color=(0, 0, 1, 1),
                          color = (0, 1, 0, 1),
                          on_press = self.download)
        self.layout.add_widget(self.btn)
    def download(self, obj):
        self.layout.remove_widget(self.btn)
        self.layout.remove_widget(self.lbl)
        self.layout.remove_widget(self.slider)
        self.layout.remove_widget(self.lblslide)
        self.layout.remove_widget(self.img)
        self.layout.remove_widget(self.lbl2)
        self.lbl = Label(text="Downloading...")
        self.layout.add_widget(self.lbl)
        threading.Thread(target=self.execute_chapterschoice).start()
        #chapterschoice(self.first_issue, self.last_issue)
    def execute_chapterschoice(self):
        chapterschoice(self.first_issue, self.last_issue)
        Clock.schedule_once(self.task_finished)
    def task_finished(self, obj):
        self.layout.remove_widget(self.btn)
        self.layout.remove_widget(self.lbl)
        self.lbl = Label(text="Task finished")
        self.layout.add_widget(self.lbl)
MyApp().run()

