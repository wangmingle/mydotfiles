#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
import re

sentinel = object()

parser = argparse.ArgumentParser(description="Get the git remote")
parser.add_argument('remote_name', type=str, default='origin', nargs='?',
                    help="Name of the remote to open (defaults to origin)")
parser.add_argument('-b', '--branch', nargs='?', const=sentinel,
                    help=('open the current branch in the browser'))
parser.add_argument('-e', '--tree', default=None,
                    help=('Open the tree at the specified folder/file'))
parser.add_argument('-r', '--compare', action='store_true', 
                    help=('Open the compare view'))
parser.add_argument('-s', '--pulls', action='store_true', 
                    help=('Open the pull requests list'))
parser.add_argument('-i', '--issues', action='store_true', 
                    help=('Open the issues page'))
parser.add_argument('-t', '--tip', action='store_true', 
                    help=('Open the latest commit (works with --branch as well)'))
parser.add_argument('-c', '--commits', action='store_true', 
                    help=('Open the commits list'))
parser.add_argument('-p', '--pull', nargs='?', default=None, const='origin',
                    help=('Open a pull request for the current branch. '
                          'Defaults to a pull request against the '
                          'remote_name remote.'))
args = parser.parse_args()

def _get_remote_url(remote_name):
    """ Retrieve the remote URL from a remote name like 'upstream' """
    cmd = "git config --get remote.{}.url".format(remote_name)
    try:
        remote_url = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        sys.stderr.write("Couldn't find a remote named {}\n".format(
            remote_name))
        sys.exit(1)
    return remote_url


def _parse_git_remote_url(url):
    """Parse Git remote URL's into a SRE_Match object
    
    Matches user@<hostname>:<web_user>/<user_repo>
    or      git://<hostname>/<web_user>/<user_repo>
    """
    ssh_regex = re.compile(r"""
                           ^(
                                (?P<git_user>\S+)@   # match user@ ssh url's
                                |
                                git://               # match git read-only url's
                                |
                                https://
                           )
                           (?P<host>[^/:]+) # hostname
                           [:/]             # separator
                           (?P<user>[^/]+)
                           /
                           (?P<repo_name>.+?)
                           (\.git)?$
                           """, re.X)
    try:
        return ssh_regex.match(str(url, 'utf-8'))
    except Exception: # Python 2
        return ssh_regex.match(str(url))


def _get_branch():
    cmd = "git rev-parse --symbolic-full-name --abbrev-ref HEAD"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

remote_url = _get_remote_url(args.remote_name)
match = _parse_git_remote_url(remote_url)

if match is None:
    raise ValueError("Couldn't parse {url} as a git remote".format(url=remote_url))
url = "".join(["https://", match.group('host'), '/', match.group('user'), '/',
               match.group('repo_name')])

if args.branch and args.branch is sentinel:
    branch = _get_branch()
else:
    branch = args.branch

def _open_url(url):
    # Would like to use webbrowser but sometimes it just fails.
    os.system("open '{url}'".format(url=url.strip()))
    sys.exit(0)

if args.pulls and args.pull:
    raise ValueError("Cannot specify both --pulls and --pull flags")

if args.pulls:
    _open_url(url + "/pulls")
elif args.tree is not None:
    branch = _get_branch()
    _open_url("{url}/tree/{branch}/{tree}".format(url=url, branch=branch, tree=args.tree))
elif args.compare:
    _open_url(url + "/compare")
elif args.branch and not args.tip:
    _open_url("{}/tree/{}".format(url, branch))
elif args.issues:
    _open_url(url + "/issues")
elif args.commits:
    _open_url(url + "/commits")
elif args.tip:
    commit = subprocess.check_output(
        "git rev-parse {}".format(branch or "HEAD"), shell=True).strip()
    _open_url(url + "/commit/{}".format(commit))

if args.pull:
    branch = _get_branch()
    if args.pull != 'origin':
        upstream_url = _get_remote_url(args.pull).decode('utf-8')
        upstream_match = _parse_git_remote_url(upstream_url)
        upstream_remote_branch = '{}:master'.format(upstream_match.group('user'))
    else:
        upstream_remote_branch = 'master'
    if 'github.com' in url:
        _open_url(url + "/compare/{branch}?expand=1".format(branch=branch))
    else:
        _open_url(url + "/pull/new/{}...{}".format(upstream_remote_branch, branch))

_open_url(url)