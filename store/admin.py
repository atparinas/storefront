from django.contrib import admin
from django.contrib.admin.decorators import action
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse


from tags.models import TaggedItem


from . import models

class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    prepopulated_fields = {
        'slug': ['title'] 
    }
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    list_display = ['title', 'price', 'inventory_status', 'collection_title']
    list_editable = ['price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']


    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        
        return 'OK'

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products successfully updated'
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'payment_status', 'placed_at']
    inlines = [OrderItemInline]
    list_editable = ['payment_status']
    list_per_page = 10
    list_select_related = ['customer']

    @admin.display(ordering='customer')
    def customer_name(self, order):
        return f'{order.customer.first_name} {order.customer.last_name}'

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    #Eager Load when Listing
    list_select_related = ['user']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'products_count']
    search_fields = ['title']


    @admin.display(ordering='products_count')
    def products_count(self, collection):

        # app_model_page
        url = (
            reverse('admin:store_product_changelist') +
            '?' +
            urlencode({
                'collection__id' : str(collection.id)
            })

        ) 
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

        # return collection.products_count

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )
