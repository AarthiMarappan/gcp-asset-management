from rest_framework import serializers
from asset.models import Asset
import os
from asset_management import settings
from google.cloud import storage
import datetime

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'fileType', 'fileName')
        extra_kwargs = {
            'fileName': {'read_only': True},
        }

    def to_representation(self, instance):
        response = super().to_representation(instance)
        storageClient = storage.Client.from_service_account_json(
            settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        bucket = storageClient.bucket(settings.BUCKET_NAME)
        if response['id'] is not None and response['fileName'] is not None:
            blob = bucket.blob(os.path.join(
                str(response['id']),
                response['fileName']
            ))
            response['url'] = blob.generate_signed_url(
                version = 'v4',
                expiration = datetime.timedelta(minutes = 15),
                method = 'GET'
            )

        # response['url'] = os.path.join(settings.MEDIA_ROOT, str(response['id']))
        return response
