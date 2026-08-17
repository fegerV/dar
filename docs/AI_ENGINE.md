# ДарАгент MVP — AI Engine Specification v0.2

## Часть B — AI Engine

### 1. Creative Brief JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://daragent.ru/schemas/creative-brief.json",
  "title": "Creative Brief",
  "description": "Структурированное описание поздравления",
  "type": "object",
  "required": ["occasion", "recipient", "sender"],
  "properties": {
    "occasion": {
      "type": "string",
      "enum": ["birthday", "wedding", "anniversary", "new_year", "march_8", "february_23", "graduation", "promotion", "retirement", "professional_holiday", "other"]
    },
    "recipient": {
      "type": "object",
      "required": ["name", "relationship"],
      "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 255},
        "age": {"type": "integer", "minimum": 0, "maximum": 120},
        "gender": {"type": "string", "enum": ["male", "female", "other"]},
        "relationship": {"type": "string", "minLength": 1, "maxLength": 100}
      }
    },
    "sender": {
      "type": "object",
      "required": ["name", "relationship"],
      "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 255},
        "relationship": {"type": "string", "minLength": 1, "maxLength": 100}
      }
    },
    "personality": {
      "type": "array",
      "items": {"type": "string"},
      "default": []
    },
    "interests": {
      "type": "array",
      "items": {"type": "string"},
      "default": []
    },
    "tone": {
      "type": "object",
      "properties": {
        "humor": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
        "emotion": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
        "seriousness": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
        "warmth": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5}
      }
    },
    "style": {
      "type": "string",
      "default": "cinematic",
      "enum": ["cinematic", "documentary", "news", "interview", "trailer", "music_video", "cartoon"]
    },
    "duration": {
      "type": "integer",
      "minimum": 15,
      "maximum": 120,
      "default": 60
    },
    "surprise_level": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "default": 0.5
    },
    "additional_info": {
      "type": "string",
      "maxLength": 1000
    }
  }
}
```

---

### 2. Template JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://daragent.ru/schemas/template.json",
  "title": "Template",
  "description": "Шаблон поздравления",
  "type": "object",
  "required": ["template_id", "version", "name", "category", "requirements", "variables", "scenes"],
  "properties": {
    "template_id": {
      "type": "string",
      "pattern": "^[a-z0-9_]+$"
    },
    "version": {
      "type": "integer",
      "minimum": 1
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "description": {
      "type": "string"
    },
    "category": {
      "type": "string",
      "enum": ["cinematic", "humor", "romantic", "family", "corporate", "special"]
    },
    "price_tier": {
      "type": "string",
      "enum": ["basic", "standard", "premium", "exclusive"],
      "default": "standard"
    },
    "requirements": {
      "type": "object",
      "properties": {
        "occasion": {
          "type": "array",
          "items": {"type": "string"}
        },
        "relationships": {
          "type": "array",
          "items": {"type": "string"}
        },
        "min_age": {
          "type": "integer",
          "minimum": 0
        },
        "max_age": {
          "type": "integer",
          "maximum": 120
        },
        "genders": {
          "type": "array",
          "items": {"type": "string", "enum": ["male", "female", "other"]}
        },
        "styles": {
          "type": "array",
          "items": {"type": "string"}
        },
        "min_duration": {
          "type": "integer"
        },
        "max_duration": {
          "type": "integer"
        }
      }
    },
    "variables": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Список переменных, которые шаблон использует (например: recipient.name, recipient.age)"
    },
    "scenes": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/scene"
      }
    },
    "conditions": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/condition"
      }
    },
    "prompts": {
      "type": "object",
      "description": "Шаблоны prompt'ов для каждой сцены"
    },
    "audio_settings": {
      "type": "object",
      "properties": {
        "music_genre": {"type": "string"},
        "music_mood": {"type": "string"},
        "voice_gender": {"type": "string", "enum": ["male", "female", "any"]},
        "voice_style": {"type": "string"},
        "background_music_volume": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "render_settings": {
      "type": "object",
      "properties": {
        "resolution": {"type": "string", "enum": ["720p", "1080p", "4k"]},
        "fps": {"type": "integer", "enum": [24, 25, 30, 60]},
        "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1", "4:5"]},
        "format": {"type": "string", "enum": ["mp4", "mov", "webm"]}
      }
    },
    "fallback_scene_id": {
      "type": "string",
      "description": "ID сцены для использования при ошибке генерации"
    }
  },
  "$defs": {
    "scene": {
      "type": "object",
      "required": ["id", "scene_order", "scene_type", "duration", "prompt_template"],
      "properties": {
        "id": {"type": "string"},
        "scene_order": {"type": "integer", "minimum": 1},
        "scene_type": {
          "type": "string",
          "enum": ["intro", "hero", "story", "climax", "resolution", "outro", "transition"]
        },
        "duration": {
          "type": "integer",
          "minimum": 1,
          "description": "Длительность сцены в секундах"
        },
        "prompt_template": {
          "type": "string",
          "description": "Шаблон prompt для генерации видео/изображения"
        },
        "voice_text_template": {
          "type": "string",
          "description": "Шаблон текста для озвучки"
        },
        "voice_settings": {
          "type": "object",
          "properties": {
            "voice_id": {"type": "string"},
            "speed": {"type": "number", "minimum": 0.5, "maximum": 2.0},
            "pitch": {"type": "number", "minimum": -12, "maximum": 12},
            "emotion": {"type": "string"}
          }
        },
        "visual_style": {
          "type": "object",
          "properties": {
            "camera_angle": {"type": "string"},
            "lighting": {"type": "string"},
            "color_grading": {"type": "string"},
            "negative_prompt": {"type": "string"}
          }
        },
        "music_cue": {
          "type": "object",
          "properties": {
            "cue_point": {"type": "string"},
            "intensity": {"type": "string", "enum": ["low", "medium", "high"]}
          }
        },
        "condition_json": {
          "$ref": "#/$defs/condition"
        },
        "variables_required": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "condition": {
      "type": "object",
      "required": ["field", "operator", "value", "then"],
      "properties": {
        "field": {
          "type": "string",
          "description": "Поле из Creative Brief (например: recipient.age)"
        },
        "operator": {
          "type": "string",
          "enum": ["==", "!=", ">", "<", ">=", "<=", "contains", "in"]
        },
        "value": {
          "description": "Значение для сравнения"
        },
        "then": {
          "type": "string",
          "description": "ID сцены или действие при истинном условии"
        },
        "else": {
          "type": "string",
          "description": "ID сцены или действие при ложном условии"
        }
      }
    }
  }
}
```

---

### 3. Scene Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://daragent.ru/schemas/scene.json",
  "title": "Scene",
  "type": "object",
  "required": ["id", "scene_order", "scene_type", "duration", "prompt_template"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^scene_[0-9]+$"
    },
    "scene_order": {
      "type": "integer",
      "minimum": 1
    },
    "scene_type": {
      "type": "string",
      "enum": ["intro", "hero", "story", "climax", "resolution", "outro", "transition"]
    },
    "duration": {
      "type": "integer",
      "minimum": 1,
      "maximum": 60
    },
    "prompt_template": {
      "type": "string",
      "minLength": 10
    },
    "compiled_prompt": {
      "type": "string",
      "description": "Prompt после компиляции с подставленными переменными"
    },
    "voice_text_template": {
      "type": "string"
    },
    "compiled_voice_text": {
      "type": "string"
    },
    "generated_asset_id": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "generating", "ready", "failed"]
    }
  }
}
```

---

### 4. Recommendation Engine

#### Алгоритм scoring (MVP)

```python
def calculate_template_score(template, creative_brief):
    """
    Scoring algorithm for template recommendation.
    Returns score between 0.0 and 1.0
    """
    
    # 1. Occasion match (25%)
    occasion_match = 0.0
    if template.requirements.get('occasion'):
        if creative_brief['occasion'] in template.requirements['occasion']:
            occasion_match = 1.0
    else:
        occasion_match = 0.5  # No preference = neutral
    
    # 2. Relationship match (20%)
    relationship_match = 0.0
    if template.requirements.get('relationships'):
        if creative_brief['recipient']['relationship'] in template.requirements['relationships']:
            relationship_match = 1.0
    else:
        relationship_match = 0.5
    
    # 3. Tone match (20%)
    tone_match = calculate_tone_similarity(
        creative_brief.get('tone', {}),
        template.tone_profile or {}
    )
    
    # 4. Interests match (15%)
    interests_match = calculate_interests_overlap(
        creative_brief.get('interests', []),
        template.interests_keywords or []
    )
    
    # 5. Age match (5%)
    age_match = 1.0
    if template.requirements.get('min_age'):
        if creative_brief['recipient'].get('age', 0) < template.requirements['min_age']:
            age_match = 0.0
    if template.requirements.get('max_age'):
        if creative_brief['recipient'].get('age', 0) > template.requirements['max_age']:
            age_match = 0.0
    
    # 6. Gender match (5%)
    gender_match = 1.0
    if template.requirements.get('genders'):
        recipient_gender = creative_brief['recipient'].get('gender')
        if recipient_gender and recipient_gender not in template.requirements['genders']:
            gender_match = 0.0
    
    # 7. Style match (5%)
    style_match = 1.0
    if template.requirements.get('styles'):
        if creative_brief.get('style') not in template.requirements['styles']:
            style_match = 0.5
    
    # 8. Duration match (5%)
    duration_match = 1.0
    brief_duration = creative_brief.get('duration', 60)
    if template.requirements.get('min_duration'):
        if brief_duration < template.requirements['min_duration']:
            duration_match = 0.5
    if template.requirements.get('max_duration'):
        if brief_duration > template.requirements['max_duration']:
            duration_match = 0.5
    
    # Calculate base score
    base_score = (
        occasion_match * 0.25 +
        relationship_match * 0.20 +
        tone_match * 0.20 +
        interests_match * 0.15 +
        age_match * 0.05 +
        gender_match * 0.05 +
        style_match * 0.05 +
        duration_match * 0.05
    )
    
    # Bonuses
    popularity_bonus = min(template.popularity_score / 1000, 0.1)  # max 0.1
    conversion_bonus = min((template.conversion_rate or 0) * 0.5, 0.05)  # max 0.05
    novelty_bonus = 0.05 if template.is_new else 0.0  # New templates get boost
    
    final_score = min(base_score + popularity_bonus + conversion_bonus + novelty_bonus, 1.0)
    
    return round(final_score, 3)


def calculate_tone_similarity(brief_tone, template_tone):
    """Calculate cosine similarity between tone vectors"""
    if not brief_tone or not template_tone:
        return 0.5
    
    keys = ['humor', 'emotion', 'seriousness', 'warmth']
    brief_vector = [brief_tone.get(k, 0.5) for k in keys]
    template_vector = [template_tone.get(k, 0.5) for k in keys]
    
    dot_product = sum(a * b for a, b in zip(brief_vector, template_vector))
    magnitude_brief = math.sqrt(sum(a * a for a in brief_vector))
    magnitude_template = math.sqrt(sum(b * b for b in template_vector))
    
    if magnitude_brief == 0 or magnitude_template == 0:
        return 0.5
    
    return dot_product / (magnitude_brief * magnitude_template)


def calculate_interests_overlap(brief_interests, template_keywords):
    """Calculate Jaccard similarity between interests sets"""
    if not brief_interests or not template_keywords:
        return 0.5
    
    brief_set = set(i.lower() for i in brief_interests)
    template_set = set(k.lower() for k in template_keywords)
    
    intersection = len(brief_set & template_set)
    union = len(brief_set | template_set)
    
    if union == 0:
        return 0.5
    
    return intersection / union
```

#### Response format

```json
{
  "project_id": "770e8400-e29b-41d4-a716-446655440002",
  "recommendations": [
    {
      "template_id": "550e8400-e29b-41d4-a716-446655440003",
      "template_name": "Герой фильма",
      "score": 0.94,
      "reason": "Подходит для близкого друга с хорошим чувством юмора",
      "preview_url": "https://storage.daragent.ru/previews/movie_hero.mp4",
      "price": 299,
      "category": "cinematic",
      "duration_estimate": 60,
      "score_breakdown": {
        "occasion_match": 1.0,
        "relationship_match": 1.0,
        "tone_match": 0.92,
        "interests_match": 0.85,
        "age_match": 1.0,
        "gender_match": 1.0,
        "style_match": 1.0,
        "duration_match": 1.0,
        "popularity_bonus": 0.06,
        "conversion_bonus": 0.03,
        "novelty_bonus": 0.0
      }
    }
  ],
  "generated_at": "2025-01-15T11:50:00Z"
}
```

---

### 5. Prompt Compiler

#### System prompt template

```
You are a cinematic video prompt compiler for DarAgent greeting video generation system.
Your task is to create detailed, production-ready prompts for AI video generation.

RULES:
1. Always include: subject, action, setting, lighting, camera, style
2. Be specific about visual details
3. Include negative prompts to avoid common issues
4. Keep prompts under 500 characters
5. Use professional cinematography terminology

OUTPUT FORMAT:
Return JSON with: {
  "prompt": "...",
  "negative_prompt": "...",
  "style_preset": "...",
  "camera_params": {...}
}
```

#### Compilation algorithm

```python
class PromptCompiler:
    def __init__(self):
        self.system_prompt = load_system_prompt()
    
    def compile(self, template_scene, creative_brief, variables):
        """
        Compile scene prompt with creative brief data
        
        Args:
            template_scene: Scene from template with prompt_template
            creative_brief: User's creative brief
            variables: Resolved variables (recipient.name, etc.)
        
        Returns:
            Compiled prompt ready for AI generation
        """
        
        # 1. Extract prompt template
        prompt_template = template_scene['prompt_template']
        
        # 2. Replace variables
        compiled_prompt = self._substitute_variables(prompt_template, variables)
        
        # 3. Add style modifiers from brief
        style_modifiers = self._get_style_modifiers(creative_brief)
        compiled_prompt = f"{compiled_prompt}. {style_modifiers}"
        
        # 4. Add visual style from scene
        if template_scene.get('visual_style'):
            visual_additions = self._format_visual_style(template_scene['visual_style'])
            compiled_prompt = f"{compiled_prompt}. {visual_additions}"
        
        # 5. Generate negative prompt
        negative_prompt = self._generate_negative_prompt(
            template_scene, 
            creative_brief
        )
        
        # 6. Build camera parameters
        camera_params = self._extract_camera_params(template_scene)
        
        # 7. Determine style preset
        style_preset = self._determine_style_preset(creative_brief.get('style', 'cinematic'))
        
        return {
            "prompt": compiled_prompt,
            "negative_prompt": negative_prompt,
            "style_preset": style_preset,
            "camera_params": camera_params,
            "seed": random.randint(1, 1000000)
        }
    
    def _substitute_variables(self, template, variables):
        """Replace {{variable}} placeholders with actual values"""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def _get_style_modifiers(self, brief):
        """Get style modifiers based on tone"""
        modifiers = []
        tone = brief.get('tone', {})
        
        if tone.get('humor', 0) > 0.7:
            modifiers.append("bright colors, playful atmosphere")
        if tone.get('emotion', 0) > 0.7:
            modifiers.append("warm lighting, intimate framing")
        if tone.get('seriousness', 0) > 0.7:
            modifiers.append("dramatic lighting, serious mood")
        if tone.get('warmth', 0) > 0.7:
            modifiers.append("golden hour, cozy atmosphere")
        
        return ", ".join(modifiers) if modifiers else ""
    
    def _generate_negative_prompt(self, scene, brief):
        """Generate negative prompt to avoid common issues"""
        negatives = [
            "blurry", "low quality", "distorted", "ugly", 
            "deformed hands", "extra limbs", "bad anatomy",
            "text overlay", "watermark", "logo"
        ]
        
        # Add scene-specific negatives
        if scene.get('visual_style', {}).get('negative_prompt'):
            negatives.extend(scene['visual_style']['negative_prompt'].split(','))
        
        return ", ".join(negatives)
    
    def _determine_style_preset(self, style):
        """Map style to AI generator preset"""
        style_map = {
            "cinematic": "cinematic Filmstock",
            "documentary": "documentary realism",
            "news": "broadcast news",
            "interview": "talk show",
            "trailer": "movie trailer",
            "music_video": "music video aesthetic",
            "cartoon": "3D animation"
        }
        return style_map.get(style, "cinematic")
```

#### Example compilation

**Input:**
```json
{
  "prompt_template": "{{recipient.name}}, a {{recipient.age}} year old {{recipient.gender}}, stands confidently as the hero of the story",
  "visual_style": {
    "camera_angle": "low angle shot",
    "lighting": "dramatic side lighting",
    "color_grading": "teal and orange"
  }
}

{
  "recipient": {
    "name": "Александр",
    "age": 40,
    "gender": "male"
  },
  "tone": {
    "humor": 0.8,
    "emotion": 0.6
  },
  "style": "cinematic"
}
```

**Output:**
```json
{
  "prompt": "Александр, a 40 year old male, stands confidently as the hero of the story. bright colors, playful atmosphere. low angle shot, dramatic side lighting, teal and orange color grading",
  "negative_prompt": "blurry, low quality, distorted, ugly, deformed hands, extra limbs, bad anatomy, text overlay, watermark, logo",
  "style_preset": "cinematic Filmstock",
  "camera_params": {
    "angle": "low angle",
    "lens": "35mm",
    "aperture": "f/2.8"
  },
  "seed": 482951
}
```

---

### 6. Generation State Machine

```python
from enum import Enum
from typing import Optional, Dict, Any

class GenerationStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    PREPARING = "preparing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_ASSETS = "generating_assets"
    GENERATING_VIDEO = "generating_video"
    RENDERING = "rendering"
    UPLOADING = "uploading"
    READY = "ready"
    FAILED = "failed"

class GenerationStateMachine:
    """
    State machine for managing video generation lifecycle
    """
    
    # Valid state transitions
    TRANSITIONS = {
        GenerationStatus.CREATED: [GenerationStatus.QUEUED, GenerationStatus.FAILED],
        GenerationStatus.QUEUED: [GenerationStatus.PREPARING, GenerationStatus.FAILED],
        GenerationStatus.PREPARING: [
            GenerationStatus.GENERATING_SCRIPT, 
            GenerationStatus.FAILED
        ],
        GenerationStatus.GENERATING_SCRIPT: [
            GenerationStatus.GENERATING_ASSETS,
            GenerationStatus.GENERATING_VIDEO,
            GenerationStatus.FAILED
        ],
        GenerationStatus.GENERATING_ASSETS: [
            GenerationStatus.GENERATING_VIDEO,
            GenerationStatus.FAILED
        ],
        GenerationStatus.GENERATING_VIDEO: [
            GenerationStatus.RENDERING,
            GenerationStatus.FAILED
        ],
        GenerationStatus.RENDERING: [
            GenerationStatus.UPLOADING,
            GenerationStatus.FAILED
        ],
        GenerationStatus.UPLOADING: [
            GenerationStatus.READY,
            GenerationStatus.FAILED
        ],
        GenerationStatus.READY: [],  # Terminal state
        GenerationStatus.FAILED: [GenerationStatus.QUEUED]  # Can retry
    }
    
    MAX_RETRIES = 3
    
    def can_transition(self, current: GenerationStatus, next: GenerationStatus) -> bool:
        """Check if transition is valid"""
        return next in self.TRANSITIONS.get(current, [])
    
    def transition(
        self, 
        generation: Generation, 
        new_status: GenerationStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Execute state transition
        
        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_transition(generation.status, new_status):
            logger.error(
                f"Invalid transition: {generation.status} -> {new_status}"
            )
            return False
        
        # Update status
        generation.status = new_status
        
        # Handle errors
        if new_status == GenerationStatus.FAILED:
            generation.retry_count += 1
            generation.error_message = error_message
            
            if generation.retry_count >= self.MAX_RETRIES:
                logger.error(f"Max retries reached for generation {generation.id}")
                return True
            
            # Auto-retry logic
            if self._should_retry(generation):
                generation.status = GenerationStatus.QUEUED
                self._schedule_retry(generation)
        
        # Clear errors on success
        elif new_status != GenerationStatus.FAILED:
            generation.error_message = None
        
        # Track timestamps
        if new_status == GenerationStatus.PREPARING and not generation.started_at:
            generation.started_at = datetime.utcnow()
        
        if new_status in [GenerationStatus.READY, GenerationStatus.FAILED]:
            if not generation.completed_at:
                generation.completed_at = datetime.utcnow()
        
        generation.save()
        return True
    
    def _should_retry(self, generation: Generation) -> bool:
        """Determine if generation should be auto-retried"""
        # Don't retry certain errors
        non_retryable_errors = [
            'TEMPLATE_NOT_FOUND',
            'INVALID_BRIEF',
            'PAYMENT_REQUIRED'
        ]
        
        if generation.error_code in non_retryable_errors:
            return False
        
        return generation.retry_count < self.MAX_RETRIES
    
    def _schedule_retry(self, generation: Generation):
        """Schedule generation for retry"""
        # Add back to queue with delay
        delay_seconds = min(2 ** generation.retry_count * 60, 3600)  # Exponential backoff
        redis_client.zadd(
            'generation_retry_queue',
            {str(generation.id): time.time() + delay_seconds}
        )
```

---

### 7. Worker Queues Architecture

```python
# Queue configuration
QUEUES = {
    'script_queue': {
        'priority': 'high',
        'workers': 2,
        'timeout': 300,
        'retry_limit': 3
    },
    'image_queue': {
        'priority': 'high',
        'workers': 5,
        'timeout': 120,
        'retry_limit': 3
    },
    'video_queue': {
        'priority': 'medium',
        'workers': 3,
        'timeout': 600,
        'retry_limit': 2
    },
    'voice_queue': {
        'priority': 'high',
        'workers': 3,
        'timeout': 60,
        'retry_limit': 3
    },
    'render_queue': {
        'priority': 'medium',
        'workers': 2,
        'timeout': 900,
        'retry_limit': 2
    },
    'upload_queue': {
        'priority': 'low',
        'workers': 2,
        'timeout': 300,
        'retry_limit': 5
    }
}

# Priority levels for jobs
JOB_PRIORITIES = {
    'payment_user': 0,  # Highest - user just paid
    'paid': 1,
    'free': 2,
    'retry': 3  # Lowest - will be retried later
}
```

---

### 8. Idempotency & Retry Strategy

```python
class IdempotencyHandler:
    """
    Handle idempotent operations for generations and payments
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.lock_timeout = 300  # 5 minutes
    
    def acquire_lock(self, key: str, timeout: int = None) -> bool:
        """Acquire distributed lock"""
        timeout = timeout or self.lock_timeout
        return self.redis.set(
            f'idempotency:lock:{key}',
            '1',
            nx=True,
            ex=timeout
        )
    
    def release_lock(self, key: str):
        """Release distributed lock"""
        self.redis.delete(f'idempotency:lock:{key}')
    
    def check_idempotency(self, idempotency_key: str) -> Optional[Dict]:
        """Check if operation was already processed"""
        cached = self.redis.get(f'idempotency:result:{idempotency_key}')
        if cached:
            return json.loads(cached)
        return None
    
    def cache_result(self, idempotency_key: str, result: Dict, ttl: int = 3600):
        """Cache operation result"""
        self.redis.setex(
            f'idempotency:result:{idempotency_key}',
            ttl,
            json.dumps(result)
        )
    
    @contextmanager
    def idempotent_operation(self, idempotency_key: str, ttl: int = 3600):
        """Context manager for idempotent operations"""
        # Check if already processed
        cached_result = self.check_idempotency(idempotency_key)
        if cached_result:
            yield cached_result
            return
        
        # Acquire lock
        if not self.acquire_lock(idempotency_key):
            raise IdempotencyConflictError(
                f"Operation {idempotency_key} is already being processed"
            )
        
        try:
            result = yield None
            if result is not None:
                self.cache_result(idempotency_key, result, ttl)
        finally:
            self.release_lock(idempotency_key)


class RetryStrategy:
    """Exponential backoff retry strategy"""
    
    def __init__(self, max_retries: int = 3, base_delay: int = 60):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def get_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt number"""
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, 0.1 * delay)
        return min(delay + jitter, 3600)  # Cap at 1 hour
    
    def should_retry(self, attempt: int, error_type: str) -> bool:
        """Determine if retry should be attempted"""
        if attempt >= self.max_retries:
            return False
        
        non_retryable = [
            'VALIDATION_ERROR',
            'NOT_FOUND',
            'UNAUTHORIZED',
            'FORBIDDEN'
        ]
        
        return error_type not in non_retryable
```
