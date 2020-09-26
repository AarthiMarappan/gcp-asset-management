from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
import sys
from api_base.PostResponse import PostResponse
from api_base.PutResponse import PutResponse
from api_base.GetResponse import GetResponse
from api_base.DeleteResponse import DeleteResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from api_base.BadDataErrorResponse import BadDataErrorResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api_base.FormValidationErrorException import FormValidationErrorException
from api_base.EntityNotFoundResponse import EntityNotFoundResponse
from api_base.SystemErrorResponse import SystemErrorResponse
from api_base.response import Response
from django.db.models import F

class ApiBase(APIView):

    def markAsDeleted(self, model):
        if model.status:
            model.status = 0
        model.save()
        return model
    
    def handleEntitySave(self, serializer):
        serializer.save()
        return serializer

    def handleEntityDelete(self, model):
        if model.status:
            model.status = 0
        model.save()
        return model

    def generatePostSuccessResponse(self, model):
        response = PostResponse(model.data)
        return response.formatResponse()

    def generatePutSuccessResponse(self, model):
        response = PutResponse(model.data)
        return response.formatResponse()

    def generateDeleteSuccessResponse(self):
        response = DeleteResponse()
        return response.formatResponse()

    def generateGetSuccessResponse(self, model):
        response = GetResponse(model.data)
        return response.formatResponse()

    def generateResponse(self, data):
        response = Response(data = data, statusCode = 200, errors = None )
        return response.formatResponse()

    def validateEntityAuthority(self, model, data):
        try:
            model.objects.get(id = data)
            return model
        except Exception as e:
            return e
        
    def handleFormSubmission(self, serializer, request_data):
        form_data = serializer(data = request_data)
        if form_data.is_valid():
            serializer.save()
            return form_data
        raise ValidationError
            
    def generateFormErrorResponse(self, model):
        response = BadDataErrorResponse(
            errors = FormValidationErrorException.formErrorResponseFormat(model)
        )
        return response.formatResponse()

    def generateBadDataErrorResponse(self, error):
        response = BadDataErrorResponse(errors = error)
        return response.formatResponse()
        
    def handleException(self, e):
        if isinstance(e, ValidationError):
            response = BadDataErrorResponse(errors = e)
            return response.formatResponse() 
        if isinstance(e, ObjectDoesNotExist):
            return EntityNotFoundResponse.generateEntityNotFound()
        return SystemErrorResponse.generateSystemErrorResponse()

    def formatResponse(self, data):
        response_data = {
            'data': data
        }
        return JsonResponse(response_data, status = status.HTTP_200_OK)

    @classmethod
    def list(cls, request, queryset, serializer, key, orderBy = None, status = None):
        result = {}
        final_result = {}
        page_size = int(request.GET.get('page_size', 10))
        page = request.GET.get('page', 1)
        if status:
            queryset = queryset.filter(status = 1)
        if orderBy:
            queryset = queryset.order_by(orderBy)
        paginator = cls.get_pagination(queryset, page, page_size)
        serializer_value = serializer(paginator['value'], many=True)
        result.update([
            ('page' , paginator['page']),
            ('totalPageCount', paginator['paginator_value'].num_pages),
            ('totalCount', paginator['paginator_value'].count),
            ('pageSize', page_size),
            (key , serializer_value.data)
        ])
        final_result['data'] = result
        return JsonResponse(final_result, safe = False)

    @classmethod
    def get_pagination(cls, queryset, page, page_size):
        paginator = Paginator(queryset, page_size)
        data = {}
        data['paginator_value'] = paginator
        try:
            data.update([
                ('value', paginator.page(page)), ('page', page)
            ])
        except PageNotAnInteger:
            data.update([
                ('value', paginator.page(1)), ('page', 1)
            ])
        except EmptyPage:
            data.update([
                ('value', paginator.page(paginator.num_pages)), ('page', paginator.num_pages)
            ])
        return data