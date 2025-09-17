from bson import ObjectId
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from utils import aws_utils
from utils.nanoid_utils import default_nanoid
from core.database import mongodb
from motor_quote.enums import PluginStatus
from core.views import module_permission
from permission.enums import Operation
from motor_policy.serializers import (
    PolicyPresignedURLRequestSerializer,
    PolicyPresignedURLResponseSerializer,
    BulkPolicyPresignedURLRequestSerializer,
    BulkPolicyPresignedURLResponseSerializer,
    PolicyExportSerializer,
    PolicyExportResponseSerializer,
    ZipUploadSerializer,
    ZipUploadResponseSerializer,
    ZipUploadErrorResponseSerializer,
    FileAccessRequestSerializer,
    FileAccessResponseSerializer,
)
from plugin.services.policy_extraction import PolicyExtractionObject
from motor_policy.models import MotorPolicy


class S3UploadMixin:
    @swagger_auto_schema(
        operation_summary="Generate presigned S3 upload URL for document",
        operation_description=(
            "Returns a presigned URL for uploading a document directly to S3. "
        ),
        request_body=PolicyPresignedURLRequestSerializer,
        responses={200: PolicyPresignedURLResponseSerializer},
    )
    @module_permission(op=Operation.CREATE)
    @action(detail=False, methods=["post"], url_path="policy-presigned-url")
    def policy_presigned_url(self, request, *args, **kwargs):
        serializer = PolicyPresignedURLRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = request.user.company
        ext = serializer.get_extension()
        if not ext:
            raise ValueError("Got None as extension")

        key = f'policy-docs/{company.uid}/{serializer.data["file_name"]}__{default_nanoid()}.{ext}'

        upload_url, file_url = aws_utils.get_upload_presigned_url(
            bucket_name=settings.COMPANY_S3_BUCKET,
            object_key=key,
            content_type=serializer.validated_data["content_type"],
            max_size=10 * 1024 * 1024,  # 10 MB
            expiration=3600,
        )

        serializer = PolicyPresignedURLResponseSerializer(
            {"upload_url": upload_url, "file_url": file_url}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Generate bulk presigned S3 upload URLs for documents",
        operation_description="Returns multiple presigned URLs for uploading documents directly to S3.",
        request_body=BulkPolicyPresignedURLRequestSerializer,
        responses={200: BulkPolicyPresignedURLResponseSerializer},
    )
    @module_permission(op=Operation.CREATE)
    @action(detail=False, methods=["post"], url_path="bulk-policy-presigned-url")
    def bulk_policy_presigned_url(self, request, *args, **kwargs):
        serializer = BulkPolicyPresignedURLRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = request.user.company

        files_out = []
        for f in serializer.validated_data["files"]:
            file_name = f["file_name"]
            content_type = f["content_type"]
            ext = content_type.split("/")[-1]
            file_name = file_name + f"__{default_nanoid()}"
            key = f"policy-docs/{company.uid}/{file_name}.{ext}"

            upload_url, file_url = aws_utils.get_upload_presigned_url(
                bucket_name=settings.COMPANY_S3_BUCKET,
                object_key=key,
                content_type=content_type,
                max_size=10 * 1024 * 1024,
                expiration=3600,
            )

            files_out.append(
                {"file_name": file_name, "upload_url": upload_url, "file_url": file_url}
            )

        response = BulkPolicyPresignedURLResponseSerializer({"files": files_out})
        return Response(response.data, status=status.HTTP_200_OK)


class FileProcessingMixin:
    @action(detail=False, methods=["get"], url_path="next-pending-file")
    @permission_classes([AllowAny])
    def next_pending_file(self, request, *args, **kwargs):
        """Get next pending file for a company"""
        company_id = request.query_params.get("company_id")

        if not company_id:
            return Response(
                {"detail": "company_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        pending_file = mongodb.motor_policy.find_one(
            {
                "meta.company_id": company_id,
                "meta.status": PluginStatus.PENDING.value,
                "meta.processing": {"$ne": True}
            }
        )

        if not pending_file:
            return Response(
                {"detail": "No more files to process"}, status=status.HTTP_404_NOT_FOUND
            )

        mongodb.motor_policy.update_one(
            {"_id": pending_file["_id"]}, {"$set": {"meta.processing": True}}
        )

        presigned_url = aws_utils.get_presigned_url_from_s3_url(
            pending_file["meta"]["file_url"]
        )

        return Response(
            {
                "mongo_id": str(pending_file["_id"]),
                "file_url": presigned_url,
                "file_name": pending_file["meta"]["file_name"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-file-status")
    @permission_classes([AllowAny])
    def update_file_status(self, request, *args, **kwargs):
        """Update file processing status"""
        mongo_id = request.data.get("mongo_id")
        success = request.data.get("success")
        extracted_data = request.data.get("extracted_data")
        error = request.data.get("error")


        if not mongo_id:
            return Response(
                {"detail": "mongo_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if success and extracted_data:
            response = PolicyExtractionObject(**extracted_data)
            mongo_update = {
                "meta.status": PluginStatus.COMPLETED,
                "meta.processing": False,
                "details": extracted_data,
            }
            mongo_update.update(extracted_data)
            

            mongodb.motor_policy.update_one(
                {"_id": ObjectId(mongo_id)}, {"$set": mongo_update}
            )

            # Update RDS
            try:
                motor_policy = MotorPolicy.objects.get(mongo_id=mongo_id)
                policy_number = response.policy_number or "Unknown"
                motor_policy.name = f"Policy {policy_number}"
                motor_policy.description = f"Processed policy {policy_number}"

                motor_policy.insurer = response.insurer
                motor_policy.product = response.product
                motor_policy.product_type = response.product_type
                motor_policy.product_sub_type = response.product_sub_type
                motor_policy.product_category = response.product_category
                motor_policy.policy_category = response.policy_category
                motor_policy.policy_type = response.policy_type
                motor_policy.issue_date = response.issue_date

                motor_policy.save()
            except MotorPolicy.DoesNotExist:
                pass

        else:
            mongodb.motor_policy.update_one(
                {"_id": ObjectId(mongo_id)},
                {
                    "$set": {
                        "meta.status": PluginStatus.FAILED,
                        "meta.processing": False,

                    }
                },
            )

        return Response({"status": "updated"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="extraction-callback")
    @permission_classes([AllowAny])
    def extraction_callback(self, request, *args, **kwargs):
        """Legacy callback - kept for compatibility"""
        return self.update_file_status(request, *args, **kwargs)


class PolicyExportMixin:
    @swagger_auto_schema(
        operation_summary="Export policies with filters",
        operation_description="Export policies with optional filters for insurer, product, product_type, product_sub_type, product_category, policy_category, policy_type, issue_date, created_at_from, created_at_to, posp, rm, posp_city, and posp_state",
        request_body=PolicyExportSerializer,
        responses={200: PolicyExportResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="export")
    @module_permission(op=Operation.READ)
    def export(self, request, *args, **kwargs):
        serializer = PolicyExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Start with base queryset
        queryset = self.get_queryset()

        # Apply filters based on provided data
        filters = {}

        if serializer.validated_data.get("insurer"):
            filters["insurer"] = serializer.validated_data["insurer"]

        if serializer.validated_data.get("product"):
            filters["product"] = serializer.validated_data["product"]

        if serializer.validated_data.get("product_type"):
            filters["product_type"] = serializer.validated_data["product_type"]

        if serializer.validated_data.get("product_sub_type"):
            filters["product_sub_type"] = serializer.validated_data["product_sub_type"]

        if serializer.validated_data.get("product_category"):
            filters["product_category"] = serializer.validated_data["product_category"]

        if serializer.validated_data.get("policy_category"):
            filters["policy_category"] = serializer.validated_data["policy_category"]

        if serializer.validated_data.get("policy_type"):
            filters["policy_type"] = serializer.validated_data["policy_type"]

        if serializer.validated_data.get("issue_date"):
            filters["issue_date"] = serializer.validated_data["issue_date"]

        if serializer.validated_data.get("issue_date_from"):
            filters["issue_date__gte"] = serializer.validated_data["issue_date_from"]

        if serializer.validated_data.get("issue_date_to"):
            filters["issue_date__lte"] = serializer.validated_data["issue_date_to"]

        if serializer.validated_data.get("created_at_from"):
            filters["created_at__gte"] = serializer.validated_data["created_at_from"]

        if serializer.validated_data.get("created_at_to"):
            filters["created_at__lte"] = serializer.validated_data["created_at_to"]

        if serializer.validated_data.get("posp"):
            # Filter by POSP in owners field
            posp_user = serializer.validated_data["posp"]
            queryset = queryset.filter(owners=posp_user)

        if serializer.validated_data.get("rm"):
            # Get all POSPs related to this RM and filter by them in owners
            rm_user = serializer.validated_data["rm"]
            # Get all POSP profiles where this RM is the relationship manager
            posp_profiles = rm_user.posp_relationships.all()
            # Get the user IDs from these POSP profiles
            posp_user_ids = [profile.user.id for profile in posp_profiles]
            # Filter policies by these POSP users in owners
            queryset = queryset.filter(owners__id__in=posp_user_ids)

        if serializer.validated_data.get("posp_city"):
            # Filter by POSP city (current address city)
            posp_city = serializer.validated_data["posp_city"]
            # Filter policies by POSP users with matching current city
            queryset = queryset.filter(
                owners__posp_profile__details__curr_city__icontains=posp_city
            )

        if serializer.validated_data.get("posp_state"):
            # Filter by POSP state (current address state)
            posp_state = serializer.validated_data["posp_state"]
            # Filter policies by POSP users with matching current state
            queryset = queryset.filter(
                owners__posp_profile__details__curr_state=posp_state
            )

        # Apply filters to queryset
        if filters:
            queryset = queryset.filter(**filters)

        # Order by created_at descending
        queryset = queryset.order_by("-created_at")

        # Get MongoDB documents for the filtered queryset
        mongo_ids = [policy.mongo_id for policy in queryset]

        with mongodb.motor_policy.find(
            {"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}},
        ) as cursor:
            motor_policy_docs = cursor.to_list()

        # Create response with filtered data
        response_serializer = PolicyExportResponseSerializer(
            data={
                "count": queryset.count(),
                "results": motor_policy_docs,
            },
            context={
                "request": request,
                "results": motor_policy_docs,
            },
        )
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class FileAccessMixin:
    @swagger_auto_schema(
        operation_summary="Get presigned URL for file access",
        operation_description="Convert a file URL to a presigned URL for secure access",
        request_body=FileAccessRequestSerializer,
        responses={200: FileAccessResponseSerializer},
    )
    @module_permission(op=Operation.READ)
    @action(detail=False, methods=["post"], url_path="file-access")
    def get_file_access_url(self, request, *args, **kwargs):
        serializer = FileAccessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_url = serializer.validated_data["file_url"]
        
        try:
            presigned_url = aws_utils.get_presigned_url_from_s3_url(file_url)
            expiration = 3600  # 1 hour expiration
            
            response_serializer = FileAccessResponseSerializer({
                "presigned_url": presigned_url,
                "expiration": expiration
            })
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as exc:
            return Response(
                {"detail": f"Failed to generate presigned URL: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

