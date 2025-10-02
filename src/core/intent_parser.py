"""
Advanced natural language intent parsing engine with sophisticated NLP capabilities.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from .models import Intent, IntentType, CodeLanguage


class IntentParser:
    """Advanced natural language intent parsing engine with sophisticated NLP capabilities."""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.language_keywords = self._build_language_keywords()
        self.context_weights = self._build_context_weights()
        self.semantic_patterns = self._build_semantic_patterns()
        self.confidence_threshold = 0.6
        self.parsing_history = []
    
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
    
    def _build_context_weights(self) -> Dict[str, float]:
        """Build context weights for intent disambiguation."""
        return {
            "recent_function": 0.3,
            "recent_class": 0.3,
            "active_files": 0.2,
            "conversation_history": 0.2,
            "explicit_language": 0.4,
            "implicit_language": 0.1
        }
    
    def _build_semantic_patterns(self) -> Dict[str, List[str]]:
        """Build semantic patterns for advanced intent recognition."""
        return {
            "algorithm_requests": [
                "sort", "search", "find", "traverse", "iterate", "recursive",
                "binary", "linear", "bubble", "merge", "quick", "heap"
            ],
            "data_structure_requests": [
                "list", "array", "stack", "queue", "tree", "graph", "hash",
                "linked", "binary tree", "heap", "priority queue"
            ],
            "utility_requests": [
                "helper", "utility", "common", "shared", "base", "abstract"
            ],
            "test_requests": [
                "test", "verify", "check", "validate", "assert", "unit test"
            ],
            "optimization_requests": [
                "optimize", "improve", "enhance", "refactor", "performance",
                "efficient", "faster", "better"
            ]
        }
    
    def _calculate_semantic_confidence(self, text: str, intent_type: IntentType) -> float:
        """Calculate confidence based on semantic analysis."""
        text_lower = text.lower()
        base_confidence = 0.5
        
        # Check for semantic patterns
        for category, patterns in self.semantic_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            if matches > 0:
                base_confidence += min(matches * 0.1, 0.3)
        
        # Boost confidence for specific intent patterns
        if intent_type == IntentType.CREATE_FUNCTION:
            if any(word in text_lower for word in ["function", "def", "method"]):
                base_confidence += 0.2
        elif intent_type == IntentType.CREATE_CLASS:
            if any(word in text_lower for word in ["class", "object", "instance"]):
                base_confidence += 0.2
        elif intent_type == IntentType.MODIFY_CODE:
            if any(word in text_lower for word in ["modify", "change", "update", "edit"]):
                base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _extract_advanced_parameters(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract advanced parameters using NLP techniques."""
        parameters = {}
        text_lower = text.lower()
        
        # Extract function/class names with better patterns
        if intent_type in [IntentType.CREATE_FUNCTION, IntentType.CREATE_CLASS]:
            name_patterns = [
                r"(?:called|named|for)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                r"([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:function|class)",
                r"create\s+(?:a\s+)?(?:new\s+)?([a-zA-Z_][a-zA-Z0-9_]*)"
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if intent_type == IntentType.CREATE_FUNCTION:
                        parameters["function_name"] = match.group(1)
                    else:
                        parameters["class_name"] = match.group(1)
                    break
        
        # Extract test data for execution requests
        if intent_type == IntentType.RUN_CODE:
            # Look for array/list patterns
            array_patterns = [
                r"\[([^\]]+)\]",  # [1, 2, 3]
                r"with\s+([^,\s]+(?:,\s*[^,\s]+)*)",  # with 1, 2, 3
                r"using\s+([^,\s]+(?:,\s*[^,\s]+)*)"   # using 1, 2, 3
            ]
            
            for pattern in array_patterns:
                match = re.search(pattern, text)
                if match:
                    parameters["test_data"] = match.group(1)
                    break
        
        # Extract file names
        if intent_type in [IntentType.CREATE_FILE, IntentType.DELETE_FILE]:
            file_patterns = [
                r"(?:called|named)\s+([a-zA-Z0-9_.-]+)",
                r"file\s+([a-zA-Z0-9_.-]+)",
                r"([a-zA-Z0-9_.-]+)\.(py|js|ts|java|cpp|rs|go)"
            ]
            
            for pattern in file_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters["filename"] = match.group(1)
                    break
        
        # Extract search queries
        if intent_type == IntentType.SEARCH_CODE:
            # Remove common search words and extract the actual query
            query = re.sub(r"^(search\s+for|find|look\s+for|grep)\s*", "", text, flags=re.IGNORECASE)
            parameters["query"] = query.strip()
        
        return parameters
    
    def _analyze_context_relevance(self, text: str, context: Dict[str, Any]) -> float:
        """Analyze how relevant the current context is to the input."""
        if not context:
            return 0.0
        
        relevance_score = 0.0
        text_lower = text.lower()
        
        # Check for references to recent code
        if "last" in text_lower or "previous" in text_lower:
            if context.get("last_generated_code"):
                relevance_score += 0.4
        
        # Check for references to active files
        active_files = context.get("active_files", [])
        for file in active_files:
            if file.lower() in text_lower:
                relevance_score += 0.3
                break
        
        # Check for language consistency
        if context.get("last_generated_code"):
            last_lang = context["last_generated_code"].get("language", "").lower()
            if last_lang in text_lower:
                relevance_score += 0.2
        
        return min(relevance_score, 1.0)
    
    def parse(self, text: str, context: Optional[Dict] = None) -> Intent:
        """
        Parse natural language text into a structured intent with advanced NLP.
        
        Args:
            text: Natural language input
            context: Additional context for parsing
            
        Returns:
            Parsed intent with confidence score
        """
        text = text.strip().lower()
        context = context or {}
        
        # Find the best matching intent with enhanced confidence calculation
        best_intent = None
        best_confidence = 0.0
        best_parameters = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate base confidence
                    base_confidence = self._calculate_confidence(text, pattern, match)
                    
                    # Add semantic confidence
                    semantic_confidence = self._calculate_semantic_confidence(text, intent_type)
                    
                    # Add context relevance
                    context_relevance = self._analyze_context_relevance(text, context)
                    
                    # Combine confidences with weights
                    total_confidence = (
                        base_confidence * 0.4 +
                        semantic_confidence * 0.3 +
                        context_relevance * 0.3
                    )
                    
                    if total_confidence > best_confidence:
                        best_intent = intent_type
                        best_confidence = total_confidence
                        best_parameters = self._extract_advanced_parameters(text, intent_type)
        
        # Default to CREATE_FUNCTION if no pattern matches with sufficient confidence
        if best_intent is None or best_confidence < self.confidence_threshold:
            best_intent = IntentType.CREATE_FUNCTION
            best_confidence = max(0.3, best_confidence)
            best_parameters = {"description": text}
        
        # Detect programming language with enhanced logic
        language = self._detect_language(text, context)
        
        # Create intent with enhanced metadata
        intent = Intent(
            type=best_intent,
            confidence=best_confidence,
            parameters=best_parameters,
            original_text=text,
            language=language,
            context={
                **context,
                "parsing_timestamp": datetime.now().isoformat(),
                "semantic_analysis": self._analyze_semantic_content(text),
                "complexity_score": self._calculate_complexity_score(text)
            }
        )
        
        # Store parsing history for learning
        self.parsing_history.append({
            "text": text,
            "intent": intent.type.value,
            "confidence": intent.confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.parsing_history) > 100:
            self.parsing_history = self.parsing_history[-100:]
        
        return intent
    
    def _analyze_semantic_content(self, text: str) -> Dict[str, Any]:
        """Analyze semantic content of the input text."""
        text_lower = text.lower()
        
        analysis = {
            "has_algorithm_request": any(word in text_lower for word in self.semantic_patterns["algorithm_requests"]),
            "has_data_structure_request": any(word in text_lower for word in self.semantic_patterns["data_structure_requests"]),
            "has_utility_request": any(word in text_lower for word in self.semantic_patterns["utility_requests"]),
            "has_test_request": any(word in text_lower for word in self.semantic_patterns["test_requests"]),
            "has_optimization_request": any(word in text_lower for word in self.semantic_patterns["optimization_requests"]),
            "complexity_indicators": []
        }
        
        # Identify complexity indicators
        complexity_words = ["complex", "advanced", "sophisticated", "optimized", "efficient", "recursive", "dynamic"]
        analysis["complexity_indicators"] = [word for word in complexity_words if word in text_lower]
        
        return analysis
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score for the request."""
        text_lower = text.lower()
        score = 0.0
        
        # Base complexity from word count
        word_count = len(text.split())
        score += min(word_count * 0.05, 0.3)
        
        # Complexity from technical terms
        technical_terms = [
            "algorithm", "data structure", "recursive", "dynamic", "optimization",
            "performance", "complexity", "efficient", "sophisticated"
        ]
        score += sum(0.1 for term in technical_terms if term in text_lower)
        
        # Complexity from multiple requirements
        if "and" in text_lower or "also" in text_lower:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get statistics about parsing performance."""
        if not self.parsing_history:
            return {"total_parses": 0}
        
        total_parses = len(self.parsing_history)
        avg_confidence = sum(p["confidence"] for p in self.parsing_history) / total_parses
        
        # Count intent types
        intent_counts = {}
        for parse in self.parsing_history:
            intent_type = parse["intent"]
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        return {
            "total_parses": total_parses,
            "average_confidence": avg_confidence,
            "intent_distribution": intent_counts,
            "recent_parses": self.parsing_history[-10:] if len(self.parsing_history) > 10 else self.parsing_history
        }
