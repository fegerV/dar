"""Seed data for Video Generation Lab scenarios."""

SCENARIOS = [
    {
        "code": "portrait-talking",
        "name": "Portrait Talking Head",
        "description": "Single person speaking directly to camera, head and shoulders",
        "category": "portrait",
        "difficulty": "easy",
        "prompt_template": (
            "A {difficulty} portrait video of a person talking directly to camera, "
            "{camera} camera, {motion} motion, {duration} seconds"
        ),
        "negative_strategy": "avoid multiple faces, avoid distorted features",
        "target_duration_sec": 5,
        "target_camera": "static",
        "target_motion": "subtle",
        "tags": ["portrait", "talking", "headshot"],
    },
    {
        "code": "portrait-walking",
        "name": "Portrait Walking",
        "description": "Person walking naturally in an environment",
        "category": "portrait",
        "difficulty": "medium",
        "prompt_template": (
            "A person walking naturally through a {category} scene, "
            "{camera} camera following, {motion} body movement, {duration} seconds"
        ),
        "negative_strategy": "avoid unnatural gait, avoid floating",
        "target_duration_sec": 5,
        "target_camera": "tracking",
        "target_motion": "moderate",
        "tags": ["portrait", "walking", "movement"],
    },
    {
        "code": "product-showcase",
        "name": "Product Showcase",
        "description": "360-degree product rotation with dramatic lighting",
        "category": "product",
        "difficulty": "medium",
        "prompt_template": (
            "Cinematic product showcase, {camera} rotating around the object, "
            "dramatic lighting, {motion} rotation, {duration} seconds"
        ),
        "negative_strategy": "avoid reflections, avoid unstable rotation",
        "target_duration_sec": 4,
        "target_camera": "orbiting",
        "target_motion": "smooth",
        "tags": ["product", "rotation", "commercial"],
    },
    {
        "code": "food-cooking",
        "name": "Food Cooking Close-up",
        "description": "Close-up of food being prepared or served",
        "category": "food",
        "difficulty": "easy",
        "prompt_template": (
            "Close-up food video, steam rising, {camera} close shot, "
            "{motion} subtle movement, appetizing, {duration} seconds"
        ),
        "negative_strategy": "avoid unappetizing colors, avoid messy presentation",
        "target_duration_sec": 4,
        "target_camera": "close-up",
        "target_motion": "subtle",
        "tags": ["food", "cooking", "close-up"],
    },
    {
        "code": "nature-landscape",
        "name": "Nature Landscape",
        "description": "Sweeping landscape with clouds, water, or vegetation",
        "category": "nature",
        "difficulty": "easy",
        "prompt_template": (
            "Beautiful {category} landscape, {camera} panoramic shot, "
            "clouds moving, {motion} natural flow, {duration} seconds"
        ),
        "negative_strategy": "avoid human artifacts, avoid unnatural colors",
        "target_duration_sec": 5,
        "target_camera": "panoramic",
        "target_motion": "slow",
        "tags": ["nature", "landscape", "scenic"],
    },
    {
        "code": "nature-wildlife",
        "name": "Wildlife Action",
        "description": "Animal in natural habitat performing action",
        "category": "nature",
        "difficulty": "hard",
        "prompt_template": (
            "Wildlife video of animal in natural habitat, {camera} tracking shot, "
            "{motion} fast action, {duration} seconds"
        ),
        "negative_strategy": "avoid anthropomorphism, avoid zoo environments",
        "target_duration_sec": 4,
        "target_camera": "tracking",
        "target_motion": "fast",
        "tags": ["nature", "wildlife", "action"],
    },
    {
        "code": "urban-cityscape",
        "name": "Urban Cityscape",
        "description": "City skyline with traffic and pedestrians",
        "category": "urban",
        "difficulty": "medium",
        "prompt_template": (
            "Urban cityscape, {camera} establishing shot, traffic flowing, "
            "{motion} time-lapse feel, {duration} seconds"
        ),
        "negative_strategy": "avoid empty streets, avoid dystopian look",
        "target_duration_sec": 5,
        "target_camera": "wide",
        "target_motion": "moderate",
        "tags": ["urban", "city", "skyline"],
    },
    {
        "code": "urban-street",
        "name": "Street Level Action",
        "description": "Street-level view with people and activity",
        "category": "urban",
        "difficulty": "medium",
        "prompt_template": (
            "Street-level urban video, {camera} handheld feel, pedestrians walking, "
            "{motion} natural movement, {duration} seconds"
        ),
        "negative_strategy": "avoid crowd scenes, avoid chaos",
        "target_duration_sec": 4,
        "target_camera": "handheld",
        "target_motion": "moderate",
        "tags": ["urban", "street", "people"],
    },
    {
        "code": "abstract-particles",
        "name": "Abstract Particles",
        "description": "Flowing particle systems and fluid dynamics",
        "category": "abstract",
        "difficulty": "easy",
        "prompt_template": (
            "Abstract particle animation, {camera} fluid movement, "
            "colorful particles, {motion} flowing, {duration} seconds"
        ),
        "negative_strategy": "avoid recognizable objects, avoid static scenes",
        "target_duration_sec": 5,
        "target_camera": "fluid",
        "target_motion": "flowing",
        "tags": ["abstract", "particles", "fluid"],
    },
    {
        "code": "abstract-geometric",
        "name": "Geometric Shapes",
        "description": "Morphing geometric shapes and patterns",
        "category": "abstract",
        "difficulty": "medium",
        "prompt_template": (
            "Geometric shapes morphing, {camera} rotating view, "
            "{motion} smooth transitions, {duration} seconds"
        ),
        "negative_strategy": "avoid organic shapes, avoid sharp edges",
        "target_duration_sec": 4,
        "target_camera": "rotating",
        "target_motion": "smooth",
        "tags": ["abstract", "geometric", "shapes"],
    },
    {
        "code": "fashion-runway",
        "name": "Fashion Runway",
        "description": "Model walking on runway with dramatic lighting",
        "category": "fashion",
        "difficulty": "medium",
        "prompt_template": (
            "Fashion runway walk, {camera} tracking shot, dramatic lighting, "
            "{motion} confident stride, {duration} seconds"
        ),
        "negative_strategy": "avoid casual clothing, avoid messy hair",
        "target_duration_sec": 5,
        "target_camera": "tracking",
        "target_motion": "confident",
        "tags": ["fashion", "runway", "model"],
    },
    {
        "code": "fashion-product",
        "name": "Fashion Product Detail",
        "description": "Close-up of fabric texture or accessory detail",
        "category": "fashion",
        "difficulty": "easy",
        "prompt_template": (
            "Fashion detail close-up, fabric texture, {camera} macro shot, "
            "{motion} subtle movement, {duration} seconds"
        ),
        "negative_strategy": "avoid wrinkles, avoid poor lighting",
        "target_duration_sec": 4,
        "target_camera": "macro",
        "target_motion": "subtle",
        "tags": ["fashion", "detail", "texture"],
    },
    {
        "code": "music-performance",
        "name": "Music Performance",
        "description": "Musician performing on stage or studio",
        "category": "music",
        "difficulty": "hard",
        "prompt_template": (
            "Music performance video, {camera} multi-angle, stage lighting, "
            "{motion} energetic, {duration} seconds"
        ),
        "negative_strategy": "avoid lip-sync issues, avoid instrument errors",
        "target_duration_sec": 5,
        "target_camera": "multi-angle",
        "target_motion": "energetic",
        "tags": ["music", "performance", "stage"],
    },
    {
        "code": "sports-action",
        "name": "Sports Action",
        "description": "Athlete performing sports action",
        "category": "sports",
        "difficulty": "hard",
        "prompt_template": (
            "Sports action video, {camera} dynamic tracking, "
            "{motion} explosive movement, {duration} seconds"
        ),
        "negative_strategy": "avoid injury depiction, avoid slow motion",
        "target_duration_sec": 4,
        "target_camera": "dynamic",
        "target_motion": "explosive",
        "tags": ["sports", "action", "athlete"],
    },
    {
        "code": "gaming-gameplay",
        "name": "Gaming Gameplay",
        "description": "Game screen or gamer reaction",
        "category": "gaming",
        "difficulty": "medium",
        "prompt_template": (
            "Gaming video, {camera} screen capture or reaction shot, "
            "{motion} fast-paced action, {duration} seconds"
        ),
        "negative_strategy": "avoid boring gameplay, avoid low quality graphics",
        "target_duration_sec": 5,
        "target_camera": "mixed",
        "target_motion": "fast",
        "tags": ["gaming", "gameplay", "esports"],
    },
]


def get_scenario_data() -> list[dict]:
    """Get all scenario seed data."""
    return SCENARIOS


def get_scenario_by_code(code: str) -> dict | None:
    """Get scenario data by code."""
    for scenario in SCENARIOS:
        if scenario["code"] == code:
            return scenario
    return None
