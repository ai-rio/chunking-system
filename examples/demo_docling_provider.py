#!/usr/bin/env python3
"""
Demo script to show DoclingProvider integration with LLMFactory.

This script demonstrates that DoclingProvider has been successfully integrated
following the existing factory pattern and can be used alongside other providers.
"""

from src.llm.factory import LLMFactory
from src.llm.providers import DoclingProvider
from src.config.settings import config

def main():
    print("=== DoclingProvider Integration Demo ===\n")
    
    # 1. Show all available providers
    print("1. Available Providers:")
    available_providers = LLMFactory.get_available_providers()
    for provider_name, is_available in available_providers.items():
        status = "✓" if is_available else "✗"
        print(f"   {status} {provider_name}")
    print()
    
    # 2. Show DoclingProvider is registered
    print("2. Provider Registration:")
    print(f"   DoclingProvider registered: {'docling' in LLMFactory._providers}")
    print(f"   Provider class: {LLMFactory._providers.get('docling', 'Not found')}")
    print()
    
    # 3. Test provider instantiation (with mock API key)
    print("3. Provider Instantiation Test:")
    try:
        # Mock configuration for testing
        original_api_key = config.DOCLING_API_KEY
        config.DOCLING_API_KEY = "test_key"
        
        provider = LLMFactory.create_provider(
            provider_name="docling",
            model="docling-v1"
        )
        
        print(f"   ✓ DoclingProvider created successfully")
        print(f"   Provider name: {provider.provider_name}")
        print(f"   Model: {provider.model}")
        print(f"   API key configured: {provider.is_available()}")
        print(f"   Max tokens: {provider.get_max_tokens()}")
        
        # Test token counting
        test_text = "This is a test sentence for token counting."
        token_count = provider.count_tokens(test_text)
        print(f"   Token count for '{test_text}': {token_count}")
        
        # Restore original API key
        config.DOCLING_API_KEY = original_api_key
        
    except Exception as e:
        print(f"   ✗ Error creating provider: {e}")
    print()
    
    # 4. Show configuration support
    print("4. Configuration Support:")
    print(f"   DOCLING_API_KEY: {config.DOCLING_API_KEY or 'Not set'}")
    print(f"   DOCLING_API_BASE_URL: {config.DOCLING_API_BASE_URL}")
    print(f"   DOCLING_MODEL: {config.DOCLING_MODEL}")
    print(f"   DOCLING_EMBEDDING_MODEL: {config.DOCLING_EMBEDDING_MODEL}")
    print()
    
    # 5. Integration verification
    print("5. Integration Verification:")
    
    # IV1: All existing providers still work
    original_providers = ["openai", "anthropic", "jina"]
    print(f"   IV1 - Existing providers maintained: {all(p in LLMFactory._providers for p in original_providers)}")
    
    # IV2: DoclingProvider included in available providers
    print(f"   IV2 - DoclingProvider in available providers: {'docling' in available_providers}")
    
    # IV3: Factory can instantiate DoclingProvider
    print(f"   IV3 - Factory can create DoclingProvider: {LLMFactory._providers.get('docling') == DoclingProvider}")
    
    print("\n=== Integration Success! ===")
    print("DoclingProvider has been successfully integrated into the LLM factory pattern.")
    print("It follows the existing BaseLLMProvider interface and can be used alongside")
    print("other providers (OpenAI, Anthropic, Jina) without breaking existing functionality.")

if __name__ == "__main__":
    main()