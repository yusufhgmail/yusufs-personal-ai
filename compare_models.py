"""Compare different OpenAI models to find the best one for this assistant.

This script tests multiple models with the same prompts and compares:
- Response quality
- Response time
- Token usage (cost)
- Error rates
"""

import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI
from config.settings import get_settings


@dataclass
class ModelResult:
    """Result from testing a single model."""
    model: str
    prompt: str
    response: str
    response_time: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    error: Optional[str] = None
    finish_reason: Optional[str] = None


@dataclass
class ModelStats:
    """Aggregated statistics for a model."""
    model: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_response_time: float
    avg_prompt_tokens: float
    avg_completion_tokens: float
    avg_total_tokens: float
    total_cost: float  # Approximate cost in USD
    results: List[ModelResult]


# Test prompts that represent real use cases for the assistant
TEST_PROMPTS = [
    {
        "name": "Simple Task",
        "system": "You are a helpful assistant.",
        "user": "What is 2+2?"
    },
    {
        "name": "Tool Usage Decision",
        "system": "You are an AI assistant that can use tools. When you need to use a tool, respond with ACTION: tool_name and ACTION_INPUT: {...}. Otherwise, respond with FINAL_ANSWER: your answer.",
        "user": "I need to find an email from miguel@gmail.com. Should I use a tool or can you answer directly?"
    },
    {
        "name": "Complex Reasoning",
        "system": "You are a helpful assistant that helps with email management and document editing.",
        "user": "I received an email from a client asking about a project deadline. I need to check my Google Drive for the project timeline document, then draft a response. What steps should I take?"
    },
    {
        "name": "Memory Context",
        "system": "You are an AI assistant. You have access to these past interactions:\n- User mentioned they prefer formal tone in emails\n- User works on a project called FoundryVerse\n\nUse this context when responding.",
        "user": "Draft an email to a potential partner about FoundryVerse. Keep it professional."
    },
    {
        "name": "Structured Output",
        "system": "You are an AI assistant. When responding, use this format:\nTHOUGHT: your reasoning\nFOCUS: the main task\nFINAL_ANSWER: your answer",
        "user": "I need to remember that I prefer to be called Yusuf, not Youssef. Can you help me remember this?"
    }
]


# Approximate pricing per 1M tokens (as of Jan 2024, update as needed)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},  # $2.50/$10 per 1M tokens
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},  # $10/$30 per 1M tokens
    "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},  # Same as turbo
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # $0.15/$0.60 per 1M tokens
    "gpt-4": {"input": 30.00, "output": 60.00},  # $30/$60 per 1M tokens
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate approximate cost for a request."""
    if model not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model]
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def test_model(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> ModelResult:
    """Test a single model with a prompt."""
    start_time = time.time()
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        response_time = time.time() - start_time
        
        return ModelResult(
            model=model,
            prompt=user_prompt,
            response=response.choices[0].message.content,
            response_time=response_time,
            prompt_tokens=response.usage.prompt_tokens if response.usage else None,
            completion_tokens=response.usage.completion_tokens if response.usage else None,
            total_tokens=response.usage.total_tokens if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )
    except Exception as e:
        response_time = time.time() - start_time
        return ModelResult(
            model=model,
            prompt=user_prompt,
            response="",
            response_time=response_time,
            error=str(e)
        )


def test_all_models(models: List[str], test_prompts: List[Dict]) -> Dict[str, ModelStats]:
    """Test all models with all prompts."""
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    
    results_by_model: Dict[str, List[ModelResult]] = {model: [] for model in models}
    
    print(f"\n{'='*80}")
    print(f"Testing {len(models)} models with {len(test_prompts)} test prompts")
    print(f"{'='*80}\n")
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\nTest {i}/{len(test_prompts)}: {test['name']}")
        print(f"Prompt: {test['user'][:60]}...")
        print("-" * 80)
        
        for model in models:
            print(f"  Testing {model}...", end=" ", flush=True)
            result = test_model(client, model, test['system'], test['user'])
            results_by_model[model].append(result)
            
            if result.error:
                print(f"❌ ERROR: {result.error}")
            else:
                print(f"✓ ({result.response_time:.2f}s, {result.total_tokens} tokens)")
    
    # Calculate statistics for each model
    stats_by_model = {}
    for model, results in results_by_model.items():
        successful = [r for r in results if not r.error]
        failed = [r for r in results if r.error]
        
        if successful:
            avg_response_time = sum(r.response_time for r in successful) / len(successful)
            avg_prompt_tokens = sum(r.prompt_tokens or 0 for r in successful) / len(successful)
            avg_completion_tokens = sum(r.completion_tokens or 0 for r in successful) / len(successful)
            avg_total_tokens = sum(r.total_tokens or 0 for r in successful) / len(successful)
            
            total_cost = sum(
                calculate_cost(model, r.prompt_tokens or 0, r.completion_tokens or 0)
                for r in successful
            )
        else:
            avg_response_time = 0
            avg_prompt_tokens = 0
            avg_completion_tokens = 0
            avg_total_tokens = 0
            total_cost = 0
        
        stats_by_model[model] = ModelStats(
            model=model,
            total_tests=len(results),
            successful_tests=len(successful),
            failed_tests=len(failed),
            avg_response_time=avg_response_time,
            avg_prompt_tokens=avg_prompt_tokens,
            avg_completion_tokens=avg_completion_tokens,
            avg_total_tokens=avg_total_tokens,
            total_cost=total_cost,
            results=results
        )
    
    return stats_by_model


def print_comparison(stats_by_model: Dict[str, ModelStats]):
    """Print a formatted comparison of all models."""
    print(f"\n{'='*80}")
    print("MODEL COMPARISON RESULTS")
    print(f"{'='*80}\n")
    
    # Sort by average response time
    sorted_models = sorted(
        stats_by_model.items(),
        key=lambda x: x[1].avg_response_time if x[1].successful_tests > 0 else float('inf')
    )
    
    print(f"{'Model':<25} {'Success':<10} {'Avg Time':<12} {'Avg Tokens':<15} {'Cost':<10}")
    print("-" * 80)
    
    for model, stats in sorted_models:
        success_rate = f"{stats.successful_tests}/{stats.total_tests}"
        avg_time = f"{stats.avg_response_time:.2f}s" if stats.successful_tests > 0 else "N/A"
        avg_tokens = f"{stats.avg_total_tokens:.0f}" if stats.successful_tests > 0 else "N/A"
        cost = f"${stats.total_cost:.4f}" if stats.successful_tests > 0 else "N/A"
        
        print(f"{model:<25} {success_rate:<10} {avg_time:<12} {avg_tokens:<15} {cost:<10}")
    
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}\n")
    
    for model, stats in sorted_models:
        print(f"\n{model}")
        print("-" * 80)
        print(f"Success Rate: {stats.successful_tests}/{stats.total_tests} ({stats.successful_tests/stats.total_tests*100:.1f}%)")
        if stats.successful_tests > 0:
            print(f"Average Response Time: {stats.avg_response_time:.2f}s")
            print(f"Average Tokens: {stats.avg_total_tokens:.0f} (prompt: {stats.avg_prompt_tokens:.0f}, completion: {stats.avg_completion_tokens:.0f})")
            print(f"Total Cost (for all tests): ${stats.total_cost:.4f}")
        
        if stats.failed_tests > 0:
            print(f"\nErrors:")
            for result in stats.results:
                if result.error:
                    print(f"  - {result.error}")
        
        print()


def save_results(stats_by_model: Dict[str, ModelStats], filename: str = "model_comparison_results.json"):
    """Save results to a JSON file."""
    output = {}
    for model, stats in stats_by_model.items():
        output[model] = {
            "model": stats.model,
            "total_tests": stats.total_tests,
            "successful_tests": stats.successful_tests,
            "failed_tests": stats.failed_tests,
            "avg_response_time": stats.avg_response_time,
            "avg_prompt_tokens": stats.avg_prompt_tokens,
            "avg_completion_tokens": stats.avg_completion_tokens,
            "avg_total_tokens": stats.avg_total_tokens,
            "total_cost": stats.total_cost,
            "results": [asdict(r) for r in stats.results]
        }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {filename}")


def main():
    """Main function to run model comparison."""
    # Models to test
    models_to_test = [
        "gpt-4o",              # Latest, best performance
        "gpt-4-turbo",         # Faster, cheaper alternative
        "gpt-4-turbo-preview", # What you currently have
        "gpt-4o-mini",         # Smaller, much cheaper
        # "gpt-4",             # Older, more expensive (uncomment if you want to test)
    ]
    
    print("OpenAI Model Comparison Tool")
    print("=" * 80)
    print("\nThis will test the following models:")
    for model in models_to_test:
        print(f"  - {model}")
    
    print("\nModels available to test:")
    print("  - gpt-4o: Latest model, best performance, multimodal")
    print("  - gpt-4-turbo: Faster and cheaper than GPT-4, 128K context")
    print("  - gpt-4-turbo-preview: Preview version (what you currently use)")
    print("  - gpt-4o-mini: Smaller, much cheaper version of GPT-4o")
    print("  - gpt-4: Original GPT-4, more expensive")
    
    input("\nPress Enter to start testing (this will make API calls and cost money)...")
    
    stats = test_all_models(models_to_test, TEST_PROMPTS)
    print_comparison(stats)
    save_results(stats)
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("\nBased on the results:")
    print("1. Check which model has the best success rate")
    print("2. Consider response time for your use case")
    print("3. Balance cost vs quality")
    print("4. For this assistant, GPT-4o or GPT-4 Turbo are likely best")
    print("5. GPT-4o-mini might be good for simple tasks to save costs")
    print("\nTo change your model, update the LLM_MODEL environment variable.")


if __name__ == "__main__":
    main()
