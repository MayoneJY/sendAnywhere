from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import File
from .forms import FileForm
from .security import encrypt_file, decrypt_file, generate_sha256_hash
from .memory_file import create_in_memory_file
import random
import string
import urllib

def safe_file_name(file_name):
    # URL 인코딩을 사용하여 비-ASCII 문자를 처리
    return urllib.parse.quote(file_name)

def index(request):
    if request.method == 'POST':
        if 'file_user_password' in request.POST:
            file_token = request.POST['file_token']
            file_user_password = request.POST['file_user_password']
            passwordCheck = request.POST['passwordCheck']
            reload_check = False
            if passwordCheck != file_user_password:
                reload_check = True
            
            # file_token과 일치하는 데이터가 있으면 비밀번호 저장
            file = File.objects.filter(file_token=file_token)
            if file.exists():
                file = file.first()
                if(file_user_password == ''):
                    file.file_user_password = None
                else:
                    file.file_user_password = generate_sha256_hash(file_user_password)
                file.save()
                
            return render(request, 'sendFiles/success.html',{'file_token': file_token, 'file_user_password': file_user_password, 'reload_check': reload_check})
        elif 'file_check_password' in request.POST:
            file_token = request.POST['file_token']
            file_check_password = request.POST['file_check_password']
            file = File.objects.filter(file_token=file_token)
            
            if file.exists():
                file = file.first()
                if file.file_user_password == generate_sha256_hash(file_check_password):
                    decrypted_data = decrypt_file(file.file.read())
                    response = HttpResponse(decrypted_data, content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(safe_file_name(file.file.name.split('/')[-1]))
                    return response
                else:
                    return render(request, 'sendFiles/password_check.html', {'file_token': file_token, 'error_message': '비밀번호가 일치하지 않습니다.'})
            else:
                return render(request, 'sendFiles/index.html', {'file_token': file_token, 'error_message': '파일이 존재하지 않습니다.'})
        else:
            form = FileForm(request.POST, request.FILES)
            
            if 'inputReceive' in request.POST:
                # file_token과 일치하는 파일이 있으면 다운로드
                file_token = request.POST['inputReceive']
                file = File.objects.filter(file_token=file_token)
                
                if file.exists():
                    file = file.first()
                    if(file.file_user_password != None):
                        return render(request, 'sendFiles/password_check.html', {'file_token': file_token})
                    decrypted_data = decrypt_file(file.file.read())
                    response = HttpResponse(decrypted_data, content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(safe_file_name(file.file.name.split('/')[-1]))
                    print(file.file.name.split('/')[-1])
                    
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
