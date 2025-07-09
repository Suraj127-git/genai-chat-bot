import numpy as np
from typing import List, Dict, Any, Optional
from src.langgraphagenticai.common.logger import logger
import re
from datetime import datetime, timedelta

class VectorSearchUtils:
    """
    Utility functions for vector search operations
    """
    
    @staticmethod
    def preprocess_query(query: str) -> str:
        """
        Preprocess user query for better vector search
        """
        # Remove special characters but keep spaces
        query = re.sub(r'[^\w\s]', '', query)
        
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple text similarity as a fallback
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    @staticmethod
    def filter_by_recency(results: List[Dict[str, Any]], 
                         max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Filter search results by recency
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        filtered_results = []
        
        for result in results:
            try:
                timestamp_str = result.get('metadata', {}).get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp > cutoff_time:
                        filtered_results.append(result)
                else:
                    # If no timestamp, include the result
                    filtered_results.append(result)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing timestamp: {e}")
                # Include result if timestamp parsing fails
                filtered_results.append(result)
        
        return filtered_results
    
    @staticmethod
    def rank_results_by_relevance(results: List[Dict[str, Any]], 
                                query: str) -> List[Dict[str, Any]]:
        """
        Re-rank results by combining vector similarity and text similarity
        """
        for result in results:
            vector_score = result.get('score', 0.0)
            text_score = VectorSearchUtils.calculate_text_similarity(
                query, result.get('question', '')
            )
            
            # Combine scores (weighted average)
            combined_score = (0.7 * vector_score) + (0.3 * text_score)
            result['combined_score'] = combined_score
        
        # Sort by combined score
        return sorted(results, key=lambda x: x.get('combined_score', 0), reverse=True)
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract keywords from text for better search
        """
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords, limited by max_keywords
        unique_keywords = list(dict.fromkeys(keywords))[:max_keywords]
        
        return unique_keywords
