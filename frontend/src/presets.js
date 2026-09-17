// HireLens.AI — Curated Job Descriptions & Sample Candidates for Instant Demo

export const JOB_DESCRIPTION_PRESETS = [
  {
    id: "data-scientist",
    title: "Senior Data Scientist & AI Specialist",
    category: "Data Science",
    text: `Role: Senior Data Scientist / Machine Learning Engineer
Department: AI & Advanced Analytics

Key Responsibilities:
- Design, build, and deploy end-to-end Machine Learning and Deep Learning pipelines for production systems.
- Perform exploratory data analysis, feature engineering, and statistical modeling on large datasets using Pandas, NumPy, and Scikit-Learn.
- Build NLP and computer vision models utilizing PyTorch, TensorFlow, and HuggingFace Transformers.
- Deploy scalable ML APIs using FastAPI, Docker, and Kubernetes on AWS or GCP.
- Monitor model drift, data quality, and explainability using SHAP, MLflow, and Weights & Biases.
- Collaborate with product managers and software engineers to deliver data-driven business impact.

Required Qualifications & Skills:
- 4+ years of professional experience in Machine Learning, Statistics, and predictive analytics.
- Strong proficiency in Python, SQL, Git, and data manipulation.
- Experience with Deep Learning frameworks (PyTorch or TensorFlow) and NLP techniques (BERT, LLMs, embeddings).
- Hands-on experience with cloud infrastructure (AWS/GCP), CI/CD, and containerization (Docker).
- Strong communication and problem-solving skills with a degree in Computer Science, Data Science, or related STEM field.`,
  },
  {
    id: "python-backend",
    title: "Lead Python / Backend Engineer",
    category: "Python Developer",
    text: `Role: Senior / Lead Python Backend Developer
Department: Core Platform Engineering

Key Responsibilities:
- Architect, build, and maintain high-throughput asynchronous RESTful and GraphQL APIs using FastAPI, Flask, and Django.
- Design performant database schemas with PostgreSQL, Redis caching, and SQLAlchemy ORM.
- Implement robust distributed task queues using Celery, RabbitMQ, and Apache Kafka.
- Write unit, integration, and performance tests with PyTest and maintain 90%+ code coverage.
- Manage CI/CD pipelines, containerize microservices with Docker, and orchestrate with Kubernetes.
- Drive architecture reviews, security best practices (OAuth2, JWT), and code quality standards.

Required Qualifications & Skills:
- 5+ years of production Python engineering experience.
- Expert knowledge of Python 3, asynchronous programming (asyncio), and API design.
- Solid experience with relational databases (PostgreSQL/MySQL) and caching (Redis).
- Proven track record with Docker, Linux system administration, and cloud deployment (AWS/GCP).
- Experience with microservices architecture, system design, and observability (Prometheus, Grafana).`,
  },
  {
    id: "devops-architect",
    title: "DevOps & Cloud Infrastructure Architect",
    category: "DevOps",
    text: `Role: Senior DevOps / Site Reliability Engineer (SRE)
Department: Cloud Platform Operations

Key Responsibilities:
- Design, deploy, and manage multi-region cloud infrastructure on AWS and GCP using Infrastructure as Code (Terraform, CloudFormation).
- Architect and maintain enterprise Kubernetes (EKS/GKE) clusters, service mesh, and Helm charts.
- Build automated CI/CD deployment pipelines using GitHub Actions, GitLab CI, and ArgoCD.
- Implement comprehensive monitoring, alerting, and logging using Prometheus, Grafana, Datadog, and ELK Stack.
- Enforce cloud security policies, IAM access governance, secret management (Vault), and compliance.

Required Qualifications & Skills:
- 4+ years in DevOps, Cloud Engineering, or SRE roles.
- Expert knowledge of Kubernetes, Docker, and Linux system internals.
- Strong proficiency in Terraform and cloud automation scripting (Python, Bash, Go).
- Extensive experience with AWS (VPC, IAM, EC2, S3, RDS) and CI/CD tooling.
- Deep understanding of networking, DNS, load balancing, and high availability.`,
  },
  {
    id: "fullstack-developer",
    title: "Full Stack Engineer (React + Python)",
    category: "Web Designing",
    text: `Role: Senior Full Stack Software Engineer
Department: Product Engineering

Key Responsibilities:
- Build responsive, modern web applications with React, TypeScript, Next.js, and CSS/Tailwind.
- Develop scalable backend microservices and REST APIs using Python, FastAPI, and Node.js.
- Optimize web app performance, Core Web Vitals, state management (Zustand/Redux), and accessibility.
- Manage end-to-end feature delivery from database schema design (PostgreSQL/MongoDB) to interactive front-end.
- Collaborate closely with UI/UX designers to translate Figma prototypes into polished user interfaces.

Required Qualifications & Skills:
- 3+ years of full stack software engineering experience.
- Strong proficiency in modern JavaScript/TypeScript, React, HTML5, and CSS.
- Solid backend experience in Python (FastAPI/Django) or Node.js.
- Familiarity with RESTful APIs, Git, Docker, and cloud hosting platforms.
- Passion for user experience, design consistency, and clean code.`,
  },
];

export const RESUME_PRESETS = [
  {
    id: "alex-chen-ds",
    candidateName: "Alex Chen",
    role: "Senior Machine Learning Engineer",
    text: `Alex Chen
San Francisco, CA | alex.chen@example.com | +1 (555) 382-9912 | linkedin.com/in/alexchen-ai

SUMMARY
Senior Data Scientist and Machine Learning Engineer with 5+ years of experience building predictive models, NLP systems, and scalable ML infrastructure. Led AI initiatives delivering $4.2M in annual cost reductions. Expert in Python, PyTorch, Scikit-Learn, Docker, and AWS.

CORE TECHNICAL SKILLS
- Languages: Python, SQL, Bash, C++
- ML & Deep Learning: PyTorch, TensorFlow, Scikit-Learn, HuggingFace, XGBoost, Pandas, NumPy, Keras, SHAP
- NLP & AI: Transformers, BERT, LLMs, Vector Databases, Semantic Search, Word2Vec
- Cloud & Infrastructure: AWS (S3, EC2, SageMaker, Lambda), Docker, Kubernetes, Git, CI/CD, MLflow
- Databases: PostgreSQL, MongoDB, Redis

PROFESSIONAL EXPERIENCE
Senior Machine Learning Engineer | NeuralScale AI (2022 – Present)
- Architected and deployed production NLP sentiment analysis and text classification pipeline processing 2M+ customer queries daily using PyTorch and FastAPI.
- Implemented explainable AI (SHAP) and model monitoring with MLflow, reducing false positives by 28%.
- Containerized model training workflows with Docker and deployed on AWS EKS using Helm charts.

Data Scientist | DataPulse Analytics (2019 – 2022)
- Built churn prediction and recommendation algorithms using Scikit-Learn and XGBoost, improving customer retention by 18%.
- Designed automated ETL pipelines in Python and SQL to ingest 50GB+ daily user behavior logs from PostgreSQL.
- Authored internal documentation and led machine learning best practice workshops for 12 junior data analysts.

EDUCATION
Master of Science in Computer Science (Machine Learning Focus) — Stanford University (2019)
Bachelor of Science in Data Science — UC Berkeley (2017)`,
  },
  {
    id: "priya-patel-python",
    candidateName: "Priya Patel",
    role: "Lead Python Backend Developer",
    text: `Priya Patel
Austin, TX | priya.patel@email.com | +1 (555) 749-2104 | github.com/priyapatel-dev

SUMMARY
Results-driven Lead Python Backend Engineer with 6 years of experience engineering high-performance microservices, REST/GraphQL APIs, and distributed systems. Passionate about clean architecture, test-driven development, and scalable cloud solutions.

CORE TECHNICAL SKILLS
- Languages & Frameworks: Python 3, FastAPI, Django, Flask, asyncio, Pydantic
- Databases & Caching: PostgreSQL, MySQL, Redis, Elasticsearch, SQLAlchemy
- Distributed Systems & Queues: Celery, RabbitMQ, Apache Kafka, Event-driven architecture
- DevOps & Tools: Docker, Kubernetes, AWS, GitHub Actions, Linux, PyTest, Git

PROFESSIONAL EXPERIENCE
Lead Backend Engineer | CloudFlow Technologies (2021 – Present)
- Led team of 6 engineers building multi-tenant SaaS backend with FastAPI and PostgreSQL handling 15,000 requests/sec with sub-50ms latency.
- Implemented asynchronous event streaming pipeline using Kafka and Celery workers for transaction processing.
- Containerized application with Docker, orchestrated with Kubernetes on AWS, and built automated CI/CD testing with PyTest.

Senior Python Developer | Apex Financial Systems (2018 – 2021)
- Developed secure REST APIs adhering to OAuth2 and JWT protocols for banking integration using Django and Flask.
- Refactored legacy database queries and implemented Redis caching, cutting page load latency by 45%.
- Maintained 92% unit and integration test coverage across all core payment microservices.

EDUCATION
Bachelor of Science in Software Engineering — University of Texas at Austin (2018)`,
  },
  {
    id: "marcus-vance-devops",
    candidateName: "Marcus Vance",
    role: "DevOps & Cloud SRE",
    text: `Marcus Vance
Seattle, WA | marcus.vance@techmail.io | +1 (555) 612-8840 | github.com/marcusvance

SUMMARY
DevOps and Site Reliability Engineer with 4+ years specializing in AWS cloud infrastructure, Kubernetes orchestration, Terraform automation, and zero-downtime CI/CD pipelines.

TECHNICAL SKILLS
- Cloud Platforms: AWS (VPC, IAM, EKS, EC2, S3, RDS, CloudFront), Google Cloud Platform (GCP)
- Containers & Orchestration: Kubernetes, Docker, Helm, Docker Compose
- Infrastructure as Code: Terraform, Ansible, CloudFormation
- CI/CD & Automation: GitHub Actions, GitLab CI, ArgoCD, Bash, Python scripting
- Observability: Prometheus, Grafana, Datadog, ELK Stack

EXPERIENCE
DevOps Engineer | Stratus Cloud Solutions (2022 – Present)
- Automated provisioning of AWS infrastructure across 3 environments using Terraform modules, reducing setup time from days to 15 minutes.
- Migrated 40+ legacy services into AWS EKS Kubernetes clusters with Helm charts and zero downtime.
- Configured real-time metrics dashboards in Grafana with Prometheus alerting, improving MTTR by 35%.

Systems Engineer | NextGen Networks (2020 – 2022)
- Managed Linux production servers, network configurations, SSL certificates, and DNS records.
- Built GitHub Actions CI/CD workflows for automated build, test, and container deployment.

EDUCATION
Bachelor of Science in Information Technology — University of Washington (2020)`,
  },
  {
    id: "elena-rostova-frontend",
    candidateName: "Elena Rostova",
    role: "Senior React & Frontend Engineer",
    text: `Elena Rostova
New York, NY | elena.rostova@designhub.co | +1 (555) 902-1433 | elenarostova.design

SUMMARY
Senior Front-End & UI/UX Engineer with 4 years creating responsive, accessible, high-performance web applications. Expert in React, TypeScript, Next.js, and modern CSS architecture.

TECHNICAL SKILLS
- Frontend: React.js, TypeScript, Next.js, Redux Toolkit, Zustand, HTML5, CSS3, Sass
- Styling: Tailwind CSS, CSS Modules, Styled Components, Framer Motion
- Testing & Tools: Jest, React Testing Library, Webpack, Vite, Git, Figma
- APIs & Backend Basics: REST APIs, GraphQL, Node.js, Express, PostgreSQL

EXPERIENCE
Senior Frontend Developer | PixelCraft Studio (2022 – Present)
- Built state-of-the-art interactive analytics dashboard in React & Next.js serving 300K monthly active users.
- Improved Core Web Vitals (LCP by 40%, CLS to 0.01) by implementing code-splitting, lazy-loading, and SVG optimization.
- Created reusable component library in TypeScript based on Figma design system specifications.

Frontend Developer | Horizon Media (2020 – 2022)
- Developed responsive marketing pages and customer portals using React and modern CSS animations.
- Collaborated with UX researchers to conduct usability testing and implement WCAG 2.1 AA accessibility guidelines.

EDUCATION
B.A. in Computer Arts & Web Development — Pratt Institute (2020)`,
  },
];
