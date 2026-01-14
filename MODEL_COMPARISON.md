# OpenAI Model Comparison Guide

## Available OpenAI Models

### GPT-4o (Recommended - SHORTLISTED)
- **Model ID**: `gpt-4o`
- **Context Window**: 128,000 tokens
- **Capabilities**: Text, vision, audio (multimodal)
- **Performance**: Best overall performance, 88.7% on MMLU benchmark
- **Speed**: Fast
- **Cost**: $2.50/$10 per 1M tokens (input/output)
- **Best for**: General use, complex reasoning, multimodal tasks

### GPT-4 Turbo (DISCARDED (no benefits vs. 4o))
- **Model ID**: `gpt-4-turbo`
- **Context Window**: 128,000 tokens
- **Capabilities**: Text only
- **Performance**: Strong performance, faster than GPT-4
- **Speed**: Very fast
- **Cost**: $10/$30 per 1M tokens (input/output)
- **Best for**: Large context windows, fast responses, text-only tasks

### GPT-4 Turbo Preview (Current - DISCARDED)
- **Model ID**: `gpt-4-turbo-preview`
- **Context Window**: 128,000 tokens
- **Capabilities**: Text only
- **Performance**: Similar to GPT-4 Turbo
- **Speed**: Fast
- **Cost**: $10/$30 per 1M tokens (input/output)
- **Note**: This is a preview version. Consider switching to `gpt-4-turbo` or `gpt-4o`

### GPT-4o Mini (DISCARDED (cost is not the issue))
- **Model ID**: `gpt-4o-mini`
- **Context Window**: 128,000 tokens
- **Capabilities**: Text, vision, audio (multimodal)
- **Performance**: Good performance, smaller model
- **Speed**: Very fast
- **Cost**: $0.15/$0.60 per 1M tokens (input/output) - **Much cheaper!**
- **Best for**: Simple tasks, cost-sensitive applications, high-volume use

### GPT-4 (Original)
- **Model ID**: `gpt-4`
- **Context Window**: 8,000 tokens
- **Capabilities**: Text only
- **Performance**: Good but older
- **Speed**: Slower
- **Cost**: $30/$60 per 1M tokens (input/output) - **Most expensive**
- **Best for**: Legacy compatibility (not recommended for new projects)

## Running the Comparison

### Quick Start

```bash
python compare_models.py
```

This will:
1. Test all models with the same set of prompts
2. Measure response time, token usage, and errors
3. Calculate approximate costs
4. Generate a comparison report
5. Save results to `model_comparison_results.json`

### What Gets Tested

The comparison script tests models with:
1. **Simple Task**: Basic question answering
2. **Tool Usage Decision**: Reasoning about when to use tools
3. **Complex Reasoning**: Multi-step task planning
4. **Memory Context**: Using past context effectively
5. **Structured Output**: Following specific response formats

### Understanding the Results

The comparison shows:
- **Success Rate**: How many tests passed vs failed
- **Average Response Time**: Speed comparison
- **Average Tokens**: Token usage (affects cost)
- **Total Cost**: Approximate cost for all test prompts

## Recommendations

### For Your Assistant

Based on your use case (email management, document editing, tool usage):

1. **GPT-4o** - Best overall choice
   - Excellent reasoning for tool selection
   - Good at following structured formats
   - Multimodal if you add image/audio features later
   - Good balance of cost and performance

2. **GPT-4 Turbo** - Good alternative
   - Very fast responses
   - Large context window for long conversations
   - Slightly more expensive than GPT-4o

3. **GPT-4o Mini** - Cost-effective option
   - Much cheaper for high-volume use
   - Still good performance
   - Consider for simple tasks or testing

4. **GPT-4 Turbo Preview** - Consider upgrading
   - You're currently using this
   - Consider switching to `gpt-4-turbo` (stable) or `gpt-4o` (better)

## Changing Your Model

To change the model your assistant uses:

1. **Update environment variable**:
   ```bash
   # In your .env file
   LLM_MODEL=gpt-4o
   ```

2. **Or set it directly**:
   ```bash
   export LLM_MODEL=gpt-4o  # Linux/Mac
   $env:LLM_MODEL="gpt-4o"  # PowerShell
   ```

3. **Restart your application** for changes to take effect

## Cost Considerations

Approximate costs per 1,000 requests (assuming 500 prompt tokens + 500 completion tokens):

- **GPT-4o**: ~$0.006 per request
- **GPT-4 Turbo**: ~$0.020 per request
- **GPT-4 Turbo Preview**: ~$0.020 per request
- **GPT-4o Mini**: ~$0.0004 per request (15x cheaper!)
- **GPT-4**: ~$0.045 per request

For high-volume usage, GPT-4o Mini can save significant costs while still providing good quality.

## Testing Your Own Prompts

You can modify `compare_models.py` to test with your own prompts. Edit the `TEST_PROMPTS` list to include scenarios specific to your use case.
