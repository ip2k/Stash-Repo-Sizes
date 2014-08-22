import requests
from bs4 import BeautifulSoup
from pprint import pprint

# Set-up
sesh = requests.Session()
auth = ('YOUR-STASH-ADMIN-USERNAME', 'YOUR-PASSWORD')
base = 'http://stash.yourdomain.com'  # FQDN of Stash install. No trailing slash.

# Functions
def get_projects(auth=auth, requests_session=sesh):
    vals = []
    resp = requests_session.get('{}/rest/api/1.0/projects?limit=1000'.format(base), auth=auth)
    if resp.status_code != 200:
        print "ERR: 1"
        return False
    json = resp.json()

    for item in json.get('values'):
        vals.append(item)

    if vals:
        return vals
    print "ERR: 3"
    return None


def get_repos(project_key=None, auth=auth, requests_session=sesh):
    start_at = 0
    vals = []
    resp = requests_session.get('{}/rest/api/1.0/projects/{}/repos?limit=1000'.format(base, project_key), auth=auth)
    if resp.status_code != 200:
        print "ERR: 2"
        return False
    json = resp.json()

    for item in json['values']:
        vals.append(item)

    if vals:
        return vals
    print "ERR: get_repos had no vals to return"
    return None


def get_repo_size(project_key=None, repo=None, requests_session=sesh, auth=auth):
    if not all([the_project, repo, requests_session, auth]):
        return None

    resp = requests_session.get('{}/projects/{}/repos/{}/settings'.format(base, project_key, repo), auth=auth)
    print 'Processing {}/projects/{}/repos/{}'.format(base, project_key, repo)
    soup = BeautifulSoup(resp.content)
    results = soup.find_all('span', class_='field-value', id='size')
    if results:
        return results[0].text
    print "ERR: 5"
    return None


# Main
prjs = get_projects(auth=auth, requests_session=sesh)


out = {}
for the_project in prjs:
    project_key = the_project.get('key')
    if not project_key: next
    repos = get_repos(project_key=project_key)
    if repos:
        for the_repo in repos:
            repo_name = the_repo.get('name')
            repo_size = get_repo_size(project_key=project_key, repo=repo_name)
            if not out.get(project_key):
                out[project_key] = {}
            out[project_key][repo_name] = repo_size



pprint(out)

"""
Example of 'out' :

{ u'FOO': {u'myrepo': u'1.11 MB'},
 u'BAR': {u'some-repo': u'1.26 MB', u'different-repo': u'1.46 MB'},
 u'BAZ': {u'another-repo': u'80.45 kB'},
 u'QUUX': {u'repo1': u'139.87 kB',
         u'repo2': None,
         u'repo3': u'160.84 kB',
         u'repo4': u'116.49 kB',
         u'repo5': u'13.07 MB'} }
"""
