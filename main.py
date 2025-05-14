from jira_fetcher import fetch_completed_epics

def main():
    epics = fetch_completed_epics()
    print("Fetched epics:", epics)

if __name__ == "__main__":
    main()
