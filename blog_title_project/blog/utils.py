from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
import logging
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TitleGenerator:
    """
    AI-powered blog title generator using transformer models
    """
    
    def __init__(self):
        self.summarizer = None
        self.tokenizer = None
        self.model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models for title generation"""
        try:
            logger.info("Initializing title generation models...")
            
            # Option 1: Use pipeline (simpler, good for quick setup)
            self.summarizer = pipeline(
                "summarization",
                model="Michau/t5-base-en-generate-headline",  # Lightweight BART model fine tuned for titles
                tokenizer="Michau/t5-base-en-generate-headline",
                device=-1,  # Use CPU (-1), or 0 for GPU
                framework="pt"  # PyTorch
            )
            
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            # Fallback to rule-based generation
            self.summarizer = None
    
    def clean_content(self, content: str) -> str:
        """Clean and prepare content for processing"""
        if not content:
            return ""

        content = content.replace("’", "'").replace("‘", "'")  # curly apostrophes
        content = content.replace("“", '"').replace("”", '"')  # curly double quotes
        
        # Remove extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove special characters that might confuse the model
        content = re.sub(r'[^\w\s.,!?-]', '', content)
        
        # Limit content length (BART has 1024 token limit)
        if len(content) > 800:  # Conservative limit
            # Try to cut at sentence boundary
            sentences = content.split('.')
            content = ""
            for sentence in sentences:
                if len(content + sentence) > 800:
                    break
                content += sentence + "."
            
            if not content:
                content = content[:800] + "..."
        
        return content
    
    def generate_titles(self, content: str, num_titles: int = 3) -> List[Dict[str, Any]]:
        """Generate blog titles from content"""
        try:
            cleaned_content = self.clean_content(content)
            
            if len(cleaned_content.split()) < 10:
                logger.warning("Content too short for AI generation, using fallback")
                return self._fallback_titles(cleaned_content, num_titles)
            
            if self.summarizer is None:
                logger.warning("AI model not available, using rule-based generation")
                return self._rule_based_titles(cleaned_content, num_titles)
            
            titles = []
            # prompt_content = f"Generate a short and catchy blog post title for the following article:\n\n{cleaned_content}\n\nTitle:"
            # Generate multiple titles with different parameters
            for i in range(min(num_titles, 5)):  # Max 5 attempts
                try:
                    # Vary the generation parameters for diversity
                    max_length = 15 
                    min_length = 8
                    
                    result = self.summarizer(
                        "headline: "+cleaned_content,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=True,
                        temperature=0.9 + (i * 0.1),  # Increase randomness
                        num_beams=3,
                        length_penalty=1.0,
                        early_stopping=True
                    )
                    
                    if result and len(result) > 0:
                        title = result[0]['summary_text'].strip()
                        
                        # Clean up the title
                        title = self._clean_title(title)
                        
                        # Check for duplicates and minimum quality
                        if title and len(title.split()) >= 3 and title not in [t['title'] for t in titles]:
                            confidence = max(0.9 - (i * 0.1), 0.6)  # Decrease confidence for later attempts
                            titles.append({
                                'title': title,
                                'confidence': round(confidence, 2),
                                'method': 'ai',
                            })
                        
                except Exception as e:
                    logger.warning(f"Error generating title {i+1}: {str(e)}")
                    continue
            
            # If we don't have enough titles, add rule-based ones
            while len(titles) < num_titles:
                fallback = self._create_smart_fallback_title(cleaned_content, len(titles))
                if fallback not in [t['title'] for t in titles]:
                    titles.append(fallback)
                else:
                    break  # Avoid infinite loop
            
            return titles[:num_titles]
            
        except Exception as e:
            logger.error(f"Error in title generation: {str(e)}")
            return self._fallback_titles(content, num_titles)
    
    def _clean_title(self, title: str) -> str:
        """Clean up generated title"""
        if not title:
            return ""
        
        # Remove quotes and clean punctuation
        title = title.replace('"', '').replace("'", "'").replace('`', "'")
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove trailing periods if present
        title = title.rstrip('.')
        
        # Capitalize properly
        words = title.split()
        if not words:
            return ""
        
        # Words that should always be capitalized
        always_caps = {'AI', 'API', 'ML', 'NLP', 'IoT', 'SaaS', 'CEO', 'CTO', 'IT', 'UI', 'UX', 'SEO', 'ROI'}
        
        # Words that should be lowercase (unless first word)
        articles_prepositions = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        cleaned_words = []
        for i, word in enumerate(words):
            word_upper = word.upper()
            word_lower = word.lower()
            
            if word_upper in always_caps:
                cleaned_words.append(word_upper)
            elif i == 0:  # First word is always capitalized
                cleaned_words.append(word.capitalize())
            elif word_lower in articles_prepositions:
                cleaned_words.append(word_lower)
            elif len(word) > 3:  # Capitalize longer words
                cleaned_words.append(word.capitalize())
            else:
                cleaned_words.append(word_lower)
        
        return ' '.join(cleaned_words)
    
    def _rule_based_titles(self, content: str, num_titles: int) -> List[Dict[str, Any]]:
        """Generate titles using rule-based approach when AI is not available"""
        words = content.split()
        
        # Extract potential key phrases (2-3 word combinations)
        key_phrases = []
        for i in range(len(words) - 1):
            phrase = ' '.join(words[i:i+2]).title()
            if len(phrase) > 6:  # Skip very short phrases
                key_phrases.append(phrase)
        
        # Title templates
        templates = [
            "Understanding {}",
            "A Complete Guide to {}",
            "Everything You Need to Know About {}",
            "The Future of {}",
            "How to Master {}",
            "The Ultimate {} Guide",
            "Exploring {}",
            "The Power of {}",
            "Why {} Matters",
            "Getting Started with {}"
        ]
        
        titles = []
        used_phrases = set()
        
        for i in range(min(num_titles, len(key_phrases))):
            if i < len(key_phrases) and key_phrases[i] not in used_phrases:
                template = templates[i % len(templates)]
                title = template.format(key_phrases[i])
                used_phrases.add(key_phrases[i])
                
                titles.append({
                    'title': title,
                    'confidence': 0.7 - (i * 0.1),
                    'method': 'rule_based',
                })
        
        return titles
    
    def _create_smart_fallback_title(self, content: str, index: int) -> Dict[str, Any]:
        """Create intelligent fallback titles"""
        words = content.split()
        
        # Try to find meaningful phrases
        important_words = []
        for word in words[:20]:  # Check first 20 words
            if len(word) > 4 and word.lower() not in {'this', 'that', 'with', 'have', 'been', 'will', 'from', 'they', 'were', 'said', 'each', 'which', 'their', 'would', 'there', 'could', 'other'}:
                important_words.append(word.title())
        
        fallback_patterns = [
            f"Insights on {' '.join(important_words[:2])}",
            f"Understanding {' '.join(important_words[:2])}",
            f"A Deep Dive into {' '.join(important_words[:2])}",
            f"The Impact of {' '.join(important_words[:2])}",
            f"Exploring {' '.join(important_words[:2])}"
        ]
        
        if important_words:
            pattern_index = index % len(fallback_patterns)
            title = fallback_patterns[pattern_index]
        else:
            title = f"Blog Post #{index + 1}"
        
        return {
            'title': title,
            'confidence': 0.6,
            'method': 'smart_fallback',
        }
    
    def _fallback_titles(self, content: str, num_titles: int) -> List[Dict[str, Any]]:
        """Generate simple fallback titles when everything else fails"""
        basic_titles = [
            'New Blog Post',
            'Latest Article',
            'Fresh Content',
            'Recent Update',
            'New Insights'
        ]
        
        titles = []
        for i in range(num_titles):
            title_index = i % len(basic_titles)
            titles.append({
                'title': basic_titles[title_index] + (f" #{i+1}" if i >= len(basic_titles) else ""),
                'confidence': 0.4,
                'method': 'basic_fallback',
            })
        
        return titles

# Global instance
title_generator = TitleGenerator()