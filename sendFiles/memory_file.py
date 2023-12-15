from django.core.files.base import ContentFile

def create_in_memory_file(encrypted_data, name):
    return ContentFile(encrypted_data, name=name)
