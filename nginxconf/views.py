from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def nginxconf(request,env):
    return render(request, 'nginxconf/nginxinfo.html')
