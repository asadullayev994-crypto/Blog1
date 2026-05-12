from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination 
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly 

class PostListAPIView(APIView):
   
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
       
        posts = Post.objects.all().order_by('-created_at')

       
        search_query = request.query_params.get('search', None)
        if search_query:
            posts = posts.filter(title__icontains=search_query) | posts.filter(body__icontains=search_query)

      
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(posts, request)
        
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

       
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
          
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
   
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, pk):
        try:
            obj = Post.objects.get(pk=pk)
            
            self.check_object_permissions(self.request, obj)
            return obj
        except Post.DoesNotExist:
            return None

    def get(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response({"error": "Post topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response({"error": "Post topilmadi"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response({"error": "Post topilmadi"}, status=status.HTTP_404_NOT_FOUND)
            
        post.delete()
        return Response({"message": "Post muvaffaqiyatli o'chirildi"}, status=status.HTTP_204_NO_CONTENT)