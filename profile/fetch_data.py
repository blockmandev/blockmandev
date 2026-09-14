#!/usr/bin/env python3
"""
Pulls the real numbers the charts draw, into data.json.

    export GITHUB_TOKEN=ghp_...        # classic PAT, read:user + public_repo
    python3 fetch_data.py

Without a token it still gets repo/star/language data (60 req/hr, unauthenticated);
the contribution calendar and commit totals need the token, because GitHub only
exposes those through GraphQL.

Wakapi is read from its public wakatime-compatible endpoint. If your profile is
private, set WAKAPI_KEY too.
"""
import json, os, sys, urllib.request, urllib.error
from collections import Counter, defaultdict
from datetime import date

USER = os.environ.get("GH_USER", "blockmandev")
WAKAPI_USER = os.environ.get("WAKAPI_USER", "tanu1337")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WAKAPI_KEY = os.environ.get("WAKAPI_KEY", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def get(url, headers=None, body=None):
    h = {"User-Agent": "profile-charts", "Accept": "application/vnd.github+json"}
    h.update(headers or {})
    data = json.dumps(body).encode() if body else None
    if data:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, headers=h, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rest():
    """Public profile, repos, stars, and language bytes."""
    h = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    user = get(f"https://api.github.com/users/{USER}", h)
    repos, page = [], 1
    while page <= 5:
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}", h)
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    own = [r for r in repos if not r.get("fork")]
    langs = Counter()
    for r in own[:60]:                      # language bytes, one call per repo
        try:
            for name, b in get(r["languages_url"], h).items():
                langs[name] += b
        except urllib.error.HTTPError:
            break
    return {
        "repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "stars": sum(r.get("stargazers_count", 0) for r in own),
        "forks": sum(r.get("forks_count", 0) for r in own),
        "joined": (user.get("created_at") or "")[:7],
        "languages": langs.most_common(8),
    }


GQL = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}"""


def graphql():
    """Contribution calendar + commit/PR/issue totals for the last year."""
    if not TOKEN:
        print("  no GITHUB_TOKEN — skipping calendar and commit totals")
        return {}
    d = get("https://api.github.com/graphql",
            {"Authorization": f"Bearer {TOKEN}"},
            {"query": GQL, "variables": {"login": USER}})
    if "errors" in d:
        print("  graphql:", d["errors"][0].get("message"))
        return {}
    c = d["data"]["user"]["contributionsCollection"]
    cal = c["contributionCalendar"]
    weeks = [[day["contributionCount"] for day in w["contributionDays"]]
             for w in cal["weeks"]]
    months = defaultdict(int)
    for w in cal["weeks"]:
        for day in w["contributionDays"]:
            months[day["date"][:7]] += day["contributionCount"]
    return {
        "commits": c["totalCommitContributions"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "contributions": cal["totalContributions"],
        "calendar": weeks,
        "monthly": [months[k] for k in sorted(months)][-12:],
        "month_labels": [k[5:] for k in sorted(months)][-12:],
    }


def wakapi():
    """Weekly coding hours and time-by-language."""
    base = "https://wakapi.dev/api/compat/wakatime/v1"
    h = {"Authorization": f"Basic {WAKAPI_KEY}"} if WAKAPI_KEY else {}
    out = {}
    try:
        s = get(f"{base}/users/{WAKAPI_USER}/stats/last_30_days", h)["data"]
        out["waka_langs"] = [(l["name"], round(l["total_seconds"] / 3600, 1))
                             for l in s.get("languages", [])[:8]]
        out["waka_daily_avg"] = round(s.get("daily_average", 0) / 3600, 1)
        out["waka_total"] = round(s.get("total_seconds", 0) / 3600, 1)
    except Exception as e:
        print("  wakapi stats unavailable:", e)
    try:
        sm = get(f"{base}/users/{WAKAPI_USER}/summaries?range=last_30_days", h)["data"]
        out["waka_days"] = [round(d["grand_total"]["total_seconds"] / 3600, 2) for d in sm]
    except Exception as e:
        print("  wakapi summaries unavailable:", e)
    return out


if __name__ == "__main__":
    data = {"generated": date.today().isoformat(), "user": USER}
    for name, fn in (("github", rest), ("contrib", graphql), ("wakapi", wakapi)):
        print(f"fetching {name}...")
        try:
            data.update(fn())
        except urllib.error.HTTPError as e:
            print(f"  {name} failed: HTTP {e.code} ({'rate limited' if e.code == 403 else e.reason})")
        except Exception as e:
            print(f"  {name} failed: {e}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT}")
    print("now run: python3 make_charts.py")
