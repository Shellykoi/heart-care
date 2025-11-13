import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { BookOpen, Video, Headphones, MessageCircle, Search, Heart, TrendingUp, Clock } from 'lucide-react';

export function HealthContent() {
  const articles = [
    {
      title: '如何应对考前焦虑：5个实用技巧',
      type: 'article',
      category: '学业压力',
      reads: '1.2k',
      duration: '5分钟',
      image: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400'
    },
    {
      title: '深呼吸放松法：缓解紧张情绪',
      type: 'video',
      category: '情绪调节',
      reads: '856',
      duration: '3分钟',
      image: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400'
    },
    {
      title: '改善睡眠质量的7个方法',
      type: 'article',
      category: '生活质量',
      reads: '2.3k',
      duration: '8分钟',
      image: 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=400'
    },
    {
      title: '正念冥想引导练习',
      type: 'audio',
      category: '情绪调节',
      reads: '1.5k',
      duration: '15分钟',
      image: 'https://images.unsplash.com/photo-1545389336-cf090694435e?w=400'
    },
  ];

  const questions = [
    {
      question: '失眠怎么办？有什么快速入睡的方法吗？',
      answers: 12,
      views: 456,
      tags: ['睡眠问题', '失眠']
    },
    {
      question: '如何克服社交恐惧？',
      answers: 8,
      views: 328,
      tags: ['人际关系', '社交焦虑']
    },
    {
      question: '考研压力大，感觉坚持不下去了',
      answers: 15,
      views: 612,
      tags: ['学业压力', '考研']
    },
  ];

  return (
    <div className="space-y-6">
      {/* Search */}
      <Card className="bg-white border-0 shadow-soft">
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-[#666666]" />
            <Input
              placeholder="搜索心理健康知识、技巧、问题..."
              className="pl-10 h-12 bg-[#FAF8F5] border-[#E8E2DB]"
            />
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList>
          <TabsTrigger value="all" className="gap-2">
            <BookOpen className="w-4 h-4" />
            全部
          </TabsTrigger>
          <TabsTrigger value="articles" className="gap-2">
            <BookOpen className="w-4 h-4" />
            文章
          </TabsTrigger>
          <TabsTrigger value="videos" className="gap-2">
            <Video className="w-4 h-4" />
            视频
          </TabsTrigger>
          <TabsTrigger value="audio" className="gap-2">
            <Headphones className="w-4 h-4" />
            音频
          </TabsTrigger>
          <TabsTrigger value="qa" className="gap-2">
            <MessageCircle className="w-4 h-4" />
            问答
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-6">
          {/* Featured Content */}
          <div>
            <h3 className="text-lg mb-4 flex items-center gap-2 text-[#222222]">
              <TrendingUp className="w-5 h-5 text-[#FFD166]" />
              热门推荐
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {articles.map((item, index) => (
                <Card key={index} className="overflow-hidden hover:shadow-medium transition cursor-pointer bg-white border-0 shadow-soft">
                  <div className="aspect-video bg-[#FAF8F5] relative">
                    <img src={item.image} alt={item.title} className="w-full h-full object-cover" />
                    <div className="absolute top-3 left-3">
                      <Badge className="bg-white/90 text-[#222222]">
                        {item.type === 'article' && <BookOpen className="w-3 h-3 mr-1" />}
                        {item.type === 'video' && <Video className="w-3 h-3 mr-1" />}
                        {item.type === 'audio' && <Headphones className="w-3 h-3 mr-1" />}
                        {item.type === 'article' ? '文章' : item.type === 'video' ? '视频' : '音频'}
                      </Badge>
                    </div>
                  </div>
                  <CardContent className="pt-4">
                    <Badge variant="outline" className="mb-2 bg-[#FFEDD5] text-[#222222] border-[#E8E2DB]">{item.category}</Badge>
                    <h4 className="mb-3 line-clamp-2 text-[#222222]">{item.title}</h4>
                    <div className="flex items-center justify-between text-sm text-[#666666]">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {item.duration}
                        </span>
                        <span>{item.reads} 阅读</span>
                      </div>
                      <Button variant="ghost" size="sm" className="hover:bg-[#FFEDD5]">
                        <Heart className="w-4 h-4 text-[#FFD166]" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Q&A Section */}
          <div>
            <h3 className="text-lg mb-4 flex items-center gap-2 text-[#222222]">
              <MessageCircle className="w-5 h-5 text-[#FFD166]" />
              热门问答
            </h3>
            <div className="space-y-4">
              {questions.map((q, index) => (
                <Card key={index} className="hover:shadow-medium transition cursor-pointer bg-white border-0 shadow-soft">
                  <CardContent className="pt-6">
                    <h4 className="mb-3 text-[#222222]">{q.question}</h4>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        {q.tags.map((tag, i) => (
                          <Badge key={i} variant="secondary" className="bg-[#FFEDD5] text-[#222222] border-[#E8E2DB]">{tag}</Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-[#666666]">
                        <span>{q.answers} 回答</span>
                        <span>{q.views} 浏览</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="articles">
          <div className="text-center text-[#666666] py-12">
            文章内容列表...
          </div>
        </TabsContent>

        <TabsContent value="videos">
          <div className="text-center text-[#666666] py-12">
            视频内容列表...
          </div>
        </TabsContent>

        <TabsContent value="audio">
          <div className="text-center text-[#666666] py-12">
            音频内容列表...
          </div>
        </TabsContent>

        <TabsContent value="qa">
          <div className="text-center text-[#666666] py-12">
            问答内容列表...
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
