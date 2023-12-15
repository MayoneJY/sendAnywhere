from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import File
from .forms import FileForm
from .security import encrypt_file, decrypt_file
from .memory_file import create_in_memory_file
import random
import string

def index(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if 'inputReceive' in request.POST:
            # file_password와 일치하는 파일이 있으면 다운로드
            file_password = request.POST['inputReceive']
            file = File.objects.filter(file_password=file_password)
            if file.exists():
                file = file.first()
                decrypted_data = decrypt_file(file.file.read())
                response = HttpResponse(decrypted_data, content_type='application/force-download')
                response['Content-Disposition'] = 'attachment; filename=%s' % file.file.name
                return response
            else:
                return render(request, 'sendFiles/index.html', {'form': form, 'error_message': '파일이 존재하지 않습니다.'})
        elif form.is_valid():
            file_instance = form.save(commit=False)
            
            # 암호화된 파일 처리
            uploaded_file = request.FILES['file']
            encrypted_data = encrypt_file(uploaded_file.read())

            # In-Memory 파일 생성
            in_memory_file = create_in_memory_file(encrypted_data, uploaded_file.name)

            # FileField에 In-Memory 파일 할당
            file_instance.file.save(uploaded_file.name, in_memory_file, save=True)

            
            # 랜덤 문자 6자리 생성
            file_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            # 비밀번호 중복 확인
            while File.objects.filter(file_password=file_password).exists():
                file_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            file_instance.file_password = file_password
            file_instance.save()
            return render(request, 'sendFiles/success.html',{'file_password': file_password})
        else:
            return HttpResponse('Invalid Form')
    else:
        form = FileForm()
    return render(request, 'sendFiles/index.html', {'form': form})
# Create your views here.
