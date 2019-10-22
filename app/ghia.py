import click
from enum import Enum
from typing import NamedTuple, List
from io import BufferedReader, TextIOWrapper
import configparser
import requests
import re

REPO = 'svatozde/ghia_test_env'

class Mode(Enum):
    APPEND='append'
    SET='set'
    CHANGE='change'
    DRY='dry'


class IssueField(Enum):
    TITLE = 'title'
    TEXT = 'text'
    LABEL = 'label'
    ANY = 'any'


class Rule(NamedTuple):
    field: IssueField
    pattern: str


class UserRules(NamedTuple):
    user: str
    rules: List[Rule]


class Issue(NamedTuple):
    url: str
    assignees: List[str]
    title: str
    labels: List[str]
    body: str


def parseRule(value: str) -> Rule:
    splitIndex = value.find(':')
    type = value[:splitIndex]
    pattern = value[splitIndex + 1:]
    return Rule(
        field=IssueField[type.upper()],
        pattern=pattern
        )


def parsePatterns(value: str) -> List[Rule]:
    return [parseRule(line) for line in value.splitlines() if line]


def loadRules(fileReader: BufferedReader) -> List[UserRules]:
    config = configparser.ConfigParser()
    config.read_file(TextIOWrapper(fileReader))
    patterns = config['patterns']
    return [
        UserRules(
            user=user,
            rules=parsePatterns(patterns[user])
            ) for user in patterns
        ]


def loadToken(fileReader: BufferedReader) -> str:
    config = configparser.ConfigParser()
    config.read_file(TextIOWrapper(fileReader))
    return config['github']['token']


def matchBody(issue:Issue, rule:Rule) -> bool:
    return regexFind(rule.pattern,issue.body)

def matchTitle(issue:Issue, rule:Rule) -> bool:
    return regexFind(rule.pattern,issue.title)

def mathcLabel(issue:Issue, rule:Rule) -> bool:
    for l in issue.labels:
        if(regexFind(rule.pattern,l)): return True
    return False


def any(issue:Issue, rule:str) -> bool:
    return matchTitle(issue, rule) \
           or mathcLabel(issue, rule) \
           or matchBody(issue, rule)



def shouldApply(userRules:UserRules,issue:Issue) -> bool:
    for rule in userRules.rules:
        rule_type = rule.field
        if rule_type == IssueField.TITLE:
            if(matchTitle(issue, rule)):
                return True
        elif rule_type == IssueField.TEXT:
            if (matchBody(issue, rule)):
                return True
        elif rule_type == IssueField.LABEL:
            if (mathcLabel(issue, rule)):
                return True
        elif rule_type == IssueField.ANY:
            if (any(issue, rule)):
                return True


# Note no need to precopile and store patterns python caches them
# see: https://stackoverflow.com/questions/452104/is-it-worth-using-pythons
# -re-compile
def regexFind(pattern:str,value:str) -> bool:
    re.search(pattern, value)







class GitHub(object):
    def __init__(self, **config_options):
        self.__dict__.update(**config_options)
        self.session = requests.Session()
        if hasattr(self, 'api_token'):
            self.session.headers['Authorization'] = 'token %s' % self.api_token
        elif hasattr(self, 'username') and hasattr(self, 'password'):
            self.session.auth = (self.username, self.password)

        if not hasattr(self, 'repo'):
            raise Exception('missing repo name')

        self.base_url = 'https://api.github.com/repos/%s' % self.repo
        self.issues_url = self.base_url + '/issues'

    def post(self, url):
        # do stuff with args
        return None

    def issues(self) -> List[Issue]:
        # do stuff with args
        r = self.session.get(self.issues_url)
        if not r.status_code == 200:
            raise Exception(r.status_code)
        return [
            Issue(
                url=issue['url'],
                assignees=issue['assignees'],
                title=issue['title'],
                labels=[l['name'] for l in issue['labels']],
                body=issue['body']
            ) for issue in r.json()
        ]

    def update(self, issue:Issue):
        pass



def assign(mode:Mode, git:GitHub, user:str,issue:Issue):
    if mode == Mode.APPEND:
        git.update(issue)
    elif mode == Mode.SET:
        git.update(issue)
    elif mode == Mode.CHANGE:
        git.update(issue)


@click.command()
@click.option('-s',
              '--strategy',
              type=click.Choice(['append', 'set', 'change']),
              default='append',
              show_default=True,
              help='How to handle assignment collisions.'
              )
@click.option('-d',
              '--dry-run',
              default=False,
              is_flag=True,
              help='Run without making any changes.'
              )
@click.option('-a',
              '--config-auth',
              type=click.File('rb'),
              required=True,
              help='File with authorization configuration.'
              )
@click.option('-r',
              '--config-rules',
              type=click.File('rb'),
              required=True,
              help='File with assignment rules configuration.'
              )
def run(strategy, dry_run, config_auth, config_rules):
    print(strategy)
    print(dry_run)
    print(config_auth)
    print(config_rules)

    rules = loadRules(config_rules)
    token = loadToken(config_auth)

    git = GitHub(api_token=token, repo=REPO)
    issues = git.issues()

    for i in issues:
        for r in rules:
            if(shouldApply(r,i)):
                assign(Mode[strategy.upper()],git, r.user, i)

    return


if __name__ == '__main__':
    run()
