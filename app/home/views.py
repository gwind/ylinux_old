# coding: utf-8

from forms import ContactForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

def index(request):
    return render_to_response('home/index.html',{'title':"首页",},
                              context_instance=RequestContext(request))

def about(request):
    return render_to_response('home/about.html',{'title':"关于",},
                              context_instance=RequestContext(request))

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = ['ylinux.admin@gmail.com','lijian.gnu@gmail.com',]
            recipients.append(sender)

            from django.core.mail import send_mail
            send_mail (subject,message,sender,recipients)
            return render_to_response('home/thanks.html',{'title':"感谢",},
                                      context_instance=RequestContext(request))
            #return HttpResponseRedirect('/thanks/')
    else:
        form = ContactForm()

        return render_to_response('home/contact.html',
                                  {'title':"联系",'form':form,},
                                  context_instance=RequestContext(request))

#def thanks(request):
#    return render_to_response('home/thanks.html',{'title':"感谢",},
#                              context_instance=RequestContext(request))

def coding(request):
    return render_to_response('home/coding.html',{'title':"Coding 之中",},
                              context_instance=RequestContext(request))
