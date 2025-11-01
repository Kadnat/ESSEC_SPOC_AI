"""
Test script for France Travail API
Quick test to verify API credentials and search functionality

Run: python test_france_travail.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables from .env in same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print(f"🔍 Loading .env from: {env_path}")
print(f"🔑 CLIENT_ID found: {'Yes' if os.getenv('FRANCE_TRAVAIL_CLIENT_ID') else 'No'}")
print(f"🔑 CLIENT_SECRET found: {'Yes' if os.getenv('FRANCE_TRAVAIL_CLIENT_SECRET') else 'No'}\n")

from services.job_fetcher import job_fetcher

def test_api_connection():
    """Test 1: Verify API credentials and token"""
    print("=" * 60)
    print("TEST 1: API Connection & Authentication")
    print("=" * 60)
    
    if not job_fetcher.api_available:
        print("❌ API credentials not configured in .env")
        return False
    
    token = job_fetcher._get_access_token()
    if token:
        print(f"✅ Token obtained: {token[:20]}...")
        return True
    else:
        print("❌ Failed to get token")
        return False

def test_simple_search():
    """Test 2: Simple search without filters"""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Search (no filters)")
    print("=" * 60)
    
    jobs = job_fetcher.search_jobs(max_results=5)
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs")
        if len(jobs) > 0:
            print("\nFirst job:")
            job = jobs[0]
            print(f"  - Title: {job['title']}")
            print(f"  - Company: {job['company']}")
            print(f"  - Location: {job['location']}")
            print(f"  - ROME: {job['rome_code']}")
        return True
    else:
        print("⚠️  No jobs found (HTTP 204 or error)")
        return False

def test_rome_search():
    """Test 3: Search with specific ROME codes"""
    print("\n" + "=" * 60)
    print("TEST 3: Search with ROME codes (M1805, M1806)")
    print("=" * 60)
    
    # M1805 = Études et développement informatique
    # M1806 = Conseil et maîtrise d'ouvrage en systèmes d'information
    jobs = job_fetcher.search_jobs(
        rome_codes=['M1805', 'M1806'],
        max_results=5
    )
    
    if jobs:
        print(f"✅ Found {len(jobs)} IT jobs")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   ROME: {job['rome_code']}")
        return True
    else:
        print("⚠️  No jobs found with these ROME codes")
        return False

def test_keyword_search():
    """Test 4: Search with keywords"""
    print("\n" + "=" * 60)
    print("TEST 4: Search with keywords (Python, Developer)")
    print("=" * 60)
    
    jobs = job_fetcher.search_jobs(
        keywords=['Python', 'Developer'],
        max_results=5
    )
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs matching keywords")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
        return True
    else:
        print("⚠️  No jobs found with these keywords")
        return False

def test_combined_search():
    """Test 5: Search with ROME + keywords + experience"""
    print("\n" + "=" * 60)
    print("TEST 5: Combined Search (ROME + keywords + experience)")
    print("=" * 60)
    
    jobs = job_fetcher.search_jobs(
        rome_codes=['M1805'],
        keywords=['Python'],
        experience='2',  # 2-5 ans
        max_results=5
    )
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs matching all criteria")
        for i, job in enumerate(jobs[:2], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Experience: {job['experience_required']}")
        return True
    else:
        print("⚠️  No jobs found with combined filters (normal if too restrictive)")
        return False

def main():
    print("\n🧪 FRANCE TRAVAIL API - TEST SUITE")
    print("Testing API connectivity and search functions\n")
    
    results = []
    
    # Test 1: Connection
    results.append(("Authentication", test_api_connection()))
    
    # Only continue if authentication succeeded
    if not results[0][1]:
        print("\n❌ Cannot continue without valid API credentials")
        print("\nTo fix:")
        print("1. Register at: https://francetravail.io/inscription")
        print("2. Create an application and get credentials")
        print("3. Add to backend/.env:")
        print("   FRANCE_TRAVAIL_CLIENT_ID=PAR_xxxxx")
        print("   FRANCE_TRAVAIL_CLIENT_SECRET=xxxxx")
        return
    
    # Test 2-5: Searches
    results.append(("Simple Search", test_simple_search()))
    results.append(("ROME Search", test_rome_search()))
    results.append(("Keyword Search", test_keyword_search()))
    results.append(("Combined Search", test_combined_search()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! France Travail API is working correctly.")
    elif passed >= total - 1:
        print("\n✅ API is working! Some searches returned no results (normal if filters too restrictive).")
    else:
        print("\n⚠️  Some tests failed. Check API credentials and error messages above.")

if __name__ == "__main__":
    main()
