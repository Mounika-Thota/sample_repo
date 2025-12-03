#!/usr/bin/env python3
"""
Simple test script to validate the chunking comparison functionality
"""

import sys
import os
sys.path.append('/home/mothota/Desktop/Projects/azure-dev/agentic-sdlc-platform')

from src.agents.user_story_generator.document_embedding_generator.document_processor import DocumentProcessor
from src.agents.user_story_generator.document_embedding_generator.knowledge_base_manager import KnowledgeBaseManager
import uuid
import tempfile
import json

def get_test_document():
    """Get the B&FRD_Jan 21.pdf file from downloads folder"""
    downloads_path = os.path.expanduser("~/Downloads")
    test_file = os.path.join(downloads_path, "B&FRD_Jan 21.pdf")
    
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    return test_file

def test_knowledge_base_manager():
    """Test the KnowledgeBaseManager chunking comparison"""
    print("Testing KnowledgeBaseManager chunking comparison...")
    
    # Get test document
    test_file = get_test_document()
    test_doc_id = str(uuid.uuid4())
    
    try:
        # Initialize knowledge base manager
        kb_manager = KnowledgeBaseManager()
        
        # Test compare_chunking_strategies
        print(f"Testing chunking strategies on: {test_file}")
        results = kb_manager.compare_chunking_strategies(test_file, test_doc_id)
        
        print("\nComparison Results:")
        print(json.dumps(results, indent=2))
        
        return results
        
    except Exception as e:
        print(f"Error in KnowledgeBaseManager test: {e}")
        return None

def test_document_processor():
    """Test the DocumentProcessor chunking comparison"""
    print("\n" + "="*60)
    print("Testing DocumentProcessor chunking comparison...")
    
    # Get test document
    test_file = get_test_document()
    test_doc_id = str(uuid.uuid4())
    
    try:
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Create a mock file object
        class MockFile:
            def __init__(self, filepath):
                self.temp_path = filepath
                self.filename = os.path.basename(filepath)
        
        mock_file = MockFile(test_file)
        
        # Test test_chunking_strategies
        print(f"Testing chunking strategies on: {test_file}")
        results = processor.test_chunking_strategies(mock_file, test_doc_id)
        
        print("\nDocumentProcessor Results:")
        print(json.dumps(results, indent=2))
        
        return results
        
    except Exception as e:
        print(f"Error in DocumentProcessor test: {e}")
        return None

if __name__ == "__main__":
    print("Starting Chunking Comparison Tests")
    print("="*60)
    
    # Test 1: KnowledgeBaseManager
    kb_results = test_knowledge_base_manager()
    
    # Test 2: DocumentProcessor
    doc_results = test_document_processor()
    
    print("\n" + "="*60)
    print("Test Summary:")
    print(f"KnowledgeBaseManager test: {'✓ PASSED' if kb_results else '✗ FAILED'}")
    print(f"DocumentProcessor test: {'✓ PASSED' if doc_results else '✗ FAILED'}")
    
    if doc_results and doc_results.get("status") == "success":
        summary = doc_results.get("summary", {})
        if summary:
            print(f"\nBest Strategy Analysis:")
            best_analysis = summary.get("best_for_page_preservation", {})
            print(f"Recommended Strategy: {best_analysis.get('recommended_strategy', 'N/A')}")
            print(f"Reason: {best_analysis.get('reason', 'N/A')}")
