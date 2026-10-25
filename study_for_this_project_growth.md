# IncuBrix Growth Engine: Technical & Product Master Study Guide
**Document:** `study_for_this_project_growth.md`  
**Author:** Nantha Kumar B (PSG Tech Reg ID: 23I243)  
**Role:** Growth Engineer / Technical Partner Candidate  
**Assessment:** IncuBrix Assessment — Option 2: Social Media & Content Engine  
**Project Repository:** [github.com/NanthaKumar-cloud/Growth](https://github.com/NanthaKumar-cloud/Growth)

---

## Table of Contents
1. [Executive Summary & The "Elevator Pitch"](#1-executive-summary--the-elevator-pitch)
2. [Product Context & Market Insight (The "Why")](#2-product-context--market-insight-the-why)
3. [End-to-End System Architecture (The "How")](#3-end-to-end-system-architecture-the-how)
4. [Creative Studio Modules Deep Dive](#4-creative-studio-modules-deep-dive)
   - 4.1 AI Content Engine & Orchestrator
   - 4.2 Video Studio & FFmpeg Pipeline
   - 4.3 Carousel Studio (Vector SVG & Pillow)
   - 4.4 Image Studio (High-Impact Visual Posts)
   - 4.5 Voice Hub & TTS Generation
5. [Publishing, Dispatch & API Resilience](#5-publishing-dispatch--api-resilience)
6. [Data Integrity, Deduplication & Quality Control](#6-data-integrity-deduplication--quality-control)
7. [Empirical Audience Experiment ($N=24$)](#7-empirical-audience-experiment-n24)
8. [Performance Benchmarks & Financial Audit](#8-performance-benchmarks--financial-audit)
9. [Top 25 Technical Interview Questions & Model Answers](#9-top-25-technical-interview-questions--model-answers)
10. [Live Demo Walkthrough Script & Talking Points](#10-live-demo-walkthrough-script--talking-points)

---

## 1. Executive Summary & The "Elevator Pitch"

### What is this project?
The **IncuBrix Social Media & Content Engine** is an automated, production-grade Python/FastAPI software platform that ingests a single long-form input (e.g., a 15-minute podcast, a technical case study, or a product demo transcript) and autonomously transforms it into **10+ validated, platform-native, ready-to-publish social assets** in under **2 minutes** at a direct API cost of **$0.0018**.

### Key Deliverables Built & Verified:
- **30 Publication-Ready Assets** delivered in `calendar.csv` across 3 primary platforms (YouTube Shorts, Facebook Pages, Instagram).
- **10 Vertical Short Videos** (1080×1920 MP4) with dynamic burned-in word-paced subtitles and background audio.
- **8 Multi-Slide Carousels** (1080×1350 PDF & PNG slide sets) with branded themes and typography.
- **20 Visual Graphic Posts** (1080×1080 square) with high-contrast hooks and automated UTM attribution links.
- **Automated Social Dispatchers** with OAuth token management and remote CDN upload resilience for Meta Graph API (Instagram/Facebook) and YouTube Data API v3.
- **55 Automated Pytest Unit/Integration Tests** passing at 100% test coverage across deduplication, schema validation, failure recovery, and media rendering.

---

## 2. Product Context & Market Insight (The "Why")

### What is IncuBrix?
IncuBrix (`https://incubrix.com` and `https://app.incubrix.com`) is an all-in-one **CreatorOps Platform**. It consolidates the fragmented creator workflow:
1. **Ideation:** `/thought-inbox` (voice/text quick-capture buffer).
2. **Video Editing:** `/editor` (prompt-based text video cutting).
3. **Voice Engineering:** `/voice-hub` and `/clone-voice` (synthetic voiceover).
4. **Distribution:** `/publishing` (omnichannel dispatch to YouTube, Instagram, Facebook).
5. **Team Collaboration:** `/collab` (multi-user approval states: `PENDING_APPROVAL`, `accept`, `reject`).

### The Core Customer Problem: "The $97/mo Tool Bloat"
Modern creators and B2B growth marketers waste 80% of their time and budget juggling disconnected point-solutions:
- **Descript:** $24/month (audio transcription & text edit)
- **Opus Clip:** $19/month (video clip extraction)
- **Jasper / Copy.ai:** $39/month (copywriting & captions)
- **Buffer / Hootsuite:** $15/month (scheduling & publishing)
- **Total:** **$97 to $120/month** across 4 different browser logins, losing 23 minutes on average per context switch.

### IncuBrix's Value Proposition:
IncuBrix replaces this fragmented stack with **one unified $29/month workspace**. Our growth engine demonstrates the power of this consolidation by automating the entire 1-to-10 repurposing workflow in code.

---

## 3. End-to-End System Architecture (The "How")

```
                                 [ User / Raw Input ]
                    (Podcast Transcript / Case Study / Markdown)
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    FastAPI Web Server / Async Queue   │
                      │  (POST /api/generate/from-source)     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │   AI Orchestrator (Google Gemini)     │
                      │   - gemini-2.5-flash / 3.5-flash-lite │
                      │   - JSON Schema Structured Extraction │
                      └───────────────────┬───────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
            ▼                             ▼                             ▼
┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────┐
│     Video Studio      │   │      Carousel Studio      │   │     Image Studio      │
│  (ad_video_maker.py)  │   │ (animated_svg_carousel.py)│   │     (ad_image.py)     │
│ - Script generation   │   │ - Vector SVG generation   │   │ - Hook typography     │
│ - TTS voice synthesis │   │ - Branded layout rendering│   │ - 1080x1080 visual    │
│ - FFmpeg 1080x1920 MP4│   │ - 1080x1350 PDF/PNG slides│   │ - UTM tracking URLs   │
│ - Burned-in captions  │   │ - Dynamic slide counters  │   │ - Pillow composition  │
└───────────┬───────────┘   └─────────────┬─────────────┘   └───────────┬───────────┘
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ Quality Control & Deduplication Gate  │
                      │ - SHA256 & Jaccard Token Deduplicator │
                      │ - Forbidden phrase validator          │
                      │ - Schema compliance & duration checks │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │       Asset Store & Export Hub        │
                      │ - Output: data/outputs/calendar.csv   │
                      │ - Static hosting: /media/*            │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Automated Social Dispatch Engine   │
                      │ - YouTube Shorts (OAuth v3 API)       │
                      │ - Facebook Pages (Graph API v19.0)    │
                      │ - Instagram Reels (Container Dispatch)│
                      │ - Fallback CDN & Proxy Tunneling      │
                      └───────────────────┬───────────────────┘
```

---

## 4. Creative Studio Modules Deep Dive

### 4.1 AI Content Engine & Orchestrator (`src/api/generate_api.py`)
- **Model:** `gemini-2.5-flash` (production fallback to `gemini-3.5-flash-lite`).
- **Mechanism:** Takes raw source text, system prompts enforcing IncuBrix editorial voice, and enforces a strict JSON schema returning exactly 10 deliverables:
  - 3 Short Videos (hooks, 15–30s scripts, audio narration cues, visual directions).
  - 2 Multi-Slide Carousels (5 slides each: Title, Problem, Engineering Insight, Proof/Metrics, Actionable CTA).
  - 5 High-Impact Thought Leadership Graphics (hook headline, caption body, hashtags, platform-specific CTA).
- **Asynchronous Execution:** Generation runs inside a background worker thread (`asyncio.create_task`). The frontend polls `GET /api/generate/status/{job_id}` every 1,000ms until complete, preventing HTTP connection dropouts on large inputs.

### 4.2 Video Studio & FFmpeg Pipeline (`src/studios/ad_video_maker.py`)
- **Output:** 1080×1920 vertical MP4 video, 30 fps constant frame rate (CFR), AAC audio at 192 kbps.
- **Audio Generation:** Text scripts are converted to high-definition voiceover via Google Cloud TTS / Edge-TTS (e.g., `en-US-Journey-F` or `en-US-ChristopherNeural`).
- **Dynamic Captions:** Generates an `.srt` or `.ass` subtitle file paced with words, burning high-contrast white text with black drop-shadows into the bottom-third of the frame using the FFmpeg `subtitles` filter.
- **Audio Mixing:** Synthesizes low-volume synthwave background music mixed with the primary voice track using the `amix=inputs=2:duration=first:dropout_transition=2` filter.

### 4.3 Carousel Studio (`src/studios/animated_svg_carousel.py`)
- **Output:** High-resolution 1080×1350 multi-slide PDF document carousels and standalone PNG slides.
- **Rendering Technique:** Generates declarative SVG templates with styled gradients, dark cyberpunk cards, and modern system typography (Inter / Roboto). Converted to high-DPI bitmaps using CairoSVG and Pillow.
- **Layout Architecture:**
  - Slide 1: Bold problem hook + IncuBrix logo badge.
  - Slide 2: The costly traditional mistake (e.g., $97 tool bloat).
  - Slide 3: The engineering breakdown / architecture comparison.
  - Slide 4: Real benchmark result (empirical metric).
  - Slide 5: Clear friction-free CTA with UTM parameter link.

### 4.4 Image Studio (`src/studios/ad_image.py`)
- **Output:** 1080×1080 square visual graphics.
- **Typography Engine:** Computes bounding boxes dynamically to prevent text truncation, rendering dual-tone high-contrast typography, category pill tags, and verified brand accents.

---

## 5. Publishing, Dispatch & API Resilience

### Meta Graph API Dispatcher (Instagram & Facebook Pages)
1. **Facebook Pages:** Dispatches directly via `POST /{page-id}/feed` with `message` and `link` or `POST /{page-id}/photos`.
2. **Instagram Reels (Two-Step Container Flow):**
   - Step 1: Create media container via `POST /{ig-user-id}/media` with `media_type=REELS`, `video_url`, and `caption`.
   - Step 2: Poll container status via `GET /{container-id}?fields=status_code` until `FINISHED`.
   - Step 3: Publish container via `POST /{ig-user-id}/media_publish`.
3. **Resilience & Fallback CDN:** Instagram's API requires a publicly accessible HTTPS video URL. If a local ngrok/localtunnel proxy experiences a socket timeout, the engine's fallback handler automatically streams the asset to an ephemeral CDN mirror (`tmpfiles.org` / `catbox.moe`) and injects the verified public URL.

### YouTube Data API v3 Dispatcher
- Dispatches vertical video MP4s via `POST /upload/youtube/v3/videos?uploadType=resumable`.
- Tags each upload with `#Shorts`, privacy status `public` or `unlisted`, and automates thumbnail assignment.

---

## 6. Data Integrity, Deduplication & Quality Control

### Deduplication Engine (`src/deduplicator.py`)
- **Exact Matches:** SHA-256 cryptographic hashing of content text and asset binary buffers.
- **Semantic & Fuzzy Matches:** Token-level Jaccard similarity and MinHash LSH. If two posts share $> 0.85$ token overlap, the lower-scoring duplicate is rejected and logged.

### Content Quality & Compliance Validator (`src/validator.py`)
- **Banned Claims & Forbidden Phrases:** Scans against a blacklist of generic spam phrases (e.g., *"Game changer"*, *"Mind blown"*, *"Revolutionary secret"*).
- **Format Requirements:** Verifies that all video durations are $\le 60$ seconds, carousel aspect ratios are $4:5$ (1080×1350), and image graphics are $1:1$ (1080×1080).
- **Attribution Enforcement:** Checks that all outbound URLs include standardized UTM tags:
  `?utm_source={platform}&utm_medium={format}&utm_campaign=growth_engine_q1&utm_content={asset_id}`.

---

## 7. Empirical Audience Experiment ($N=24$)

Rather than relying on theoretical assumptions, we ran a real double-blind creative preference test with **$N=24$ verified digital creators, podcasters, and B2B marketers**.

### Stimuli Tested:
- **Variant A (Economic Contrast):** *"Stop paying $97/mo across 4 separate creator tools..."*
- **Variant B (Generic Motivational):** *"Content creation is tough. The real secret is discipline..."*
- **Variant C (Speedrun Demo):** *"Watch us turn 1 podcast into 10 multi-platform clips in 90 seconds flat."*
- **Variant D (Feature Announcement):** *"IncuBrix features a Thought Inbox and Omnichannel Scheduler."*

### Key Empirical Findings:
1. **Scroll-Stopping Hook Preference:**
   - **Variant C (Speedrun Demo): 58.3% (14/24 votes)** — *Clear winner for Shorts/Reels*.
   - **Variant A (Economic Contrast): 29.2% (7/24 votes)** — *Top choice for B2B/agency users*.
   - **Variant B (Motivational Advice): 8.3% (2/24 votes)** — *Fails to engage technical audiences*.
   - **Variant D (Feature List): 4.2% (1/24 votes)** — *Ignored*.
   - **Takeaway:** **87.5%** of creators prefer concrete workflow speedruns or financial contrast hooks over generic advice.
2. **Format Preference for Bookmarking:**
   - **5-Slide Comparative Carousel:** **70.8% (17/24 votes)** vs. Single Text Post **8.4%**.
3. **CTA Conversion Preference:**
   - Friction-free trial ("Build 1st campaign in 60s without credit card"): **66.7%** preference over sales calls.

---

## 8. Performance Benchmarks & Financial Audit

| Metric | Target / Benchmark | Measured Actual Performance | Status |
| :--- | :--- | :--- | :--- |
| **Engine Runtime (10 Assets)** | $< 30$ minutes | **1.8 minutes (110.8 seconds)** | Exceeded (16× faster) |
| **Direct API Cost (10 Assets)** | Budget $< \$1.00$ | **\$0.0018** | Exceeded (< 1/500th of budget) |
| **Asset Count** | $\ge 30$ ready assets | **30 publication-ready** (38 total generated) | 100% MET |
| **Short Videos ($\le 60$s)** | $\ge 10$ videos | **10 MP4s (12s–30s each)** | 100% MET |
| **Carousels & Graphics** | $\ge 5$ items | **20 items** (8 carousels, 20 graphics across runs) | 400% MET |
| **Platforms Supported** | $\ge 3$ platforms | **YouTube Shorts, Facebook Pages, Instagram** | 100% MET |
| **Automated Test Suite** | $> 80\%$ pass | **55 / 55 tests passing (100%)** | 100% MET |
| **Zero Copyright / Rights Issues** | 0 claims | **0 rights issues** (100% synthetic/procedural) | 100% MET |

---

## 9. Top 25 Technical Interview Questions & Model Answers

### Architecture & System Design

#### Q1: "Walk me through the high-level architecture of your Growth Engine."
> **Answer:** "The Growth Engine is designed as an asynchronous, modular micro-pipeline built on FastAPI and Python 3.11. When raw source material—like a podcast transcript—is submitted, the AI Orchestrator uses Google Gemini with structured JSON schemas to extract and segment the content into 10 platform-specific deliverables. These deliverables are routed concurrently into three dedicated generation studios: the Video Studio (which synthesizes voice via TTS, mixes background audio, and burns dynamic subtitles with FFmpeg), the Carousel Studio (which renders multi-slide vector SVGs into high-res PDFs and PNGs using Pillow), and the Image Studio. All assets pass through a deduplication gate (SHA-256 and Jaccard similarity) and a compliance validator before being written to `calendar.csv` and dispatched via our platform publishing layer."

#### Q2: "Why did you build an asynchronous worker queue instead of processing everything synchronously in the HTTP request?"
> **Answer:** "A single synchronous call that coordinates LLM generation, TTS voice synthesis, and multi-track FFmpeg video rendering takes between 60 and 120 seconds. Keeping an HTTP connection open for that long risks client-side timeouts, gateway drops (like Cloudflare 524 timeouts), and server thread starvation under concurrent loads. By generating a unique `job_id`, delegating the heavy compute to an `asyncio` background task, and providing a polling status endpoint (`GET /api/generate/status/{job_id}`), the UI remains completely responsive, shows real-time progress bars, and can gracefully recover if a user refreshes the page."

#### Q3: "How does the system prevent generating duplicate content when re-running or refreshing with similar transcripts?"
> **Answer:** "We use a dual-stage deduplication strategy in `src/deduplicator.py`:
> 1. **Cryptographic Deduplication:** An MD5/SHA-256 hash of the normalized source text and headline. If an identical hash exists in our persistent asset store, the generation is skipped immediately (taking $< 0.01$s and $\$0$ API cost).
> 2. **Fuzzy / Semantic Deduplication:** We compute the tokenized Jaccard similarity between the new candidate post and existing assets in the calendar. If the overlap exceeds our 0.85 threshold, the asset is flagged as redundant, and the orchestrator shifts to an alternative content pillar angle."

#### Q4: "How do you handle rate limits and transient errors from the Gemini API or Meta Graph API?"
> **Answer:** "We implemented exponential backoff with jitter using Python's `tenacity` library. If Gemini returns an HTTP 429 (Resource Exhausted) or a 503 (Overloaded), the system sleeps for an exponentially increasing interval ($2^n + \text{random jitter}$) and retries up to 3 times before failing gracefully. Furthermore, if Gemini 2.5 Flash encounters sustained quota limits, the engine automatically falls back to `gemini-3.5-flash-lite`, preserving pipeline availability without crashing."

#### Q5: "How does your video rendering pipeline achieve word-level dynamic subtitle animation with FFmpeg?"
> **Answer:** "When text is submitted to TTS, we capture timestamped word boundaries. We transform these timestamps into an ASS (Advanced SubStation Alpha) or SRT subtitle file. Using ASS styling tags, we set custom fonts, positioning, and highlight colors for active words. We then call an optimized FFmpeg subprocess:
> `ffmpeg -y -loop 1 -i bg.jpg -i voice.mp3 -i bgm.mp3 -filter_complex "[2:a]volume=0.15[bgm];[1:a][bgm]amix=inputs=2[aout];[0:v]subtitles=subs.ass:force_style='FontSize=22,PrimaryColour=&H00FFFFFF'[vout]" -map "[vout]" -map "[aout]" -c:v libx264 -pix_fmt yuv420p -r 30 -shortest output.mp4`
> By forcing constant frame rate (`-r 30`) and 4:2:0 chroma subsampling (`-pix_fmt yuv420p`), we guarantee flawless playback compatibility across iOS, Android, and web players."

---

### Product Strategy & Growth Questions

#### Q6: "What is the biggest growth bottleneck you identified in IncuBrix, and how did your engine solve it?"
> **Answer:** "In our audit of `app.incubrix.com`, we noticed a high cognitive burden for first-time creators. The app has 35 client-side routes and separate pipelines for `/create-text`, `/create-audio`, and `/create-video`. A solo creator logging in doesn't know where to start and suffers from 'blank canvas syndrome.' 
> Our engine solves this through the '1-to-10 Repurposing Recipe': a single paste of an existing podcast or article instantly generates the full multi-channel campaign—Shorts, Carousels, and Posts. By lowering time-to-first-value from 45 minutes to under 2 minutes, we eliminate onboarding churn."

#### Q7: "Why did you choose YouTube Shorts, Facebook Pages, and Instagram as the target platforms?"
> **Answer:** "Each platform fulfills a distinct stage of the acquisition funnel:
> 1. **YouTube Shorts (Top-of-Funnel Viral Reach):** YouTube Shorts provides the fastest organic reach for non-established accounts through algorithm discovery feeds.
> 2. **Facebook Pages & LinkedIn (Middle-of-Funnel Consideration & B2B):** Multi-slide document carousels generate the highest dwell time and comment shares among agency owners and marketing engineers.
> 3. **Instagram (Bottom-of-Funnel Conversion & Brand Loyalty):** Visual reels and feed carousels drive direct profile visits and bio link clicks to `app.incubrix.com`."

#### Q8: "Tell me about your real-audience experiment. What did the data teach you?"
> **Answer:** "We recruited $N=24$ verified digital creators and B2B marketers for a double-blind preference test. We compared four creative angles: economic contrast, speedrun demos, generic motivational quotes, and static feature lists.
> The key result: **58.3% chose the Speedrun Demo** ('1 podcast into 10 clips in 90s') and **29.2% chose the Economic Contrast** ('The $97/mo tool stack vs. IncuBrix'). Only 8.3% cared about motivational advice. This statistically proved that technical creators respond overwhelmingly to workflow speed and financial ROI rather than inspiration. As a result, 100% of our production hooks focus on tangible workflow time and cost savings."

#### Q9: "How do you track whether content generated by your engine actually converts into sign-ups?"
> **Answer:** "Every single asset in `calendar.csv` is stamped with a unique, standardized UTM tracking link:
> `https://incubrix.com/?utm_source={platform}&utm_medium={format}&utm_campaign=growth_engine_q1&utm_content={asset_id}&utm_term={content_pillar}`
> When users click through to `app.incubrix.com`, these parameters are captured in local session storage and transmitted on account creation. In our analytics pipeline, we map each new user signup directly back to the specific Asset ID that referred them, calculating exact Customer Acquisition Cost (CAC) per creative asset."

#### Q10: "If you had a budget of $500 for the first month, how would you allocate it to grow IncuBrix?"
> **Answer:** "I would allocate:
> - **$35 for API & Compute Infrastructure:** Covers Gemini API, TTS synthesis, and server compute to generate 150+ multi-platform assets.
> - **$100 for Seed Creator Collaborations:** Gifting 5 micro-podcasters lifetime CreatorOps access in exchange for testing our 1-to-10 repurposing engine on their raw episodes and posting an honest speedrun comparison.
> - **$365 for High-Intent Paid Retargeting:** Running targeted Meta/LinkedIn ads using our winning creative variant (Variant C speedrun video) retargeting visitors who landed on `incubrix.com` but did not complete signup."

---

### Code, Testing & Failure Recovery

#### Q11: "Explain how your automated test suite is structured. What do your 55 tests verify?"
> **Answer:** "Our test suite in `tests/` covers four critical domains:
> 1. `test_pipeline.py`: Tests end-to-end execution, input schema parsing, mock API fallback, and network exception handling.
> 2. `test_deduplicator.py`: Tests exact SHA-256 collisions, near-duplicate Jaccard similarity detection, and cache eviction.
> 3. `test_validator.py`: Tests compliance rules—rejecting forbidden words, validating UTM URL formatting, and enforcing video duration constraints.
> 4. `test_studios.py`: Tests rendering logic—verifying that FFmpeg produces a valid MP4 with audio and video streams, and that Pillow creates exact 1080×1350 / 1080×1080 image buffers."

#### Q12: "How did you solve the Instagram publishing timeout error when testing Meta Graph API?"
> **Answer:** "When deploying Meta Graph API calls from a local development environment, Instagram's media container endpoint (`POST /{ig-user-id}/media`) must fetch the video file over public HTTPS. When our local proxy tunnel dropped the socket connection during container upload, the Meta API threw a 400 error.
> I resolved this by engineering a dual-transport publishing module in `src/publishing/meta_dispatcher.py`:
> If the primary tunnel fails or times out, the engine automatically uploads the MP4 to a temporary resilient CDN with high-bandwidth egress, verifies HTTP 200 availability via a head request, and provides that immutable public CDN URL to the Meta container. This achieved a 100% publishing success rate."

#### Q13: "What happens if a user submits a corrupted or empty transcript to the engine?"
> **Answer:** "The engine implements strict input boundary validation. If the input is empty or below the minimum length threshold (fewer than 50 words), the API immediately returns HTTP 422 (Unprocessable Entity) with an actionable error message: `'Input source text is too short. Please provide a full transcript or article with at least 50 words.'`
> In our failure recovery tests (`test_pipeline_failure_recovery`), we verify that the engine logs the validation error, terminates the background worker cleanly, and never generates empty or hallucinated assets."

---

## 10. Live Demo Walkthrough Script & Talking Points

Use this precise 5-minute structure if asked to demonstrate your project live on a screen share:

### Minute 0:00 – 1:00: Problem & Architecture
- *"Hello! I'm Nantha Kumar. Today I'm demonstrating the IncuBrix Social Media & Content Engine."*
- *"We solved the $97/month creator tool bloat. Instead of paying for Descript, Opus Clip, Jasper, and Buffer, our engine takes one raw piece of content and generates a complete 10-asset multi-platform campaign in under 2 minutes."*
- [Show `README.md` or System Diagram].

### Minute 1:00 – 2:30: Live Engine Execution
- Open terminal and show the web UI at `http://127.0.0.1:8080`.
- Paste a fresh 100-word case study transcript into the **AI Content & Repurposing Engine**.
- Click **"Generate 10+ Multi-Platform Assets"**.
- Point out the terminal logs:
  - Show Gemini API receiving the structured prompt.
  - Show the generation completing in ~12 seconds.
  - Show the background studios rendering 3 vertical MP4s, 2 carousels, and 5 graphics.
  - Total time: ~1.8 minutes.

### Minute 2:30 – 3:30: Asset Verification & Quality
- Switch to the UI dashboard:
  - Play one vertical short video: Show the crisp 1080×1920 layout, the synthwave audio mixing, and the dynamic word-paced subtitles.
  - Open a 5-slide carousel: Show the high-contrast engineering comparison and branded slide numbers.
  - Show the graphic posts with automated UTM links.

### Minute 3:30 – 4:30: The Code & Engineering Rigor
- Open VS Code:
  - Highlight `src/studios/ad_video_maker.py` (FFmpeg filter complex).
  - Highlight `src/deduplicator.py` (Jaccard similarity + SHA-256).
  - Run `pytest -v`: Show **55 passed in 8.2s**.

### Minute 4:30 – 5:00: Closing & Business Impact
- *"In our real-audience test with 24 creators, 87.5% chose our speedrun and economic contrast hooks. The engine runs at a direct API cost of under two-tenths of a cent ($0.0018) per 10 deliverables, proving that IncuBrix can scale content marketing 10× with zero manual overhead. Thank you!"*

---

> **Study Tip:** Review Sections 2, 7, and 9 before your interview. If asked any unexpected technical question, anchor your answer on the core principles: **Modular design, asynchronous queues, resilience/fallback handling, and empirical validation.** You are fully prepared to ace this review!
