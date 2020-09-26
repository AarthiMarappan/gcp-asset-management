from asset.serializers import AssetSerializer
from asset.models import Asset
from asset.models import FileType
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from django.http import request
import sys
import os
from asset_management import settings
from django.core.files.storage import FileSystemStorage
from asset.models import MimeType
from api_base.views import ApiBase
import uuid
from google.cloud import storage
from asset.GCPS import GCPS
import datetime
from django.core.exceptions import ObjectDoesNotExist


class AssetView(ApiBase):

    @classmethod
    def create(self, request):
        try:
            type = FileType.objects.get(type = request.POST.get('fileType'))
            data = {
                'fileType': type.id
            }
            print('jiiiiiiiiiiiiiikklklklko')
            serializer = AssetSerializer(data = data)
            if serializer.is_valid():
                validatedData = self.validateFile(
                    self,
                    data['fileType'],
                    request.FILES.get('file')
                )
                if validatedData is not False:
                    return self.generateBadDataErrorResponse(self, validatedData)
                serializer.save()
                self.uploadFile(self, serializer.data['id'], request.FILES.get('file'))
                return self.generatePostSuccessResponse(self, serializer)
            return self.generateFormErrorResponse(self, serializer)
        except Exception as e:
            # return self.handleException(self, e)
            return JsonResponse(e, safe=False)
    
    @classmethod
    def get(self, request, id):
        try:
            asset = Asset.objects.get(id = id)
            serializer = AssetSerializer(asset)
            return self.generateGetSuccessResponse(self, serializer)
        except Exception as e:
            return JsonResponse(e, safe = False)
            # return self.handleException(self, e)

    def getUrlFromCloud(self, id):
        storageClient = storage.Client.from_service_account_json(
            settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        bucket = storageClient.get_bucket(settings.BUCKET_NAME)
        for blob in bucket.list_blobs(prefix = str(id)):
            return blob.generate_signed_url(
                version = 'v4',
                expiration = datetime.timedelta(minutes = 15),
                method = 'GET'
            )
        raise ObjectDoesNotExist()

    def uploadFile(self, id, file):
        asset = Asset.objects.get(id = id)
        # self.localStorage(self, id, file)
        self.cloudStorage(self, id, file)
        asset.fileName = file.name
        asset.save()
        return self

    def cloudStorage(self, id, file):
        storageClient = storage.Client.from_service_account_json(
            settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        bucket = storageClient.get_bucket(settings.BUCKET_NAME)
        if not bucket:
            bucket = GCPS.createBucket(storageClient, settings.BUCKET_NAME)
        
        blob = bucket.blob(os.path.join(str(id), file.name))
        blob.upload_from_file(file)
        return self
        
    def getFilePath(self, id):
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        filePath = os.path.join(settings.MEDIA_ROOT, str(id))
        os.mkdir(filePath)
        return filePath

    def localStorage(self, id, file):
        filePath = self.getFilePath(self, id)
        fileSystemStorage = FileSystemStorage(location = filePath)
        fileSystemStorage.save(file.name, file)
        return self
        
    def validateFileType(typeId, file):
        fileType = FileType.objects.get(id = typeId)
        mimeType = MimeType.objects.filter(fileType__id = fileType.id).filter(type = file.content_type)
        if mimeType.count() is 0:
            return True
        return False

    def validateFileSize(typeId, file):
        fileType = FileType.objects.get(id = typeId)
        if file.size >= (fileType.maximumSize * 1000000):
            return True
        return False

    def validateFile(self, typeId, file):
        if self.validateFileType(typeId, file):
            errors = {
                field : 'file',
                message : ["Uploaded file doesn't match given type"]
            }
            return errors
        elif self.validateFileSize(typeId, file):
            errors = {
                field : 'file',
                message : ['Uploaded file exceeds 10MB']
            }
            return errors
        return False