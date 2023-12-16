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
        if 'file_user_password' in request.POST:
            file_token = request.POST['file_token']
            file_user_password = request.POST['file_user_password']
            passwordCheck = request.POST['passwordCheck']
            reload_check = False
            if passwordCheck != file_user_password:
                reload_check = True
                
            # 비밀번호가 입력되지 않았으면 다시 로드
            if file_user_password == '':
                return render(request, 'sendFiles/success.html',{'file_token': file_token, 'reload_check': reload_check})
            
            # file_token과 일치하는 데이터가 있으면 비밀번호 저장
            file = File.objects.filter(file_token=file_token)
            if file.exists():
                file = file.first()
                file.file_user_password = file_user_password
                file.save()
                
            return render(request, 'sendFiles/success.html',{'file_token': file_token, 'file_user_password': file_user_password, 'reload_check': reload_check})
        else:
            form = FileForm(request.POST, request.FILES)
            
            if 'inputReceive' in request.POST:
                # file_token과 일치하는 파일이 있으면 다운로드
                file_token = request.POST['inputReceive']
                file = File.objects.filter(file_token=file_token)
                
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
                file_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                # 비밀번호 중복 확인
                while File.objects.filter(file_token=file_token).exists():
                    file_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                file_instance.file_token = file_token
                file_instance.save()
                return render(request, 'sendFiles/success.html',{'file_token': file_token})
            else:
                return HttpResponse('Invalid Form')
    else:
        form = FileForm()
    return render(request, 'sendFiles/index.html', {'form': form})
# Create your views here.
