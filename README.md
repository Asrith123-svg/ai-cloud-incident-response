\# AI-Powered Cloud Incident Response \& Root-Cause Analysis System



An event-driven cloud incident response system that detects application failures using AWS services, retrieves relevant operational runbooks using Retrieval-Augmented Generation (RAG), performs AI-assisted incident analysis with a local LLM, and executes controlled remediation only after human approval.



\---



\## Overview



Production incidents such as database failures, high CPU utilization, memory exhaustion, and API latency require engineers to quickly identify the problem, determine the likely cause, and take corrective action.



This project automates the initial incident-response workflow while keeping a human approval step before remediation.



The system combines:



\- AWS Lambda

\- Amazon CloudWatch

\- Amazon EventBridge

\- Amazon S3

\- Amazon DynamoDB

\- Amazon SNS

\- Amazon API Gateway

\- Sentence Transformers

\- FAISS

\- Ollama

\- Llama 3.2 3B

\- Python



The AI analysis is grounded in operational runbooks retrieved through the RAG pipeline.



\---



\## Architecture



```text

&#x20;                   AWS CLOUD

&#x20;                        |

&#x20;                        v

&#x20;             +----------------------+

&#x20;             | Payment API Lambda   |

&#x20;             +----------+-----------+

&#x20;                        |

&#x20;                        v

&#x20;             +----------------------+

&#x20;             |   CloudWatch Logs    |

&#x20;             |    + Metrics         |

&#x20;             +----------+-----------+

&#x20;                        |

&#x20;                        v

&#x20;             +----------------------+

&#x20;             |   CloudWatch Alarm   |

&#x20;             +----------+-----------+

&#x20;                        |

&#x20;                        v

&#x20;             +----------------------+

&#x20;             |     EventBridge      |

&#x20;             +----------+-----------+

&#x20;                        |

&#x20;                        v

&#x20;             +----------------------+

&#x20;             | Incident Controller  |

&#x20;             |       Lambda         |

&#x20;             +----+------------+----+

&#x20;                  |            |

&#x20;                  v            v

&#x20;             +---------+   +-----------+

&#x20;             |   S3    |   | DynamoDB  |

&#x20;             |Runbooks |   | Incidents |

&#x20;             +----+----+   +-----------+

&#x20;                  |

&#x20;                  v

&#x20;       +-------------------------+

&#x20;       | Local AI Analysis       |

&#x20;       |                         |

&#x20;       | Sentence Transformers  |

&#x20;       |          ↓              |

&#x20;       |        FAISS            |

&#x20;       |          ↓              |

&#x20;       |   Ollama / Llama 3.2    |

&#x20;       +------------+------------+

&#x20;                    |

&#x20;                    v

&#x20;            AI Incident Analysis

&#x20;                    |

&#x20;                    v

&#x20;            Human Approval

&#x20;                    |

&#x20;                    v

&#x20;             API Gateway

&#x20;                    |

&#x20;                    v

&#x20;             Approval Lambda

&#x20;                    |

&#x20;                    v

&#x20;           Remediation Lambda

&#x20;                    |

&#x20;                    v

&#x20;         Controlled Remediation

