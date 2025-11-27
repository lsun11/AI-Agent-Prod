# src/api/data/suggestions_pool.py

# ----- 20 English hard-coded fallback questions -----
DEFAULT_POOL_EN = [
    "Good Python IDEs for beginners?",
    "VS Code vs JetBrains IDEs pros and cons?",
    "Recommended Postgres services on AWS?",
    "Recommended Postgres services on GCP?",
    "Alternatives to AWS Lambda for serverless?",
    "Best platforms for practicing coding interviews?",
    "How to improve a microservices architecture?",
    "Good resources to learn system design?",
    "Tools for monitoring distributed systems?",
    "Best practices for multi-tenant SaaS design?",
    "How to restructure a resume for senior roles?",
    "Good AWS services for backend developers?",
    "When to use DynamoDB vs Postgres?",
    "Best tools for API load testing?",
    "How to choose a managed Kubernetes provider?",
    "Alternatives to Terraform for IaC?",
    "How to improve CI/CD pipeline reliability?",
    "Best logging solutions for cloud apps?",
    "How to design scalable event-driven systems?",
    "Best resources to prepare for system design interviews?",
]

# ----- 20 Chinese fallback questions (accurate translations) -----
DEFAULT_POOL_CHN = [
    "适合初学者的 Python IDE？",
    "VS Code 与 JetBrains IDE 的优缺点？",
    "在 AWS 上推荐哪些托管 Postgres 服务？",
    "在 GCP 上推荐哪些托管 Postgres 服务？",
    "有哪些可替代 AWS Lambda 的无服务器方案？",
    "哪些平台适合练习编码面试题？",
    "如何改进微服务架构？",
    "有哪些适合学习系统设计的优质资源？",
    "有哪些工具可用于监控分布式系统？",
    "多租户 SaaS 架构的最佳实践有哪些？",
    "如何重构我的简历以匹配高级工程师职位？",
    "适合后端开发的 AWS 服务有哪些？",
    "什么时候选择 DynamoDB 而不是 Postgres？",
    "有哪些优秀的 API 压力测试工具？",
    "如何选择托管 Kubernetes 服务提供商？",
    "有哪些 Terraform 的替代 IaC 工具？",
    "如何提升 CI/CD 流水线的可靠性？",
    "云应用常用的日志解决方案有哪些？",
    "如何设计可扩展的事件驱动系统？",
    "有哪些准备系统设计面试的高质量资源？",
]
