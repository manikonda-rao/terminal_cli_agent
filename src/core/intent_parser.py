"""
Intent parsing system for natural language to structured intents.
"""

import re
from typing import Dict, List, Optional, Tuple
from .models import Intent, IntentType, CodeLanguage


class IntentParser:
    """Parses natural language input into structured intents."""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.language_keywords = self._build_language_keywords()
    
    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Build regex patterns for different intent types."""
        return {
            IntentType.CREATE_FUNCTION: [
                r"create\s+(?:a\s+)?(?:python\s+)?function\s+(?:for\s+|that\s+)?(.+)",
                r"write\s+(?:a\s+)?(?:python\s+)?function\s+(?:for\s+|that\s+)?(.+)",
                r"implement\s+(?:a\s+)?(?:python\s+)?function\s+(?:for\s+|that\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:python\s+)?function\s+(?:for\s+|that\s+)?(.+)",
                r"build\s+(?:a\s+)?(?:python\s+)?function\s+(?:for\s+|that\s+)?(.+)",
            ],
            IntentType.CREATE_CLASS: [
                r"create\s+(?:a\s+)?(?:python\s+)?class\s+(?:for\s+|that\s+)?(.+)",
                r"write\s+(?:a\s+)?(?:python\s+)?class\s+(?:for\s+|that\s+)?(.+)",
                r"implement\s+(?:a\s+)?(?:python\s+)?class\s+(?:for\s+|that\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:python\s+)?class\s+(?:for\s+|that\s+)?(.+)",
            ],
            IntentType.MODIFY_CODE: [
                r"modify\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s+(?:to\s+)?(.+)",
                r"change\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s+(?:to\s+)?(.+)",
                r"update\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s+(?:to\s+)?(.+)",
                r"edit\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s+(?:to\s+)?(.+)",
                r"fix\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s+(?:to\s+)?(.+)",
            ],
            IntentType.RUN_CODE: [
                r"run\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:with\s+)?(.+)?",
                r"execute\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:with\s+)?(.+)?",
                r"test\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:with\s+)?(.+)?",
                r"call\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:with\s+)?(.+)?",
            ],
            IntentType.CREATE_FILE: [
                r"create\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+|named\s+)?(.+)",
                r"make\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+|named\s+)?(.+)",
                r"new\s+file\s+(?:called\s+|named\s+)?(.+)",
            ],
            IntentType.DELETE_FILE: [
                r"delete\s+(?:the\s+)?file\s+(.+)",
                r"remove\s+(?:the\s+)?file\s+(.+)",
                r"rm\s+(.+)",
            ],
            IntentType.SEARCH_CODE: [
                r"search\s+(?:for\s+)?(.+)",
                r"find\s+(?:all\s+)?(.+)",
                r"grep\s+(?:for\s+)?(.+)",
                r"look\s+for\s+(.+)",
            ],
            IntentType.EXPLAIN_CODE: [
                r"explain\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"what\s+does\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"how\s+does\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
            ],
            IntentType.REFACTOR_CODE: [
                r"refactor\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:to\s+)?(.+)",
                r"optimize\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:to\s+)?(.+)",
                r"improve\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(?:to\s+)?(.+)",
            ],
            IntentType.DEBUG_CODE: [
                r"debug\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"fix\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"troubleshoot\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
            ],
            IntentType.TEST_CODE: [
                r"test\s+(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"write\s+tests?\s+(?:for\s+)?(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
                r"create\s+tests?\s+(?:for\s+)?(?:the\s+)?(?:last\s+)?(?:function|code|class)\s*(.+)",
            ],
        }
    
    def _build_language_keywords(self) -> Dict[CodeLanguage, List[str]]:
        """Build keywords for language detection."""
        return {
            CodeLanguage.PYTHON: ["python", "py", "def", "class", "import"],
            CodeLanguage.JAVASCRIPT: ["javascript", "js", "function", "const", "let"],
            CodeLanguage.TYPESCRIPT: ["typescript", "ts", "interface", "type"],
            CodeLanguage.JAVA: ["java", "public", "private", "static"],
            CodeLanguage.CPP: ["cpp", "c++", "#include", "std::"],
            CodeLanguage.RUST: ["rust", "fn", "struct", "impl"],
            CodeLanguage.GO: ["go", "golang", "func", "package"],
        }
    
    def parse(self, text: str, context: Optional[Dict] = None) -> Intent:
        """
        Parse natural language text into a structured intent.
        
        Args:
            text: Natural language input
            context: Additional context for parsing
            
        Returns:
            Parsed intent with confidence score
        """
        text = text.strip().lower()
        context = context or {}
        
        # Find the best matching intent
        best_intent = None
        best_confidence = 0.0
        best_parameters = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = self._calculate_confidence(text, pattern, match)
                    if confidence > best_confidence:
                        best_intent = intent_type
                        best_confidence = confidence
                        best_parameters = self._extract_parameters(match, intent_type)
        
        # Default to CREATE_FUNCTION if no pattern matches
        if best_intent is None:
            best_intent = IntentType.CREATE_FUNCTION
            best_confidence = 0.3
            best_parameters = {"description": text}
        
        # Detect programming language
        language = self._detect_language(text, context)
        
        return Intent(
            type=best_intent,
            confidence=best_confidence,
            parameters=best_parameters,
            original_text=text,
            language=language,
            context=context
        )
    
    def _calculate_confidence(self, text: str, pattern: str, match) -> float:
        """Calculate confidence score for a pattern match."""
        base_confidence = 0.7
        
        # Boost confidence for exact matches
        if match.group(0).lower() == text.lower():
            base_confidence += 0.2
        
        # Boost confidence for longer matches
        match_length = len(match.group(0))
        text_length = len(text)
        if match_length / text_length > 0.8:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _extract_parameters(self, match, intent_type: IntentType) -> Dict[str, str]:
        """Extract parameters from regex match."""
        parameters = {}
        
        if match.groups():
            # Extract the main parameter (usually the description)
            main_param = match.group(1).strip()
            parameters["description"] = main_param
            
            # Extract additional parameters based on intent type
            if intent_type == IntentType.CREATE_FUNCTION:
                parameters["function_name"] = self._extract_function_name(main_param)
            elif intent_type == IntentType.CREATE_CLASS:
                parameters["class_name"] = self._extract_class_name(main_param)
            elif intent_type == IntentType.RUN_CODE:
                parameters["test_data"] = main_param
        
        return parameters
    
    def _extract_function_name(self, description: str) -> str:
        """Extract function name from description."""
        # Look for common function name patterns
        patterns = [
            r"for\s+(\w+)",
            r"called\s+(\w+)",
            r"named\s+(\w+)",
            r"(\w+)\s+function",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default to a generated name
        return "generated_function"
    
    def _extract_class_name(self, description: str) -> str:
        """Extract class name from description."""
        # Look for common class name patterns
        patterns = [
            r"for\s+(\w+)",
            r"called\s+(\w+)",
            r"named\s+(\w+)",
            r"(\w+)\s+class",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default to a generated name
        return "GeneratedClass"
    
    def _detect_language(self, text: str, context: Dict) -> Optional[CodeLanguage]:
        """Detect programming language from text and context."""
        # Check context first
        if "language" in context:
            try:
                return CodeLanguage(context["language"])
            except ValueError:
                pass
        
        # Check for explicit language mentions
        text_lower = text.lower()
        for language, keywords in self.language_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return language
        
        # Default to Python
        return CodeLanguage.PYTHON
