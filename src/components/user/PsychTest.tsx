import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Clock, FileText, TrendingUp, AlertCircle } from 'lucide-react';

export function PsychTest() {
  const tests = [
    {
      name: '学业压力量表 (PSS)',
      description: '评估学习压力水平，帮助识别压力源',
      duration: '5-8分钟',
      questions: 14,
      category: '压力评估',
      taken: false
    },
    {
      name: '抑郁自评量表 (SDS)',
      description: '评估抑郁情绪程度，及时发现心理健康问题',
      duration: '10-15分钟',
      questions: 20,
      category: '情绪评估',
      taken: true,
      lastScore: 42,
      lastDate: '2025-10-15'
    },
    {
      name: '焦虑自评量表 (SAS)',
      description: '评估焦虑状态，了解焦虑程度',
      duration: '10-15分钟',
      questions: 20,
      category: '情绪评估',
      taken: true,
      lastScore: 38,
      lastDate: '2025-10-20'
    },
    {
      name: '人际关系敏感量表',
      description: '评估人际交往中的敏感程度',
      duration: '8-12分钟',
      questions: 16,
      category: '人际关系',
      taken: false
    },
    {
      name: '睡眠质量量表 (PSQI)',
      description: '评估睡眠质量，发现睡眠问题',
      duration: '5-10分钟',
      questions: 18,
      category: '生活质量',
      taken: false
    },
  ];

  const reports = [
    {
      test: '抑郁自评量表 (SDS)',
      score: 42,
      level: '轻度抑郁',
      date: '2025-10-15',
      trend: 'down'
    },
    {
      test: '焦虑自评量表 (SAS)',
      score: 38,
      level: '轻度焦虑',
      date: '2025-10-20',
      trend: 'up'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Test History */}
      <Card>
        <CardHeader>
          <CardTitle>我的测评报告</CardTitle>
          <CardDescription>查看历史测评结果和趋势分析</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {reports.map((report, index) => (
            <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 transition">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4>{report.test}</h4>
                  <p className="text-sm text-gray-500">{report.date}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-2xl">{report.score}</p>
                    <Badge variant={report.level.includes('轻度') ? 'outline' : 'destructive'}>
                      {report.level}
                    </Badge>
                  </div>
                  <TrendingUp className={`w-5 h-5 ${report.trend === 'down' ? 'text-green-500 rotate-180' : 'text-red-500'}`} />
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <FileText className="w-4 h-4" />
                  查看报告
                </Button>
                <Button variant="outline" size="sm">
                  对比分析
                </Button>
                <Button variant="outline" size="sm">
                  导出PDF
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Available Tests */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tests.map((test, index) => (
          <Card key={index} className="hover:shadow-lg transition">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{test.name}</CardTitle>
                  <CardDescription className="mt-2">{test.description}</CardDescription>
                </div>
                <Badge>{test.category}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {test.duration}
                </div>
                <div className="flex items-center gap-1">
                  <FileText className="w-4 h-4" />
                  {test.questions} 题
                </div>
              </div>

              {test.taken && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-start gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm text-blue-900">上次测评：{test.lastDate}</p>
                      <p className="text-sm text-blue-600 mt-1">得分：{test.lastScore}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <Button className="flex-1">
                  {test.taken ? '重新测评' : '开始测评'}
                </Button>
                {test.taken && (
                  <Button variant="outline">
                    查看报告
                  </Button>
                )}
              </div>

              <p className="text-xs text-gray-500 text-center">
                测评结果仅供参考，不构成医学诊断
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
