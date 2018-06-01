from github import Github
from paramiko import SSHClient
from ShellHandler import ShellHandler
import time
import os
import yaml

# There isnt a way to get the last element unless you
# iterate through the linked list
def getLastElem(pList):
    toRet = None
    for i in pList:
        toRet = i
    return toRet

def testedCommit(sha, pr):
    tested = False
    for comment in pr.get_issue_comments():
        if(comment.body.find(sha) != -1):
            print("Nothing new to test")
            tested = True
            break
    return tested

def loadCommit(commit):
    os.system("rm -rf NachOS")
    os.system("ssh-agent bash -c \'ssh-add autoTester_id_rsa; git clone git@github.com:ajberchek/NachOS.git\'")
    os.system("cd NachOS;git checkout " + commit + ";scp -i " + cfg["nachosServer"]["sshKeyPath"] + " -r " + cfg["github"]["dirWithCode"] + " " + cfg["nachosServer"]["hostnameWithUser"] + ":" + cfg["nachosServer"]["dirToRun"])

def runTest(cfg):
    print("Testing code")
    ssh = ShellHandler(cfg["nachosServer"]["hostnameWithUser"].split('@')[1],cfg["nachosServer"]["hostnameWithUser"].split('@')[0])
    ssh.execute("bash")
    ssh.execute("cd " + cfg["nachosServer"]["dirToRun"])
    (cmdIn, cmdOut, cmdErr) = ssh.execute(cfg["nachosServer"]["testCommand"])
    ssh.execute("exit")
    return "".join(cmdOut)


cfg = yaml.load(open("config.yaml", 'r'))
git = Github(cfg["github"]["oauth"])
repo = git.get_user(cfg["github"]["repoOwner"]).get_repo(cfg["github"]["repoName"])
while True:
    for pr in repo.get_pulls():
        commit = getLastElem(pr.get_commits())
        if(not testedCommit(commit.sha,pr)):
            print("Testing " + pr.title + " on commit " + commit.sha)
            pr.create_issue_comment("Testing latest changes")
            loadCommit(commit.sha)
            results = runTest(cfg)
            pr.create_issue_comment("Test results for " + commit.sha + ":\n" + results)

    print("Going to sleep")
    time.sleep(15)
