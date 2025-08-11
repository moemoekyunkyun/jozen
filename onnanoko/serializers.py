from rest_framework import serializers
from .models import Series, Group, Tag, Character, Image

class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ['id', 'name', 'slug', 'description']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'slug', 'description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CharacterSerializer(serializers.ModelSerializer):
    series = SeriesSerializer(read_only=True)
    series_id = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), source='series', write_only=True, required=False, allow_null=True)
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, source='groups', write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tags', write_only=True, required=False)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id', 'name', 'slug', 'birth_date', 'age', 'height_cm', 'weight_kg',
            'bust_cm', 'waist_cm', 'hips_cm', 'is_2d', 'series', 'series_id',
            'groups', 'group_ids', 'tags', 'tag_ids', 'description',
            'primary_image', 'primary_image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'primary_image_url']

    def get_primary_image_url(self, obj):
        if obj.primary_image:
            request = self.context.get('request')
            url = obj.primary_image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

class ImageSerializer(serializers.ModelSerializer):
    uploader = serializers.StringRelatedField(read_only=True)
    characters = CharacterSerializer(many=True, read_only=True)
    character_ids = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all(), many=True, source='characters', write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tags', write_only=True, required=False)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            'id', 'file', 'file_url', 'uploader', 'uploaded_at',
            'characters', 'character_ids', 'tags', 'tag_ids',
            'width', 'height', 'is_approved', 'description'
        ]
        read_only_fields = ['uploader', 'uploaded_at', 'width', 'height', 'is_approved', 'file_url']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            url = obj.file.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
