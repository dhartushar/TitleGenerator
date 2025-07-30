import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import title_generator

logger = logging.getLogger(__name__)

class SuggestTitlesView(APIView):
    """
    API endpoint to generate blog title suggestions
    """
    
    def post(self, request):
        """Generate title suggestions for blog content"""
        start_time = time.time()
        
        try:
            # Get content from request
            content = request.data.get('content', '').strip()
            max_suggestions = min(int(request.data.get('max_suggestions', 3)), 5)  # Max 5
            
            # Validate input
            if not content:
                return Response({
                    'success': False,
                    'error': 'Content is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(content) < 20:
                return Response({
                    'success': False,
                    'error': 'Content too short (minimum 20 characters)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(content) > 5000:
                return Response({
                    'success': False,
                    'error': 'Content too long (maximum 5000 characters)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate titles
            logger.info(f"Generating {max_suggestions} titles for content length: {len(content)}")
            suggestions = title_generator.generate_titles(content, max_suggestions)
            
            processing_time = time.time() - start_time
            
            # Return response
            response_data = {
                'success': True,
                'suggestions': suggestions,
                'processing_time': round(processing_time, 2),
            }
            
            logger.info(f"Title generation completed in {processing_time:.2f} seconds")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in title generation: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error during title generation',
                'details': str(e) if getattr(request, 'debug', False) else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class HealthCheckView(APIView):
    """Simple health check endpoint"""
    
    def get(self, request):
        try:
            # Test if the title generator is working
            test_result = title_generator.generate_titles("This is a test content for health check.", 1)
            model_status = "healthy" if test_result else "unhealthy"
        except Exception:
            model_status = "unhealthy"
        
        return Response({
            'status': 'healthy',
            'service': 'Blog Title Generator API',
            'version': '1.0.0',
            'model_status': model_status,
            'endpoints': {
                'suggest_titles': '/api/blog/suggest-titles/',
                'health_check': '/api/blog/health/'
            }
        })

