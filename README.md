# Content Pipeline

**An AI-powered content processing system that classifies, enriches, and routes sports content at scale**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Anthropic](https://img.shields.io/badge/API-Anthropic%20Claude-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Project Overview

This project demonstrates a **production-ready content automation pipeline** built for B2B sports media platforms. It simulates how companies like ESPN, FanDuel, or Bleacher Report process thousands of articles daily - automatically classifying content, extracting structured metadata, generating audience-specific variations, and routing to appropriate downstream systems.

**Business Context**: Sports media companies need to process high volumes of content with consistency and speed. Manual classification and tagging doesn't scale. This pipeline automates the entire workflow using AI, from raw input to structured, routed output.

---

## Architecture

### Pipeline Stages

The pipeline chains **three sequential AI calls** (demonstrating AI orchestration):

```
Raw Content → [1] Classify → [2] Extract Metadata → [3] Generate Headlines → Route to Destination
                  ↓               ↓                      ↓                      ↓
              match_report    teams, players,       3 headline versions    outputs/match_reports/
              transfer_news   competition,          (neutral, fan,         outputs/transfer_news/
              injury_update   sentiment,            casual)                outputs/injury_updates/
              opinion_piece   key_stats                                    outputs/opinion_pieces/
```

### Why Chain AI Calls?

Rather than one monolithic prompt, we chain calls because:

1. **Separation of Concerns**: Each stage does one thing well. If headline generation fails, you still have classification + metadata.
2. **Conditional Logic**: Different content types need different extraction (match reports need scores; transfers need fees).
3. **Cost Efficiency**: Skip expensive downstream processing if content isn't relevant.
4. **Observability**: Pinpoint exactly where failures occur in the pipeline.

**Trade-off**: Higher latency (3 sequential calls) vs. better reliability and debuggability. For batch processing (not real-time), this is the right choice.

---

## Key Features

### Production Engineering Principles

- **Structured Logging**: Every stage is logged with timestamps, input IDs, and outcomes for debugging at scale
- **Error Handling**: Graceful failures with specific error messages at each stage
- **Content Routing**: Different content types → different destinations (simulating microservice architecture)
- **Modular Design**: Each pipeline component is independent and testable
- **Conditional Processing**: Extraction logic adapts based on content type
- **Batch Processing**: Handle multiple items in sequence with summary statistics

### AI/ML Techniques

- **Prompt Engineering**: Content-type-specific prompts, few-shot examples, structured output requests
- **Audience-Aware Generation**: Three headline variations for different user personas
- **Metadata Extraction**: Converting unstructured text → structured JSON
- **Classification with Confidence Scores**: Not just categories, but how confident the model is

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:Asani-A/content-pipeline.git
   cd content-pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

### Quick Start

**Run the test suite** (processes 5 diverse test cases):
```bash
python test_runner.py
```

**Process a single item**:
```bash
python main.py
```

**Process custom content**:
```python
from main import ContentPipeline

pipeline = ContentPipeline()

result = pipeline.process(
    content="Your sports content here...",
    input_id="custom_001",
    source="manual_input"
)
```

---

## Test Coverage

The test suite includes **5 diverse scenarios** to prove robustness:

| Test Case | Content Type | Sport | Purpose |
|-----------|-------------|-------|---------|
| 1 | Match Report | Football | Happy path - standard match coverage |
| 2 | Transfer News | Basketball | Cross-sport handling, financial data |
| 3 | Injury Update | Football | Negative sentiment, medical terminology |
| 4 | Opinion Piece | Basketball | Subjective content, analysis vs facts |
| 5 | Edge Case | Football | Ambiguous/mixed content (training incident + transfer rumors) |

**Why these tests matter**: Real pipelines need to handle edge cases, not just happy paths. These tests prove the system is production-ready.

---

## Project Structure

```
content-pipeline/
├── pipeline/
│   ├── classifier.py      # Stage 1: Content classification
│   ├── extractor.py       # Stage 2: Metadata extraction  
│   ├── generator.py       # Stage 3: Headline generation
│   ├── router.py          # Routing logic to output destinations
│   └── logger.py          # Structured logging for observability
├── outputs/               # Routed content by type
│   ├── match_reports/
│   ├── transfer_news/
│   ├── injury_updates/
│   └── opinion_pieces/
├── logs/                  # Processing logs
├── main.py               # Pipeline orchestrator
├── test_runner.py        # Comprehensive test suite
├── config.py             # Configuration and settings
└── requirements.txt      # Dependencies
```

---

## 🔍 How It Works (Under the Hood)

### Stage 1: Classification

```python
# Prompt: Classify content into one of 5 categories
# Output: {"content_type": "match_report", "confidence": 0.95, "reasoning": "..."}
```

**Why this matters**: Different content types flow to different systems (live scores, transfer trackers, fantasy APIs, editorial CMS).

### Stage 2: Metadata Extraction

```python
# Prompt changes based on Stage 1 classification
# Match report → extract: score, goalscorers, attendance
# Transfer news → extract: player, clubs, fee, contract length
# Output: Structured JSON with teams, players, competition, sentiment, key_stats
```

**Why this matters**: Downstream systems need structured data, not paragraphs. This converts text → database-ready fields.

### Stage 3: Headline Generation

```python
# Uses metadata from Stage 2 as context
# Generates 3 variations:
# - Neutral: "Manchester United defeat Liverpool 2-1"
# - Fan: "Red Devils sink Liverpool with late winner!"  
# - Casual: "Man United beat rivals Liverpool in crucial Premier League clash"
```

**Why this matters**: Different audiences need different framing. B2C apps show fan-oriented; aggregators show neutral.

### Stage 4: Routing

```python
# match_report → outputs/match_reports/
# transfer_news → outputs/transfer_news/
# Each file contains: original content + all processing results + timestamps
```

**Why this matters**: Simulates microservice architecture where different content types go to different APIs/databases.

---

## Sample Output

**Input**: Match report about Manchester United vs Liverpool

**Output File** (`outputs/match_reports/test_001_match_report_20240219_143022.json`):

```json
{
  "input_id": "test_001_match_report",
  "processed_at": "2024-02-19T14:30:22.451234",
  "content_type": "match_report",
  "classification": {
    "content_type": "match_report",
    "confidence": 0.96,
    "reasoning": "Contains match score, goalscorers, and post-match analysis"
  },
  "metadata": {
    "teams": ["Manchester United", "Liverpool"],
    "players": ["Marcus Rashford", "Bruno Fernandes", "Mohamed Salah"],
    "competition": "Premier League",
    "sentiment": "positive",
    "key_stats": {
      "score": "2-1",
      "goalscorers": ["Marcus Rashford", "Bruno Fernandes", "Mohamed Salah"],
      "attendance": "74,879"
    }
  },
  "headlines": {
    "neutral": "Manchester United defeat Liverpool 2-1 at Old Trafford",
    "fan_oriented": "Red Devils down Liverpool in thrilling derby clash!",
    "casual_viewer": "Man United beat historic rivals Liverpool 2-1 to boost top-four hopes"
  },
  "original_content": "...",
  "pipeline_version": "1.0"
}
```

---

## Technical Concepts Demonstrated

### For Interviewers

This project showcases:

1. **AI Orchestration**: Chaining multiple LLM calls with conditional logic
2. **Prompt Engineering**: Content-type-specific prompts, structured outputs, few-shot learning
3. **Production Observability**: Structured logging, error tracking, success metrics
4. **Modular Architecture**: Single-responsibility components, easy to test/update
5. **Real-World Scaling**: Batch processing, routing logic, edge case handling
6. **API Integration**: Anthropic Claude API usage with proper error handling

### Why This Project Matters

B2B SaaS platforms (sports media, content aggregators, betting platforms) process **millions** of articles monthly. They need:

- **Automated classification** (human tagging doesn't scale)
- **Structured metadata** (databases need fields, not paragraphs)  
- **Audience variations** (same content, different framing for different users)
- **Reliable pipelines** (failures must be debuggable, retryable)


---

## Challenges & Solutions

### JSON Parsing Robustness

**Challenge**: During initial testing, all 5 test cases failed at the metadata extraction stage with `JSONDecodeError`. The structured logging revealed that classification succeeded, but extraction consistently failed with "Expecting value: line 1 column 1".

**Root Cause**: Claude API responses sometimes include markdown formatting (``` json ... ```) or preamble text ("Here's the metadata:"), which breaks standard `json.loads()` parsing. This is common with LLMs optimized for human-readable output rather than strict machine parsing.

**Solution**: Implemented a robust JSON extraction utility (`pipeline/utils.py`) using a fallback strategy pattern:
1. **Fast path**: Try simple `json.loads()` first
2. **Markdown removal**: Strip ``` code fences if present  
3. **Object extraction**: Find first `{` and last `}`, ignore surrounding text
4. **Clear errors**: Show what was received if all strategies fail

This defensive programming approach was applied across all three API-calling modules (classifier, extractor, generator), making the entire pipeline resilient to response format variations.

**Impact**: Success rate improved from 0% to 100% on test suite. The centralized utility means any future response format issues only need to be fixed once.

**Key Takeaway**: When integrating with LLMs in production, never assume responses match documentation perfectly. Build defensive parsing that handles multiple formats, and use structured logging to quickly isolate failures.

---

## Future Enhancements

Production-ready additions for scaling:

- [ ] **Async processing** with task queues (Celery, RabbitMQ)
- [ ] **Database integration** (PostgreSQL for metadata, S3 for content)
- [ ] **Caching layer** (Redis for frequently accessed content)
- [ ] **Monitoring dashboard** (Grafana + Prometheus for pipeline metrics)
- [ ] **A/B testing** for headline variants (track which headlines get more clicks)
- [ ] **Model versioning** (track which Claude model version processed each item)
- [ ] **Retry logic** with exponential backoff for transient API failures
- [ ] **Dead letter queue** for items that fail repeatedly

---

## Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:

- Open an issue for bugs or feature requests
- Submit a pull request with improvements
- Share how you'd extend this for your use case

---

## License

MIT License - feel free to use this code for learning or your own projects.

---

## About

Built by Abdul-Jaleel Asani as a portfolio project demonstrating AI engineering skills for production content platforms.

**Connect**: abduljaleelasani@gmail.com(#)

---

## Tags

`ai-engineering` `anthropic-claude` `content-automation` `production-ml` `sports-tech` `b2b-saas` `pipeline-orchestration` `prompt-engineering` `python`
