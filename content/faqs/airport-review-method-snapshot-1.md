# Timeout可以按0ms算进平均值吗？

不可以。超时没有提供有效毫秒数，记为0会让结果显得更好。应单独统计超时数量，对有效数值另算统计量，并说明两者的样本口径。

## 核对步骤

1. 保留Timeout原状态
2. 只对有效数值计算
3. 同时显示总数和超时数

[完整指南](article-airport-review-method-snapshot.html)
