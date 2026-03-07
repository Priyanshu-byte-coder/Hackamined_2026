"""Quick test to check if LangSmith API is accessible and returning data."""

from app.langsmith_client import fetch_traces, compute_analytics, get_project_id

print("=" * 60)
print("Testing LangSmith API Connection")
print("=" * 60)

# Test 1: Get project ID
print("\n1. Getting project ID...")
try:
    project_id = get_project_id()
    if project_id:
        print(f"   ✓ Project ID found: {project_id}")
    else:
        print("   ✗ Project not found. Check LANGCHAIN_PROJECT name in .env")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Fetch traces
print("\n2. Fetching traces (last 24 hours)...")
try:
    traces = fetch_traces(limit=10, hours_back=24)
    print(f"   ✓ Found {len(traces)} traces")
    if traces:
        print("\n   Recent traces:")
        for i, t in enumerate(traces[:5], 1):
            print(f"     {i}. {t.get('name', 'unknown')} - {t.get('status', 'unknown')}")
    else:
        print("   ⚠ No traces found. Possible reasons:")
        print("     - Traces are still uploading to LangSmith (wait 10-30 seconds)")
        print("     - LANGCHAIN_TRACING_V2 is not 'true' in .env")
        print("     - LANGCHAIN_API_KEY is incorrect")
        print("     - No API calls have been made yet")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Compute analytics
print("\n3. Computing analytics...")
try:
    analytics = compute_analytics(hours_back=24)
    print(f"   ✓ Total traces: {analytics.get('total_traces', 0)}")
    print(f"   ✓ Success rate: {analytics.get('success_rate', 0)}%")
    if analytics.get('latency', {}).get('avg_s'):
        print(f"   ✓ Avg latency: {analytics['latency']['avg_s']}s")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
