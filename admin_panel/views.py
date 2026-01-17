from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from products.models import Product
from orders.models import Order
from accounts.models import User
from brands.models import Brand
from orders.models import OrderItem
from django.db.models import Sum, Count
from .serializers import AdminUserSerializer,ProductReadSerializer,ProductWriteSerializer,AdminOrderSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from admin_panel.pagination import UserPagination,AdminOrderPagination
from products.views import ProductPagination
from django.db.models import Q
from django.db.models.functions import TruncMonth

class AdminDashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Basic stats
        total_products = Product.objects.count()
        total_users = User.objects.count()
        total_orders = Order.objects.count()

        total_revenue = (
            Order.objects
            .filter(status__in=["paid", "delivered"])
            .aggregate(total=Sum("total_amount"))["total"]
            or 0
        )

        # Cart items count
        total_cart_items = (
            User.objects
            .annotate(cart_count=Count("cart_items"))
            .aggregate(total=Sum("cart_count"))["total"] or 0
        )

        # Brand product count
        brand_counts = (
            Brand.objects
            .annotate(count=Count("products"))
            .values("name", "count")
        )

        # Stock distribution
        stock_data = (
            Product.objects
            .values("name")
            .annotate(value=Sum("stock"))
        )

        return Response({
            "stats": {
                "totalProducts": total_products,
                "totalUsers": total_users,
                "totalOrders": total_orders,
                "totalCartItems": total_cart_items,
                "totalRevenue": total_revenue,
            },
            "brandCounts": list(brand_counts),
            "stockData": list(stock_data),
        })

# Piechart
class StockSummaryAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        in_stock = Product.objects.filter(stock__gt=0).count()
        out_of_stock = Product.objects.filter(stock__lte=0).count()

        return Response({
            "in_stock": in_stock,
            "out_of_stock": out_of_stock
        })

#Brand Radar Chart
class BrandSalesAPIView(APIView):
    permission_classes = [IsAdminUser] 

    def get(self, request):
        data = (
            OrderItem.objects
            .values("product__brand__name")
            .annotate(sales=Sum("quantity"))
            .order_by("-sales")
        )

        result = [
            {
                "brand": item["product__brand__name"],
                "sales": item["sales"]
            }
            for item in data
        ]

        return Response(result)

#Brand Count Chart
class BrandProductCountAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            Product.objects
            .values("brand__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        result = [
            {
                "brand": item["brand__name"],
                "count": item["count"]
            }
            for item in data
        ]

        return Response(result)
    

class AdminRevenueAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = (
            Order.objects
            .filter(status__in=["paid", "delivered"])
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("total_amount"))
            .order_by("month")
        )

        data = []
        for item in queryset:
            data.append({
                "month": item["month"].strftime("%b"),
                "revenue": item["revenue"] or 0
            })

        return Response(data)


class AdminUserListAPIView(APIView):
    def get(self, request):
        search = request.query_params.get("search")
        role = request.query_params.get("role")

        # Ensure distinct=True in annotations to prevent result multiplication
        users_qs = User.objects.only(
            'id', 'full_name', 'email', 'role', 'is_active'
        ).annotate(
            cart_count=Count("cart_items", distinct=True),
            wishlist_count=Count("wishlist", distinct=True),
            orders_count=Count("orders", distinct=True),
        ).order_by('-created_at') # Always order for consistent pagination

        if search:
            users_qs = users_qs.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )

        if role and role != 'all':
            users_qs = users_qs.filter(role=role)

        stats = {
            "total_users": User.objects.count(),
            "total_admins": User.objects.filter(role="admin").count(),
            "total_active": User.objects.filter(is_active=True).count(),
            "total_blocked": User.objects.filter(is_active=False).count(),
        }

        paginator = UserPagination()
        page = paginator.paginate_queryset(users_qs, request)
        serializer = AdminUserSerializer(page, many=True)

        return Response({
            "count": users_qs.count(),
            "total_pages": paginator.page.paginator.num_pages,
            "current_page": paginator.page.number,
            "results": serializer.data,
            "stats": stats,
        })

    

#Toggle user
class ToggleBlockUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return Response({
            "id": user.id,
            "is_active": user.is_active
        })


#Product list
class ProductListCreateAPIView(APIView):

    def get(self, request):
        queryset = Product.objects.select_related("brand", "category")

        # 🔹 Brand filter
        brand = request.GET.get("brand")
        if brand:
            queryset = queryset.filter(brand__name__iexact=brand)

        # 🔹 Stock filter
        stock = request.GET.get("stock")
        if stock == "in":
            queryset = queryset.filter(stock__gt=0)
        elif stock == "out":
            queryset = queryset.filter(stock=0)

        # 🔹 Search filter
        search = request.GET.get("search", "").strip()
        if search:
            if search.isdigit():
                queryset = queryset.filter(id=int(search))
            else:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(brand__name__icontains=search) |
                    Q(category__title__icontains=search)
                )

        queryset = queryset.order_by("-id")  # stable pagination

        paginator = ProductPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProductReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductRetrieveUpdateDeleteAPIView(APIView):

    def get_object(self, pk):
        return get_object_or_404(
            Product.objects.select_related("brand", "category"),
            pk=pk
        )

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductReadSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductWriteSerializer(product, data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductReadSerializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = AdminOrderPagination

    def get(self, request):
        status = request.GET.get("status", "all")
        search = request.GET.get("search", "").strip()

        orders = (
            Order.objects
            .select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )


        # 🔹 Status filtering
        if status == "processing":
            orders = orders.filter(status__in=["confirmed", "paid"])
        elif status != "all":
            orders = orders.filter(status=status)


        # 🔹 Search filtering
        if search.isdigit():
            orders = orders.filter(id=int(search))
        else:
            orders = orders.filter(
                Q(user__full_name__icontains=search) |
                Q(user__email__icontains=search)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)

        serializer = AdminOrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    

class AdminOrderStatsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            "total_orders": Order.objects.count(),
            "processing": Order.objects.filter(
                status__in=["confirmed", "paid"]
            ).count(),
            "delivered": Order.objects.filter(status="delivered").count(),
            "cancelled": Order.objects.filter(status="cancelled").count(),
        })



class AdminOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        status = request.data.get("status")

        if status not in dict(Order._meta.get_field("status").choices):
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.status = status
        order.save()

        return Response({
            "success": True,
            "new_status": order.status
        })