from rest_framework import serializers
from decimal import Decimal

from store.models import Product, Collection, Review


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













    # def create(self, validated_data):
    #     # **validated_data means upack the dictionary
    #     product = Product(**validated_data)
    #     # Perform other operations here if any
    #     product.save()
    #     return product

    # def update(self, instance, validated_data):
    #     instance.price = validated_data.get('price')
    #     instance.save()
    #     return instance

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2)
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#     collection = CollectionSerializer()

#     def calculate_tax(self, product: Product):
#         return product.price * Decimal(1.1)


