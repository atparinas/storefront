from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from store.models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review


class CollectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    
    products_count = serializers.ReadOnlyField()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory',  'price', 'price_with_tax', 'collection']
    
    # collection = CollectionSerializer()
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.price * Decimal(1.1)



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(
            product_id=product_id,
            **validated_data
        )

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    product_id = serializers.IntegerField()

    # validating individual fields follow this convention
    # valida_field_name
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No Product with given Id")
        
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        # need to use the self.instance to match the implementation of the save method
        # of the ModelSerializer
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

    user_id = serializers.IntegerField(read_only=True)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']

    product = SimpleProductSerializer()

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']

    items = OrderItemSerializer(many=True)

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No Cart with that Id")

        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The Cart is Empty')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            (customer, created) = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.price,
                    quantity = item.quantity
                ) for item in cart_items 
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order