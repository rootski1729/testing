from bson import ObjectId
from motor_quote.enums import TaskStatus
from core.views import PermissionScopedViewSet, module_permission, AsyncPermissionScopedViewSet
from motor_quote.models import MotorQuoteRequest
from permission.enums import Module, Operation
from motor_quote.serializers import (
    MotorQuoteRequestCreateSerializer,
    MotorQuoteRequestBasicSerializer,
    MotorQuoteRequestListResponseSerializer,
    MotorQuoteRequestRecordingRequestSerializer,
    MotorQuoteRequestRecordingResponseSerializer,
    MotorQuoteRequestRetrieveSerializer,
    MotorQuoteRequestValidationResponseSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from motor_quote.models import MotorQuoteRequest
from core.database import mongodb
from motor_quote.utils import AevisUtils
from core.serializers import LimitOffsetSerializer
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction
from motor_quote.utils import QuoteRequestUtils
from rest_framework.decorators import action


class MotorQuoteRequestViewSet(PermissionScopedViewSet):
    queryset = MotorQuoteRequest.objects.all()
    modules = [Module.MOTOR_QUOTE]
    lookup_field = "uid"

    def __get_list_response(self, request, queryset, next, previous):
        mongo_ids = [req.mongo_id for req in queryset]

        with mongodb.quote_tasks.find(
            {"request_id": {"$in": mongo_ids}},
            {"_id": 0, "request_id": 1, "id": 1, "status": 1, "insurer": 1},
        ) as cursor:
            tasks_docs = cursor.to_list()

        with mongodb.quote_req.find(
            {"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}},
            QuoteRequestUtils.get_basic_details_projection(),
        ) as cursor:
            req_docs = cursor.to_list()

        _task_docs_map = {}
        for doc in tasks_docs:
            if doc["request_id"] in _task_docs_map:
                _task_docs_map[doc["request_id"]].append(doc)
            else:
                _task_docs_map[doc["request_id"]] = [doc]

        _details_map = {str(doc["_id"]): doc for doc in req_docs}

        response_serializer = MotorQuoteRequestListResponseSerializer(
            data={
                "next": next,
                "previous": previous,
            },
            context={
                "request": request,
                "results": queryset,
                "tasks": _task_docs_map,
                "details": _details_map,
            },
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="List all quote requests",
        operation_description="Retrieve a list of all quote requests.",
        query_serializer=LimitOffsetSerializer,
        responses={200: MotorQuoteRequestListResponseSerializer},
    )
    @module_permission(op=Operation.READ)
    def list(self, request, *args, **kwargs):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = self.get_queryset().filter(company=request.user.company).order_by(
            "-created_at"
        )

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        if paginated_queryset is None:
            next_link = None
            prev_link = None
            results = queryset
        else:
            next_link = paginator.get_next_link()
            prev_link = paginator.get_previous_link()
            results = paginated_queryset

        return self.__get_list_response(
            request,
            results,
            next_link,
            prev_link,
        )

    @swagger_auto_schema(
        operation_summary="Create a new quote request",
        operation_description="Create a new quote request with the provided data.",
        request_body=MotorQuoteRequestCreateSerializer,
        responses={201: MotorQuoteRequestBasicSerializer},
    )
    @module_permission(op=Operation.CREATE)
    def create(self, request, *args, **kwargs):
        serializer = MotorQuoteRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inserted_doc = mongodb._insert_one(mongodb.quote_req, serializer.data)
        company, access_location, access_department, access_level = (
            request.user.company,
            request.user.location,
            request.user.department,
            request.user.role.access_level,
        )
        with transaction.atomic():
            quote_req = MotorQuoteRequest.objects.create(
                mongo_id=str(inserted_doc.inserted_id),
                name=serializer.data["name"],
                description=serializer.data["description"],
                company=company,
                access_location=access_location,
                access_department=access_department,
                access_level=access_level,
            )
            quote_req.owners.set([request.user])

            task_ids = AevisUtils.create_quote_task(quote_req, serializer)
            quote_req.tasks = task_ids
            quote_req.save()

        response_serializer = MotorQuoteRequestBasicSerializer(quote_req)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_summary="Retrieve a specific quote request",
        operation_description="Retrieve a specific quote request by its ID.",
        responses={200: MotorQuoteRequestRetrieveSerializer, 404: "Not Found"},
    )
    @module_permission(op=Operation.READ)
    def retrieve(self, request, *args, **kwargs):

        try:
            # TODO: Replace self.get_object() when self.get_object() is used
            instance = MotorQuoteRequest.objects.get(uid=kwargs["uid"])
        except MotorQuoteRequest.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        for task in instance.tasks:
            QuoteRequestUtils.update_task_status(task)

        quote_req_doc = mongodb.quote_req.find_one({"_id": ObjectId(instance.mongo_id)})
        with mongodb.quote_tasks.find(
            {"id": {"$in": instance.tasks}},
            {
                "_id": 0,
                "id": 1,
                "status": 1,
                "insurer": 1,
                "quote_status": 1,
                "created_at": 1,
                "updated_at": 1,
            },
        ) as cursor:
            task_docs = cursor.to_list()
        serializer = MotorQuoteRequestRetrieveSerializer(
            data={
                "insurers": quote_req_doc["insurers"],
                "details": quote_req_doc["details"],
                "tasks": task_docs,
            },
            context={"instance": instance},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Call status for quote tasks",
        operation_description="Trigger a status check for all ongoing quote tasks.",
        responses={200: MotorQuoteRequestListResponseSerializer},
    )
    @action(methods=["post"], detail=False, url_path="call-status")
    @module_permission(op=Operation.READ)
    def call_status(self, request, *args, **kwargs):
        with mongodb.quote_tasks.find(
            {"status": {"$nin": [TaskStatus.COMPLETED, TaskStatus.FAILED]}},
            {
                "_id": 0,
                "id": 1,
                "request_id": 1,
                "status": 1,
            },
        ) as cursor:
            task_docs = cursor.to_list()

        for task in task_docs:
            QuoteRequestUtils.update_task_status(task["id"])

        queryset = list(
            MotorQuoteRequest.objects.filter(
                mongo_id__in=[task["request_id"] for task in task_docs]
            )
        )
        return self.__get_list_response(request, queryset, None, None)

    @swagger_auto_schema(
        operation_summary="Get Recording of the Quote Request Execution",
        operation_description="Retrieve the recording of the quote request execution.",
        query_serializer=MotorQuoteRequestRecordingRequestSerializer,
        responses={
            200: MotorQuoteRequestRecordingResponseSerializer,
            404: "Not Found",
            503: "Service Unavailable",
        },
    )
    @action(methods=["get"], detail=True, url_path="recording")
    @module_permission(op=Operation.READ)
    def recording(self, request, *args, **kwargs):
        serializer = MotorQuoteRequestRecordingRequestSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        try:
            # TODO: Replace self.get_object() when self.get_object() is used
            instance = MotorQuoteRequest.objects.get(uid=kwargs["uid"])
        except MotorQuoteRequest.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        with mongodb.quote_tasks.find(
            {"id": {"$in": instance.tasks}},
            {
                "_id": 0,
                "id": 1,
                "insurer": 1,
            },
        ) as cursor:
            task_docs = cursor.to_list()

        insurer_task = None
        for task in task_docs:
            if task["insurer"] == serializer.data["insurer"]:
                insurer_task = task
                break

        if not insurer_task:
            return Response(
                {"detail": "Insurer not found for the quote request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recording_response = QuoteRequestUtils.get_recording(insurer_task["id"])
        if not recording_response:
            return Response(
                {
                    "detail": "Could not retrieve recording for the quote request at the moment"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response_serializer = MotorQuoteRequestRecordingResponseSerializer(
            data={
                "is_available": recording_response["is_available"],
                "recording_url": recording_response.get("recording_url", None),
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class AsyncMotorQuoteRequestViewSet(AsyncPermissionScopedViewSet):
    queryset = MotorQuoteRequest.objects.all()
    modules = [Module.MOTOR_QUOTE]
    lookup_field = "uid"

    @swagger_auto_schema(
        operation_summary="Validate a quote request",
        operation_description="Validate a quote request with the provided data.",
        request_body=MotorQuoteRequestCreateSerializer,
        responses={200: MotorQuoteRequestValidationResponseSerializer, 503: "Service Unavailable"},
    )
    @module_permission(op=Operation.CREATE)
    @action(methods=["post"], detail=False, url_path="validate")
    async def validate(self, request, *args, **kwargs):
        serializer = MotorQuoteRequestCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        success, validation_response = await AevisUtils.validate_quote_request(serializer)
        if not success:
            return Response(
                {"detail": "Could not validate quote request at the moment"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        
        response_serializer = MotorQuoteRequestValidationResponseSerializer(
            data=validation_response
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
