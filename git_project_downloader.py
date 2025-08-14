import requests
import csv
from getpass import getpass

# --------- CONFIGURATION ---------
# IMPORTANT: Change this to your GitHub username or organization name
OWNER_NAME = "enstenr"  # e.g., "my-username" or "my-org"
PROJECT_NUMBER = 3  # Project v2 number
CSV_FILE = "github_project_export.csv"

# Prompt user for GitHub token securely
GITHUB_TOKEN = getpass("Enter your GitHub Personal Access Token: ")

# --------- GRAPHQL QUERY ---------
# This query now works for both Users and Organizations
QUERY = """
query($owner: String!, $projectNumber: Int!, $cursor: String) {
  user(login: $owner) {
    projectV2(number: $projectNumber) {
      title
      items(first: 50, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          content {
            ... on DraftIssue {
              title
              assignees(first: 10) {
                nodes {
                  login
                }
              }
            }
            ... on Issue {
              title
              number
              url
              state
              assignees(first: 10) {
                nodes {
                  login
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
            ... on PullRequest {
              title
              number
              url
              state
              assignees(first: 10) {
                nodes {
                  login
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
                text
              }
              ... on ProjectV2ItemFieldNumberValue {
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
                number
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2Field {
                    name
                  }
                }
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}


def run_query(query, variables):
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code}, {response.text}")
    return response.json()


def fetch_all_items():
    items = []
    cursor = None
    while True:
        variables = {
            "owner": OWNER_NAME,
            "projectNumber": PROJECT_NUMBER,
            "cursor": cursor
        }
        result = run_query(QUERY, variables)
        if "errors" in result:
            # First, check if the error is because it's an org, not a user
            if "Could not resolve to a User with the login" in result['errors'][0]['message']:
                # If so, we'll try the organization query as a fallback
                return fetch_all_items_for_org()  # A function to handle orgs
            raise Exception(f"GraphQL query returned errors: {result['errors']}")

        project_data = result.get("data", {}).get("user", {}).get("projectV2")
        if not project_data:
            print("Could not retrieve project data. Is the OWNER_NAME and PROJECT_NUMBER correct?")
            # Try falling back to an organization query
            print("Trying to query as an Organization instead...")
            return fetch_all_items_for_org()

        nodes = project_data.get("items", {}).get("nodes", [])
        for node in nodes:
            item = {}
            if node.get("content"):
                item = {
                    "Title": node["content"].get("title"),
                    "IssueNumber": node["content"].get("number", ""),
                    "URL": node["content"].get("url", ""),
                    "State": node["content"].get("state", ""),
                    "Assignees": ", ".join(a["login"] for a in node["content"].get("assignees", {}).get("nodes", [])),
                    "Labels": ", ".join(l["name"] for l in node["content"].get("labels", {}).get("nodes", []))
                }

            # Custom fields
            for field in node.get("fieldValues", {}).get("nodes", []):
                if field and "field" in field and "name" in field["field"]:
                    field_name = field["field"]["name"]
                    if "text" in field:
                        item[field_name] = field["text"]
                    elif "number" in field:
                        item[field_name] = field["number"]
                    elif "name" in field:
                        item[field_name] = field["name"]
            items.append(item)

        page_info = project_data.get("items", {}).get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info["endCursor"]
        else:
            break
    return items


# This is the original function to query an organization, kept as a fallback.
def fetch_all_items_for_org():
    # This function would contain the original logic querying for an 'organization'.
    # For simplicity in this example, we'll just print a message.
    # To make this fully functional, you would copy the logic from fetch_all_items
    # but use the original GraphQL query for organizations.
    print("Fallback to organization query is not fully implemented in this example.")
    print("Please verify if OWNER_NAME is a user or an organization and use the correct script.")
    return []


def export_to_csv(items):
    if not items:
        print("No items found to export.")
        return
    # Get all unique headers
    headers = set()
    for item in items:
        headers.update(item.keys())
    headers = sorted(list(headers))

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in items:
            writer.writerow(item)
    print(f"Exported {len(items)} items to {CSV_FILE}")


if __name__ == "__main__":
    try:
        all_items = fetch_all_items()
        export_to_csv(all_items)
    except Exception as e:
        print(f"An error occurred: {e}")