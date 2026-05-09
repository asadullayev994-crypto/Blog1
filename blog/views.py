from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Post
from .serializers import PostSerializer
from .permission import IsAuthorOrReadOnly 

class PostListAPIView(APIView):
 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # Post yaratilayotganda muallifni avtomatik tokendan oladi
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
        return Response({"message": "Post o'chirildi"}, status=status.HTTP_204_NO_CONTENT)