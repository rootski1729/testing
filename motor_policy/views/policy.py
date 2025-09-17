from bson import ObjectId
import requests
from motor_quote.enums import TaskStatus
from core.views import PermissionScopedViewSet
from motor_quote.models import MotorQuoteRequest
from permission.enums import Module
from motor_policy.serializers import (
    MotorPolicySerializer,
    MotorPolicyResponseSerializer,
    PolicyBulkUploadResponseSerializer,
    PolicyBulkUploadSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from motor_policy.models import MotorPolicy
from core.database import mongodb
from core.serializers import LimitOffsetSerializer
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction
from motor_quote.utils import QuoteRequestUtils
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from core.views import module_permission
from permission.enums import Operation
from motor_policy.serializers import (
    PolicyUploadSerializer,
    PolicyListResponseSerializer,
    ZipUploadSerializer,
    ZipUploadResponseSerializer,
    ZipUploadErrorResponseSerializer,
    MotorPolicyResponseSerializer,
)
from utils.nanoid_utils import default_nanoid
from utils import aws_utils
from utils.policy_processing_client import policy_processing_service
from django.conf import settings
from plugin.services.policy_extraction import (
    policy_extraction,
    PolicyExtractionResponse,
    PolicyExtractionRequest,
    PolicyExtractionObject,
)
from datetime import datetime
from django.db.models import Min, Max
from rest_framework.permissions import IsAuthenticated
from motor_quote.enums import PluginStatus
from .mixins import S3UploadMixin, FileProcessingMixin, PolicyExportMixin, FileAccessMixin
from authentication.serializers import NanoUserSerializer
from core.views import FilteringMixin
from core.filtering import FieldInfo, FieldTypes

class MotorPolicyViewSet(
    PermissionScopedViewSet, S3UploadMixin, FileProcessingMixin, PolicyExportMixin, FileAccessMixin, FilteringMixin
):
    queryset = MotorPolicy.objects.all()
    modules = [Module.MOTOR_POLICY]
    lookup_field = "uid"
    filter_fields = {
        "created_by_email": FieldInfo(filter="created_by__email", name="Created By (Email)", type=FieldTypes.STRING, choices=None),
        "created_by_first_name": FieldInfo(filter="created_by__first_name", name="Created By (First Name)", type=FieldTypes.STRING, choices=None),
        "created_by_last_name": FieldInfo(filter="created_by__last_name", name="Created By (Last Name)", type=FieldTypes.STRING, choices=None),
        "created_by_phone_number": FieldInfo(filter="created_by__phone_number", name="Created By (Phone Number)", type=FieldTypes.STRING, choices=None),
        "relationship_managers_email": FieldInfo(filter="created_by__posp_profile__relationship_managers__email", name="Relationship Manager (Email)", type=FieldTypes.STRING, choices=None),
    }

    @module_permission(op=Operation.READ)
    def __get_list_response(self, request, queryset, next, previous):
        mongo_ids = [req.mongo_id for req in queryset]
        # Fetch matching MongoDB docs (query does not guarantee order when using $in).
        object_ids = [ObjectId(mongo_id) for mongo_id in mongo_ids if mongo_id]
        with mongodb.motor_policy.find(
            {"_id": {"$in": object_ids}},
        ) as cursor:
            motor_policy_docs = cursor.to_list()

        # Map docs by their string _id so we can reorder them to match the Django queryset
        details_map = {str(doc["_id"]): doc for doc in motor_policy_docs}

        # Preserve the ordering from the Django queryset (so ordering by created_at is respected)
        ordered_details = [details_map.get(req.mongo_id) for req in queryset]

        response_serializer = PolicyListResponseSerializer(
            data={
                "next": next,
                "previous": previous,
            },
            context={
                "request": request,
                "results": queryset,
                "details": ordered_details,
            },
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    list_response_method = __get_list_response

    @action(
        detail=False,
        methods=["get"],
        url_path="filters/aggregated",
        permission_classes=[IsAuthenticated],
    )
    def aggregated_policy_filters(self, request):
        # Get unique values for each filter field
        insurer = MotorPolicy.objects.values_list("insurer", flat=True).distinct()
        product = MotorPolicy.objects.values_list("product", flat=True).distinct()
        product_type = MotorPolicy.objects.values_list(
            "product_type", flat=True
        ).distinct()
        product_sub_type = MotorPolicy.objects.values_list(
            "product_sub_type", flat=True
        ).distinct()
        product_category = MotorPolicy.objects.values_list(
            "product_category", flat=True
        ).distinct()
        policy_category = MotorPolicy.objects.values_list(
            "policy_category", flat=True
        ).distinct()
        policy_type = MotorPolicy.objects.values_list(
            "policy_type", flat=True
        ).distinct()
        issue_date_range = MotorPolicy.objects.aggregate(
            min=Min("issue_date"), max=Max("issue_date")
        )
        created_at_range = (
            MotorPolicy.objects.aggregate(min=Min("created_at"), max=Max("created_at"))
            if hasattr(MotorPolicy, "created_at")
            else None
        )

        return Response(
            {
                "insurer": list(insurer),
                "product": list(product),
                "product_type": list(product_type),
                "product_sub_type": list(product_sub_type),
                "product_category": list(product_category),
                "policy_category": list(policy_category),
                "policy_type": list(policy_type),
                "issue_date_range": issue_date_range,
                "created_at_range": created_at_range,
            }
        )

    @swagger_auto_schema(
        operation_summary="List all quote requests",
        operation_description="Retrieve a list of all quote requests.",
        query_serializer=LimitOffsetSerializer,
        responses={200: PolicyListResponseSerializer},
    )
    @module_permission(op=Operation.READ)
    def list(self, request, *args, **kwargs):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = self.get_queryset().order_by("-created_at")

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
        operation_summary="Submit policy extraction",
        operation_description=(
            "Returns a presigned URL for uploading a document directly to S3. "
        ),
        request_body=PolicyUploadSerializer,
        responses={200: MotorPolicyResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="upload-policy")
    @module_permission(op=Operation.CREATE)
    def upload_policy(self, request, *args, **kwargs):
        serializer = PolicyUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_url = serializer.validated_data["url"]
        file_name = serializer.validated_data.get("file_name")

        # Fetch the file bytes using AWS utils (object was uploaded via presigned URL)
        try:
            file_bytes, content_type = aws_utils.get_object_bytes_from_url(file_url)
            if not content_type:
                content_type = "application/pdf"
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch file from S3: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = PolicyExtractionRequest(file=("policy.pdf", file_bytes, content_type))
        plugin_result: PolicyExtractionResponse = policy_extraction.run(
            request, payload
        )

        if not getattr(plugin_result, "is_success", False):
            return Response(
                {"detail": getattr(plugin_result, "message", "Extraction failed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize extracted policy data
        extracted = plugin_result.response
        plugin_serializer = MotorPolicySerializer(data=extracted.model_dump())
        plugin_serializer.is_valid(raise_exception=True)

        user = request.user
        access_data = {
            "company": user.company,
            "access_location": user.location,
            "access_department": user.department,
            "access_level": user.role.access_level,
        }

        now = datetime.now()

        inserted_doc = mongodb._insert_one(
            mongodb.motor_policy,
            {
                "meta": {
                    "file_url": file_url,
                    "file_name": file_name,
                    **{
                        f"{k}": v.uid if hasattr(v, "uid") else v
                        for k, v in access_data.items()
                    },  # access_level does not have uid
                    "created_by": NanoUserSerializer(user).data,
                    "owners": [user.uid],
                    "created_at": now,
                    "updated_at": now,
                    "status": PluginStatus.COMPLETED,
                },
                "details": plugin_serializer.data,
            },
        )

        with transaction.atomic():
            motor_policy = MotorPolicy.objects.create(
                mongo_id=str(inserted_doc.inserted_id),
                name=f"Policy {plugin_serializer.data.get('policy_number', 'Unknown')}",
                description=f"Uploaded policy {plugin_serializer.data.get('policy_number', 'Unknown')}",
                insurer=extracted.insurer,
                product=extracted.product,
                product_type=extracted.product_type,
                product_sub_type=extracted.product_sub_type,
                product_category=extracted.product_category,
                policy_category=extracted.policy_category,
                policy_type=extracted.policy_type,
                issue_date=extracted.issue_date,
                created_by = user,
                **access_data,
            )
            motor_policy.owners.set([request.user])
            motor_policy.save()

        # add uid to inserted_doc
        mongodb.motor_policy.update_one(
            {"_id": ObjectId(inserted_doc.inserted_id)},
            {"$set": {"uid": str(motor_policy.uid)}},
        )

        return Response(plugin_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific quote request",
        operation_description="Retrieve a specific quote request by its ID.",
        responses={200: MotorPolicyResponseSerializer, 404: "Not Found"},
    )
    @module_permission(op=Operation.READ)
    def retrieve(self, request, *args, **kwargs):
        try:
            # TODO: Replace self.get_object() when self.get_object() is used
            instance = MotorPolicy.objects.get(uid=kwargs["uid"])
        except MotorPolicy.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        motor_policy_doc = mongodb.motor_policy.find_one({"uid": instance.uid})
        if not motor_policy_doc:
            return Response(
                {"detail": "UID NOT FOUND"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = MotorPolicyResponseSerializer(data=motor_policy_doc)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a specific policy",
        operation_description="Delete a specific policy by its ID.",
        responses={200: MotorPolicyResponseSerializer, 404: "Not Found"},
    )
    @module_permission(op=Operation.DELETE)
    def destroy(self, request, *args, **kwargs):
        try:
            # Fetch policy from Postgres
            instance = MotorPolicy.objects.get(uid=kwargs["uid"])
        except MotorPolicy.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        # Delete from MongoDB
        motor_policy_doc = mongodb.motor_policy.find_one_and_delete(
            {"uid": instance.uid}
        )
        if not motor_policy_doc:
            return Response(
                {"detail": "UID NOT FOUND"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete from Postgres
        instance.delete()

        # Return deleted document (serialized)
        serializer = MotorPolicyResponseSerializer(data=motor_policy_doc)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": f"{instance.name} deleted successfully"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Update an existing policy",
        operation_description="Update the details of an existing policy.",
        request_body=MotorPolicyResponseSerializer,
        responses={200: MotorPolicyResponseSerializer, 400: "Bad Request"},
    )
    @module_permission(op=Operation.UPDATE)
    def partial_update(self, request, *args, **kwargs):
        try:
            # Fetch policy from Postgres
            instance = MotorPolicy.objects.get(uid=kwargs["uid"])
        except MotorPolicy.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the incoming data
        serializer = MotorPolicyResponseSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update the MongoDB document
        motor_policy_doc = mongodb.motor_policy.find_one({"uid": instance.uid})
        if not motor_policy_doc:
            return Response(
                {"detail": "UID NOT FOUND"}, status=status.HTTP_404_NOT_FOUND
            )

        # Update the MongoDB document with the validated data
        update_data = serializer.data

        mongodb.motor_policy.update_one({"uid": instance.uid}, {"$set": update_data})

        model_fields = ["name", "description"]
        model_update_data = {k: v for k, v in update_data.items() if k in model_fields}

        if model_update_data:
            for field, value in model_update_data.items():
                setattr(instance, field, value)
            instance.save()

        # Return the updated data
        updated_doc = mongodb.motor_policy.find_one({"uid": instance.uid})
        response_serializer = MotorPolicyResponseSerializer(data=updated_doc)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Register uploaded bulk policy files",
        operation_description="Takes uploaded file URLs and creates MongoDB + RDS entries (unprocessed). Triggers external worker.",
        request_body=PolicyBulkUploadSerializer,
        responses={200: PolicyBulkUploadResponseSerializer},
    )
    @module_permission(op=Operation.CREATE)
    @action(detail=False, methods=["post"], url_path="bulk-policy-upload")
    def bulk_policy_upload(self, request, *args, **kwargs):
        serializer = PolicyBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = request.user.company
        files = serializer.validated_data["files"]

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        jwt_token = (
            auth_header.replace("Bearer ", "")
            if auth_header.startswith("Bearer ")
            else None
        )

        results = []

        for file_entry in files:
            file_url = file_entry["url"]
            file_name = file_entry.get("file_name") or f"{default_nanoid()}"
            file_name = file_name + f"__{default_nanoid()}"

            mongo_doc = {
                "meta": {
                    "file_url": file_url,
                    "file_name": file_name,
                    "company_id": company.uid if company else None,
                    "uploaded_by": request.user.uid,
                    "status": PluginStatus.PENDING,
                },
                "details": None,
            }

            inserted = mongodb._insert_one(mongodb.motor_policy, mongo_doc)
            inserted_id = inserted.inserted_id

            try:
                with transaction.atomic():
                    motor_policy = MotorPolicy.objects.create(
                        mongo_id=str(inserted_id),
                        name=f"Policy pending {file_name}",
                        description=f"Pending processing for {file_name}",
                        company=company,
                        access_location=request.user.location,
                        access_department=request.user.department,
                        access_level=request.user.role.access_level,
                    )
                    motor_policy.owners.set([request.user])
                    motor_policy.save()
            except Exception as exc:
                mongodb.motor_policy.update_one(
                    {"_id": ObjectId(inserted_id)},
                    {"$set": {"meta.rds_create_error": str(exc)}},
                )
                motor_policy = None

            if motor_policy:
                mongodb.motor_policy.update_one(
                    {"_id": ObjectId(inserted_id)},
                    {"$set": {"uid": str(motor_policy.uid)}},
                )

            results.append(
                {
                    "file_url": file_url,
                    "file_name": file_name,
                    "mongo_id": str(inserted_id),
                    "rds_uid": str(motor_policy.uid) if motor_policy else None,
                    "status": "PENDING",
                }
            )

        # Start company processing (only sends company_id)
        policy_processing_service.start_company_processing(
            company_id=str(company.uid), jwt_token=jwt_token
        )

        response = PolicyBulkUploadResponseSerializer({"files": results})
        return Response(response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Upload ZIP file containing multiple policies",
        operation_description="Upload a ZIP file and extract individual policy files for processing",
        request_body=ZipUploadSerializer,
        responses={
            200: ZipUploadResponseSerializer,
            400: ZipUploadErrorResponseSerializer,
            502: ZipUploadErrorResponseSerializer,
        },
    )
    @module_permission(op=Operation.CREATE)
    @action(detail=False, methods=["post"], url_path="zip-policy-upload")
    def zip_policy_upload(self, request, *args, **kwargs):
        serializer = ZipUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_url = serializer.validated_data["url"]
        file_name = serializer.validated_data.get("file_name")

        try:
            presigned_url = aws_utils.get_presigned_url_from_s3_url(file_url)

        except Exception as e:
            return Response(
                {
                    "detail": f"Failed to generate presigned URL: {str(e)}",
                    "error_code": "PRESIGNED_URL_ERROR",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        jwt_token = (
            auth_header.replace("Bearer ", "")
            if auth_header.startswith("Bearer ")
            else None
        )

        job_id = f"zip_{default_nanoid()}"

        try:
            lambda_result = aws_utils.call_zip_processing_lambda(
                presigned_url, jwt_token, "ProcessZipPolicies", job_id
            )

            if lambda_result["success"]:
                return Response(
                    {
                        "message": "ZIP processing started successfully",
                        "status": "PROCESSING",
                        "job_id": job_id,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )  # 202 = Accepted for processing
            else:
                return Response(
                    {
                        "detail": f"Failed to start ZIP processing: {lambda_result['error']}",
                        "error_code": "LAMBDA_START_ERROR",
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        except Exception as e:
            return Response(
                {
                    "detail": f"ZIP processing service unavailable: {str(e)}",
                    "error_code": "SERVICE_UNAVAILABLE",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

    # Additional endpoint to check job status
    @action(detail=False, methods=["get"], url_path="zip-status")
    def zip_processing_status(self, request, job_id=None, *args, **kwargs):
        if not job_id:
            return Response(
                {"detail": "job_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "job_id": job_id,
                "status": "PROCESSING",  # PROCESSING, COMPLETED, FAILED
                "progress": "Extracting files from ZIP...",
            }
        )
