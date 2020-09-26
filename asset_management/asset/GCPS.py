from google.cloud import storage
from asset_management import settings

class GCPS():
    def createBucket(storageClient, bucketName):
        return storageClient.create_bucket(bucketName)