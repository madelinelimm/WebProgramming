from logging import PlaceHolder
from django.shortcuts import render, redirect
import random
import markdown
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    getentries = util.get_entry(title)
    if getentries != None:
        getentries = markdown.markdown(getentries) 

    return render(request, "encyclopedia/entry.html", {
        "getentries": getentries,
        "entrytitle" : title
    })

def searchpage(request):
    query = request.GET.get('q').strip()
    return render(request, "encyclopedia/searchpage.html", {
        "searchpage": util.search(query),
        "query" : query
    })


def newpage(request):
    error_msg = None
    if request.method == "POST":
        newpagetitle = request.POST.get('newpagetitle').strip()
        newpageedit = request.POST.get('newpageedit').strip()
        if util.get_entry(newpagetitle) :
            error_msg = "Error: Encyclopedia entry already exist, please provide another title!"
            return render(request, "encyclopedia/newpage.html", {"error" : error_msg})
        # check for invalid form
        elif newpagetitle == "": 
            error_msg = "Error: Could not save empty encyclopedia title!"
            return render(request, "encyclopedia/newpage.html", {"error" : error_msg})
        else:
            util.save_entry(newpagetitle, newpageedit)
            return redirect("entry", title = newpagetitle)   
    else:     
        return render(request, "encyclopedia/newpage.html", { "error" : error_msg})


def editpage(request, title):
    if request.method == "POST":
        newpageedit = request.POST.get('newpageedit').strip()
        util.save_entry(title, newpageedit)
        return redirect("entry", title = title)
    else:
        entrypage = util.get_entry(title)
        return render(request, "encyclopedia/editpage.html", {
                        "title" : title,
                        "entrypage" : entrypage
                        })

                        
def randompage(request):
    cur_list = util.list_entries()
    random_entry = random.randint(1, len(cur_list))
    random_entry_title = cur_list[random_entry - 1]
    getentries = util.get_entry(random_entry_title)
    return render(request, "encyclopedia/entry.html", {
        "getentries": markdown.markdown(getentries),
        "entrytitle" : random_entry_title
    })
