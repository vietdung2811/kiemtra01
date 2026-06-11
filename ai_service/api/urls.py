from django.urls import path
from .views import RecommendView, TrackView, GraphRecommendView, ChatView

urlpatterns = [
    path('recommend/', RecommendView.as_view(), name='recommend'),
    path('graph-recommend/', GraphRecommendView.as_view(), name='graph-recommend'),
    path('track-view/', TrackView.as_view(), name='track-view'),
    path('chat/', ChatView.as_view(), name='chat'),
]
