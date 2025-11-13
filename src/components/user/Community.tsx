import { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from '../ui/dialog';
import { Heart, MessageCircle, Share2, Plus, Flag, Loader2 } from 'lucide-react';
import { communityApi } from '../../services/api';
// 简单的时间格式化函数
const formatTime = (dateString: string) => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}天前`;
    if (hours > 0) return `${hours}小时前`;
    if (minutes > 0) return `${minutes}分钟前`;
    return '刚刚';
  } catch {
    return dateString;
  }
};

// 简单的toast实现
const useToast = () => {
  return {
    toast: (options: { title: string; description?: string; variant?: 'default' | 'destructive' }) => {
      console.log('Toast:', options.title, options.description);
      if (options.variant === 'destructive') {
        alert(`${options.title}: ${options.description || ''}`);
      }
    },
  };
};

interface Post {
  id: number;
  author_id: number;
  author_name: string;
  author_nickname?: string;
  author_role?: string;
  category: string;
  content: string;
  tags?: string;
  like_count: number;
  comment_count: number;
  is_liked: boolean;
  created_at: string;
}

interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  user_name: string;
  user_nickname?: string;
  content: string;
  like_count: number;
  is_liked: boolean;
  created_at: string;
}

export function Community() {
  const { toast } = useToast();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showPostDialog, setShowPostDialog] = useState(false);
  const [postCategory, setPostCategory] = useState('心情树洞');
  const [postContent, setPostContent] = useState('');
  const [postTags, setPostTags] = useState('');
  const [posting, setPosting] = useState(false);
  const [expandedPost, setExpandedPost] = useState<number | null>(null);
  const [comments, setComments] = useState<Record<number, Comment[]>>({});
  const [commentContent, setCommentContent] = useState<Record<number, string>>({});
  const [likingPosts, setLikingPosts] = useState<Set<number>>(new Set());
  const [reportingPosts, setReportingPosts] = useState<Set<number>>(new Set());

  // 获取帖子列表
  const fetchPosts = async (category?: string) => {
    try {
      setLoading(true);
      const categoryMap: Record<string, string> = {
        'all': '',
        'tree-hole': '心情树洞',
        'qa': '互助问答',
        'share': '经验分享',
      };
      const response = await communityApi.getPosts({
        category: categoryMap[category || 'all'] || undefined,
        limit: 50,
      });
      // API拦截器已经返回了data，response就是数组
      const postsData = Array.isArray(response) ? response : (Array.isArray(response?.data) ? response.data : []);
      setPosts(postsData);
    } catch (error: any) {
      console.error('获取帖子列表失败:', error);
      setPosts([]); // 确保posts始终是数组
      toast({
        title: '获取失败',
        description: error.response?.data?.detail || error?.detail || '无法加载帖子列表',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // 获取评论列表
  const fetchComments = async (postId: number) => {
    try {
      const response = await communityApi.getPostComments(postId);
      // API拦截器已经返回了data，response就是数组
      const commentsData = Array.isArray(response) ? response : (Array.isArray(response?.data) ? response.data : []);
      setComments(prev => ({ ...prev, [postId]: commentsData }));
    } catch (error: any) {
      console.error('获取评论失败:', error);
      setComments(prev => ({ ...prev, [postId]: [] })); // 确保comments始终是数组
    }
  };

  useEffect(() => {
    fetchPosts(selectedCategory);
  }, [selectedCategory]);

  // 发布帖子
  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postContent.trim()) {
      toast({
        title: '内容不能为空',
        variant: 'destructive',
      });
      return;
    }

    try {
      setPosting(true);
      const response = await communityApi.createPost({
        category: postCategory,
        content: postContent,
        tags: postTags || undefined,
      });
      
      toast({
        title: '发布成功',
        description: '您的帖子已成功发布',
      });
      
      setShowPostDialog(false);
      setPostContent('');
      setPostTags('');
      fetchPosts(selectedCategory);
    } catch (error: any) {
      console.error('发布帖子失败:', error);
      toast({
        title: '发布失败',
        description: error.response?.data?.detail || '无法发布帖子',
        variant: 'destructive',
      });
    } finally {
      setPosting(false);
    }
  };

  // 点赞/取消点赞
  const handleLikePost = async (postId: number) => {
    if (likingPosts.has(postId)) return;
    
    try {
      setLikingPosts(prev => new Set(prev).add(postId));
      const response = await communityApi.likePost(postId);
      // API拦截器已经返回了data，response就是数据对象
      const data = response?.data || response;
      
      setPosts(prev => prev.map(post => 
        post.id === postId 
          ? { ...post, like_count: data.like_count, is_liked: data.is_liked }
          : post
      ));
    } catch (error: any) {
      console.error('点赞失败:', error);
      toast({
        title: '操作失败',
        description: error.response?.data?.detail || '无法点赞',
        variant: 'destructive',
      });
    } finally {
      setLikingPosts(prev => {
        const newSet = new Set(prev);
        newSet.delete(postId);
        return newSet;
      });
    }
  };

  // 发布评论
  const handleCreateComment = async (postId: number) => {
    const content = commentContent[postId]?.trim();
    if (!content) {
      toast({
        title: '评论内容不能为空',
        variant: 'destructive',
      });
      return;
    }

    try {
      const response = await communityApi.createComment({
        post_id: postId,
        content: content,
      });
      // API拦截器已经返回了data，response就是数据对象
      const commentData = response?.data || response;
      
      setComments(prev => ({
        ...prev,
        [postId]: [...(prev[postId] || []), commentData],
      }));
      
      setCommentContent(prev => ({ ...prev, [postId]: '' }));
      setPosts(prev => prev.map(post => 
        post.id === postId 
          ? { ...post, comment_count: post.comment_count + 1 }
          : post
      ));
      
      toast({
        title: '评论成功',
        description: '您的评论已成功发布',
      });
    } catch (error: any) {
      console.error('发布评论失败:', error);
      toast({
        title: '评论失败',
        description: error.response?.data?.detail || '无法发布评论',
        variant: 'destructive',
      });
    }
  };

  // 展开/收起评论
  const toggleComments = (postId: number) => {
    if (expandedPost === postId) {
      setExpandedPost(null);
    } else {
      setExpandedPost(postId);
      if (!comments[postId]) {
        fetchComments(postId);
      }
    }
  };


  // 获取标签数组
  const getTags = (tags?: string) => {
    if (!tags) return [];
    try {
      return tags.split(',').filter(t => t.trim());
    } catch {
      return [];
    }
  };

  // 举报功能
  const handleReportPost = async (postId: number) => {
    if (reportingPosts.has(postId)) return;
    
    if (!confirm('确定要举报该帖子吗？')) {
      return;
    }

    try {
      setReportingPosts(prev => new Set(prev).add(postId));
      await communityApi.reportPost(postId);
      
      toast({
        title: '举报成功',
        description: '您的举报已提交，我们会尽快处理',
      });
      
      // 如果举报次数达到3次，帖子会被隐藏，刷新列表
      fetchPosts(selectedCategory);
    } catch (error: any) {
      console.error('举报失败:', error);
      toast({
        title: '举报失败',
        description: error.response?.data?.detail || error?.detail || '无法举报该帖子',
        variant: 'destructive',
      });
    } finally {
      setReportingPosts(prev => {
        const newSet = new Set(prev);
        newSet.delete(postId);
        return newSet;
      });
    }
  };

  // 分享功能
  const handleShare = (post: Post) => {
    if (navigator.share) {
      navigator.share({
        title: `来自${post.author_name}的${post.category}帖子`,
        text: post.content,
        url: window.location.href,
      }).catch(() => {
        // 用户取消分享
      });
    } else {
      // 复制到剪贴板
      const text = `${post.content}\n\n来自: ${post.author_name}`;
      navigator.clipboard.writeText(text).then(() => {
        toast({
          title: '已复制到剪贴板',
        });
      });
    }
  };

  const categoryMap: Record<string, string> = {
    '心情树洞': 'tree-hole',
    '互助问答': 'qa',
    '经验分享': 'share',
  };

  return (
    <div className="space-y-6">
      {/* Create Post */}
      <Card>
        <CardContent className="pt-6">
          <Dialog open={showPostDialog} onOpenChange={setShowPostDialog}>
            <DialogTrigger asChild>
              <Button className="w-full gap-2">
                <Plus className="w-4 h-4" />
                发布帖子
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>发布新帖</DialogTitle>
                <DialogDescription>
                  所有发言默认匿名，请遵守社区规范
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreatePost} className="space-y-4">
                <div className="space-y-2">
                  <Tabs value={postCategory} onValueChange={setPostCategory}>
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="心情树洞">心情树洞</TabsTrigger>
                      <TabsTrigger value="互助问答">互助问答</TabsTrigger>
                      <TabsTrigger value="经验分享">经验分享</TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>

                <Textarea
                  placeholder="说说你的想法..."
                  rows={6}
                  className="resize-none"
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                />

                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="标签（用逗号分隔，可选）"
                    className="w-full px-3 py-2 border rounded-md"
                    value={postTags}
                    onChange={(e) => setPostTags(e.target.value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    禁止人身攻击、广告等违规内容
                  </p>
                  <Button type="submit" disabled={posting}>
                    {posting ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        发布中...
                      </>
                    ) : (
                      '发布'
                    )}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Filter Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
        <TabsList>
          <TabsTrigger value="all">全部</TabsTrigger>
          <TabsTrigger value="tree-hole">心情树洞</TabsTrigger>
          <TabsTrigger value="qa">互助问答</TabsTrigger>
          <TabsTrigger value="share">经验分享</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedCategory} className="space-y-4 mt-6">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : posts.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-gray-500">
                暂无帖子，快来发布第一个吧！
              </CardContent>
            </Card>
          ) : (
            posts.map((post) => (
            <Card key={post.id} className="hover:shadow-md transition">
              <CardContent className="pt-6 space-y-4">
                {/* Post Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                          {post.author_name?.[0] || '用'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium">{post.author_name}</p>
                          {post.author_role && (
                            <Badge variant="secondary" className="text-xs">
                              {post.author_role === 'counselor' ? '咨询师' : post.author_role === 'admin' ? '管理员' : ''}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{formatTime(post.created_at)}</p>
                    </div>
                  </div>
                  <Badge variant="outline">{post.category}</Badge>
                </div>

                {/* Post Content */}
                <div>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{post.content}</p>
                </div>

                {/* Post Tags */}
                  {getTags(post.tags).length > 0 && (
                    <div className="flex gap-2 flex-wrap">
                      {getTags(post.tags).map((tag, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>
                  )}

                {/* Post Actions */}
                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center gap-6">
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`gap-2 ${post.is_liked ? 'text-red-500' : 'text-gray-600 hover:text-red-500'}`}
                        onClick={() => handleLikePost(post.id)}
                        disabled={likingPosts.has(post.id)}
                      >
                        <Heart className={`w-4 h-4 ${post.is_liked ? 'fill-current' : ''}`} />
                        <span>{post.like_count}</span>
                    </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 text-gray-600 hover:text-blue-500"
                        onClick={() => toggleComments(post.id)}
                      >
                      <MessageCircle className="w-4 h-4" />
                        <span>{post.comment_count}</span>
                    </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 text-gray-600 hover:text-green-500"
                        onClick={() => handleShare(post)}
                      >
                      <Share2 className="w-4 h-4" />
                      分享
                    </Button>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-gray-400 hover:text-red-600"
                    onClick={() => handleReportPost(post.id)}
                    disabled={reportingPosts.has(post.id)}
                    title="举报"
                  >
                    <Flag className="w-4 h-4" />
                  </Button>
                </div>

                  {/* Comments Section */}
                  {expandedPost === post.id && (
                    <div className="pt-4 border-t space-y-4">
                      {/* Comment Input */}
                      <div className="flex gap-2">
                        <Textarea
                          placeholder="写下你的评论..."
                          rows={2}
                          className="resize-none flex-1"
                          value={commentContent[post.id] || ''}
                          onChange={(e) => setCommentContent(prev => ({ ...prev, [post.id]: e.target.value }))}
                        />
                        <Button
                          onClick={() => handleCreateComment(post.id)}
                          disabled={!commentContent[post.id]?.trim()}
                        >
                          评论
                        </Button>
                      </div>

                      {/* Comments List */}
                      <div className="space-y-3">
                        {comments[post.id]?.map((comment) => (
                          <div key={comment.id} className="flex gap-3 p-3 bg-gray-50 rounded-lg">
                            <Avatar className="h-8 w-8">
                              <AvatarFallback className="bg-gray-300 text-gray-600 text-xs">
                                {comment.user_name?.[0] || '用'}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="text-sm font-medium">{comment.user_name}</p>
                                <p className="text-xs text-gray-500">{formatTime(comment.created_at)}</p>
                              </div>
                              <p className="text-sm text-gray-700">{comment.content}</p>
                            </div>
                          </div>
                        ))}
                        {comments[post.id]?.length === 0 && (
                          <p className="text-sm text-gray-500 text-center py-4">暂无评论</p>
                        )}
                      </div>
                    </div>
                  )}
              </CardContent>
            </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
