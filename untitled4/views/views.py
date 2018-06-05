import base64

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render


video = None
tracker = None
track = False
currcamera = None
currtype = None


def getframe(request):
    import cv2
    global video, tracker, track, currtype, currcamera
    from django.http import HttpResponse
    if (video is None or not video.isOpened):
        return HttpResponse("Error1")
    try:
        ret, frame = video.read()
        if track:
            ok, bbox = tracker.update(frame)
            if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            else:
                cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),
                            2)
                if currtype is "2":
                    from untitled4.models import VideoNeighbours
                    from django.db.models import Q
                    camlist = VideoNeighbours.objects.filter(Q(video1_id=currcamera) | Q(video2_id=currcamera))
                    finlist = camlist.values_list('video1').union(camlist.values_list('video2')).distinct()
                    for i in finlist:
                        print(i[0])
                else:
                    from untitled4.models import Cameras
                    from untitled4.models import Neighbours
                    from django.db.models import Q
                    camlist = Neighbours.objects.filter(Q(camera1=Cameras.objects.filter(name=currcamera)[0]) | Q(
                        camera2=Cameras.objects.filter(name=currcamera)[0]))
                    finlist = camlist.values_list('camera1__name').union(camlist.values_list('camera2__name')).distinct()
                    if finlist.count() > 0:
                        count = 0
                        tomove = finlist[0][0]
                        count1 = 0
                        for i in finlist:
                            tempvideo = cv2.VideoCapture(getlink(name=i[0], type=currtype, user=request.user))
                            for j in range(0, 5):
                                tempret, tempframe = tempvideo.read()
                                tempok, tempbox = tracker.update(tempframe)
                                if tempok:
                                    count1 += 1
                            if count1 > count:
                                count = count1
                                tomove = i[0]
                        print(tomove)
                        if tomove != currcamera:
                            currcamera = tomove
                            video = cv2.VideoCapture(getlink(name=currcamera, type=currtype, user=request.user))
        cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        from PIL import Image
        jpeg = Image.fromarray(cv2_im)
        from io import BytesIO
        output = BytesIO()
        jpeg.save(output, "PNG")
        return HttpResponse(base64.b64encode(output.getvalue()))
    except Exception as e:
        print(str(e))
        return HttpResponse("Error")


def deleteobject(request):
    name = request.POST['name']
    ty = request.POST['type']
    global video, tracker, track
    if ty is "1":
        from untitled4.models import Cameras
        thumb = Cameras.objects.filter(name=name,userid=request.user)[0].thumbnail
        import os
        try:
            from untitled4.settings import BASE_DIR
            os.remove(os.path.join(BASE_DIR, "untitled4\\static\\", thumb))
        except:
            print("Not Found")
        Cameras.objects.filter(name=name, userid=request.user).delete()
        from untitled4.models import Neighbours
        Neighbours.objects.filter(camera1__name=name, camera1__userid=request.user).delete()
        Neighbours.objects.filter(camera2__name=name, camera2__userid=request.user).delete()
    else:
        from untitled4.models import Videos
        vidname = Videos.objects.filter(name=name, userid=request.user)[0].path
        thumbnail = Videos.objects.filter(name=name, userid=request.user)[0].thumbnail
        import os
        from untitled4.settings import BASE_DIR
        video = None
        tracker = None
        track = False
        try:
            os.remove(os.path.join(BASE_DIR, "untitled4\\static\\", thumbnail))
        except:
            print("Not Found")
        try:
            os.remove(vidname)
        except:
            print("Not Found")
        Videos.objects.filter(name=name, userid=request.user).delete()
        from untitled4.models import VideoNeighbours
        VideoNeighbours.objects.filter(video1_id=name, video1__userid=request.user).delete()
        VideoNeighbours.objects.filter(video2_id=name, video2__userid=request.user).delete()
    from django.http import HttpResponse
    return HttpResponse("Success")


def stoptracker(request):
    global track, tracker
    track = False
    tracker = None
    from django.http import HttpResponse
    return HttpResponse("Success")


def inittracker(request):
    import cv2
    global tracker, track
    track = True
    image = request.POST['image']
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    h = int(request.POST['h'])
    w = int(request.POST['w'])
    box = (x, y, w, h)
    image = image[22:]
    if (tracker is None):
        tracker = cv2.TrackerTLD_create()
    tracker.init(readb64(image), box)
    from django.http import HttpResponse
    return HttpResponse("Success")


def readb64(base64_string):
    import cv2
    from io import BytesIO
    sbuf = BytesIO()
    sbuf.write(base64.b64decode(base64_string))
    from PIL import Image
    pimg = Image.open(sbuf)
    import numpy as np
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


def getlink(name, user, type):
    if type is "1":
        from untitled4.models import Cameras
        camera = Cameras.objects.filter(userid=user, name=name)[0]
        username = camera.username
        password = camera.password
        ipaddr = camera.ipaddr
        print('rtsp://' + ipaddr + '/h264_ulaw.sdp')
        return 'http://' + ipaddr + '/video'
    from untitled4.models import Videos
    return Videos.objects.filter(userid=user, name=name)[0].path


def openvideo(request):
    import cv2
    name = request.POST['name']
    ty = request.POST['type']
    global video, currcamera, currtype
    currcamera = name
    currtype = ty
    if (video is None or not video.isOpened()):
        video = cv2.VideoCapture(getlink(name=name, user=request.user, type=ty))
    from django.http import HttpResponse
    return HttpResponse("Success")


def closevideo(request):
    global video
    if (video is not None and video.isOpened()):
        video.release()
        video = None
    from django.http import HttpResponse
    return HttpResponse("Success")


def index(request):
    from untitled4.models import Cameras
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'Home.html', {'user': user, 'cameras': Cameras.objects.filter(userid=user)})
        else:
            return render(request, 'Home.html',
                          {'error': "Invalid Username or Password", 'name': username, 'pass': password})
    if request.user.is_authenticated:
        return render(request, 'Home.html',
                      {'user': request.user, 'cameras': Cameras.objects.filter(userid=request.user)})
    else:
        return render(request, 'Home.html', {})


def camerabyname(request):
    name = request.POST['name']
    from untitled4.models import Cameras
    from django.http import HttpResponse
    objectQuerySet = Cameras.objects.filter(userid=request.user, name__contains=name)
    from django.core import serializers
    data = serializers.serialize('json', list(objectQuerySet), fields=('name'))
    return HttpResponse(data, content_type='application/json')


def videosbyname(request):
    name = request.POST['name']
    from untitled4.models import Videos
    from django.http import HttpResponse
    objectQuerySet = Videos.objects.filter(userid=request.user, name__contains=name)
    from django.core import serializers
    data = serializers.serialize('json', list(objectQuerySet))
    return HttpResponse(data, content_type='application/json')


def register(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return render(request, 'Register.html',
                          {'error': "Username Already Exists", 'name': username, 'pass': password, 'email': email})
        elif User.objects.filter(email=email).exists():
            return render(request, 'Register.html',
                          {'error': "Email Already Exists", 'name': username, 'pass': password, 'email': email})
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            from untitled4.models import Cameras
            return render(request, 'Home.html', {'user': user, 'cameras': Cameras.objects})
    elif request.user.is_authenticated:
        return index(request)
    else:
        return render(request, 'Register.html', {})


def logoff(request):
    logout(request)
    return render(request, 'Home.html', {})


def addCamera(request):
    import cv2
    if request.POST:
        name = request.POST['name']
        ipaddr = request.POST['ipaddr']
        username = request.POST['username']
        password = request.POST['password']
        neighbours = request.POST.getlist('neigh[]')
        th = cv2.VideoCapture('http://' + ipaddr + '/video')
        success, image = th.read()
        thumb = name + ".jpg"
        from untitled4.settings import BASE_DIR
        try:
            import os
            os.mkdir(os.path.join(BASE_DIR, "untitled4\\static\\cameras"))
        except:
            print("error")
        import os
        cv2.imwrite(os.path.join(BASE_DIR, "untitled4\\static\\cameras\\", thumb), image)
        user = request.user
        from untitled4.models import Cameras, Neighbours
        if Cameras.objects.filter(ipaddr=ipaddr, name=name).exists():
            return render(request, 'CameraAdd.html',
                          {'error': "Camera Already Exists", 'username': username, 'password': password, 'user': user
                              , 'ipaddr': ipaddr, 'name': name})
        else:
            Cameras.objects.create(name=name, ipaddr=ipaddr, username=username, password=password, userid=user, thumbnail="cameras\\" + thumb)
            for i in neighbours:
                Neighbours.objects.create(camera1=Cameras.objects.filter(name=name)[0],
                                          camera2=Cameras.objects.filter(name=i)[0])
            return render(request, 'Home.html', {'user': user, 'cameras': Cameras.objects.filter(userid=user)})
    elif request.user.is_authenticated:
        return render(request, 'CameraAdd.html', {})
    else:
        return render(request, 'Home.html', {})


def videosview(request):
    if request.user.is_authenticated:
        from untitled4.models import Videos
        return render(request, 'Videos.html',
                      {'user': request.user, 'videos': Videos.objects.filter(userid=request.user)})
    else:
        return render(request, 'Home.html', {})


def addVideos(request):
    import cv2
    global os
    if request.POST:
        name = request.POST['name']
        user = request.user
        ext = request.FILES['docfile'].name
        folder = 'videos/'
        uploaded_filename = name + ext[ext.find("."):]
        from untitled4.settings import BASE_DIR
        BASE_PATH = BASE_DIR
        try:
            import os
            os.mkdir(os.path.join(BASE_PATH, folder))
        except:
            print("error")
        full_filename = os.path.join(BASE_PATH, folder, uploaded_filename)
        fout = open(full_filename, 'wb+')
        from django.core.files.base import ContentFile
        file_content = ContentFile(request.FILES['docfile'].read())
        try:
            for chunk in file_content.chunks():
                fout.write(chunk)
            fout.close()
        except:
            return render(request, 'AddVideo.html',
                          {'error': "File Upload Error", 'user': user
                              , 'name': name})
        th = cv2.VideoCapture(full_filename)
        success, image = th.read()
        thumb = name + ".jpg"
        cv2.imwrite(os.path.join(BASE_PATH, "untitled4\\static\\", thumb), image)
        neighbours = request.POST.getlist('neigh[]')
        from untitled4.models import VideoNeighbours
        from untitled4.models import Videos
        if Videos.objects.filter(name=name).exists():
            return render(request, 'AddVideo.html',
                          {'error': "Video Already Exists", 'user': user
                              , 'name': name})
        else:
            Videos.objects.create(name=name, path=full_filename, userid=request.user, thumbnail=thumb)
            for i in neighbours:
                VideoNeighbours.objects.create(video1=Videos.objects.filter(name=name)[0],
                                               video2=Videos.objects.filter(name=i)[0])
            return render(request, 'Videos.html', {'user': user, 'videos': Videos.objects.filter(userid=user)})
    elif request.user.is_authenticated:
        return render(request, 'AddVideo.html', {})
    else:
        return render(request, 'Videos.html', {})